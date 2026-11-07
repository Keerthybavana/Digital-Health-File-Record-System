import os
import sys
import io
import shutil
import tempfile
import unittest
from unittest.mock import patch
from flask.config import Config
from sqlalchemy.pool import StaticPool

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PyPDF2

class TestPDFUploadSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Create dedicated temporary directories for uploads and QR codes
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_upload_dir = os.path.join(cls.temp_dir, 'uploads')
        cls.temp_qr_dir = os.path.join(cls.temp_dir, 'qrcodes')
        os.makedirs(cls.temp_upload_dir, exist_ok=True)
        os.makedirs(cls.temp_qr_dir, exist_ok=True)

        # 2. Intercept config assignment to guarantee in-memory DB and isolated directories
        orig_setitem = Config.__setitem__
        def mock_setitem(self, key, value):
            if key == 'SQLALCHEMY_DATABASE_URI':
                value = 'sqlite:///:memory:'
            elif key == 'UPLOAD_FOLDER':
                value = cls.temp_upload_dir
            elif key == 'QRCODES_FOLDER':
                value = cls.temp_qr_dir
            return orig_setitem(self, key, value)

        with patch.object(Config, '__setitem__', mock_setitem):
            from app import create_app
            from app.models import db, User, Document, Activity
            cls.db = db
            cls.User = User
            cls.Document = Document
            cls.Activity = Activity
            cls.app = create_app()

        cls.app.config['TESTING'] = True
        cls.app.config['LOGIN_DISABLED'] = False
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': StaticPool,
            'connect_args': {'check_same_thread': False}
        }
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # 3. Create tables in the isolated in-memory DB
        cls.db.create_all()

        # 4. Create an isolated synthetic test user
        cls.test_user = cls.User(name="Test User", email="test_isolated@example.com", password="dummy_hash")
        cls.db.session.add(cls.test_user)
        cls.db.session.commit()
        cls.test_user_id = cls.test_user.id

    @classmethod
    def tearDownClass(cls):
        # 1. Pop application context
        try:
            cls.app_context.pop()
        except Exception:
            pass

        # 2. Recursively delete the temporary directory
        if os.path.exists(cls.temp_dir):
            try:
                shutil.rmtree(cls.temp_dir)
            except Exception as e:
                print("Temp dir cleanup error:", e)

    def setUp(self):
        # Clear any cached login state on flask.g
        from flask import g
        if hasattr(g, '_login_user'):
            delattr(g, '_login_user')

        # Fresh test client for each test
        self.client = self.app.test_client()
        self.client._cookies.clear()
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user_id)
            sess['_fresh'] = True

    def tearDown(self):
        # Clear any cached login state on flask.g after test
        from flask import g
        if hasattr(g, '_login_user'):
            delattr(g, '_login_user')

    def _create_synthetic_pdf(self, pages=1):
        writer = PyPDF2.PdfWriter()
        for _ in range(pages):
            writer.add_blank_page(width=72, height=72)
        buf = io.BytesIO()
        writer.write(buf)
        buf.seek(0)
        return buf

    def test_01_valid_small_synthetic_pdf_ajax_upload(self):
        """Scenario 1: Small valid synthetic PDF uploads via AJAX and returns 200 JSON."""
        pdf_bytes = self._create_synthetic_pdf(pages=1)
        data = {'file': (pdf_bytes, 'synthetic_small.pdf')}
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}

        response = self.client.post('/upload', data=data, content_type='multipart/form-data', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.headers.get('Content-Type', ''))

        json_data = response.get_json()
        self.assertEqual(json_data.get('status'), 'success')
        self.assertIn('synthetic_small.pdf', json_data.get('message', ''))
        self.assertEqual(json_data.get('redirect'), '/dashboard')

        # Verify DB and QR code inside isolated environment
        doc = self.Document.query.filter_by(original_filename='synthetic_small.pdf').order_by(self.Document.id.desc()).first()
        self.assertIsNotNone(doc)
        self.assertTrue(os.path.exists(os.path.join(self.app.config['UPLOAD_FOLDER'], doc.filename)))
        self.assertTrue(os.path.exists(os.path.join(self.app.config['QRCODES_FOLDER'], f"qr_{doc.id}.png")))

    def test_02_valid_multipage_pdf_upload(self):
        """Scenario 2: Multi-page valid synthetic PDF uploads successfully with classification."""
        pdf_bytes = self._create_synthetic_pdf(pages=5)
        data = {'file': (pdf_bytes, 'synthetic_multipage.pdf')}
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}

        response = self.client.post('/upload', data=data, content_type='multipart/form-data', headers=headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data.get('status'), 'success')

        doc = self.Document.query.filter_by(original_filename='synthetic_multipage.pdf').order_by(self.Document.id.desc()).first()
        self.assertIsNotNone(doc)

    def test_03_corrupted_pdf_returns_clear_error(self):
        """Scenario 3: Corrupted binary receives a 400 JSON error and creates no orphan records."""
        corrupt_bytes = io.BytesIO(b'%PDF-1.4 header without any valid xref, trailer, or EOF.')
        data = {'file': (corrupt_bytes, 'corrupted_test.pdf')}
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}

        docs_before = self.Document.query.count()
        response = self.client.post('/upload', data=data, content_type='multipart/form-data', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('application/json', response.headers.get('Content-Type', ''))

        json_data = response.get_json()
        self.assertEqual(json_data.get('status'), 'error')
        self.assertIn('corrupted or is not a valid PDF', json_data.get('message', ''))

        docs_after = self.Document.query.count()
        self.assertEqual(docs_before, docs_after)

    def test_04_empty_filename_or_non_pdf_rejected(self):
        """Scenario 4: Non-PDF files and empty file submissions are rejected with 400 JSON error."""
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}

        # 4a. Non-PDF rejected
        data_txt = {'file': (io.BytesIO(b'plain text'), 'test.txt')}
        res = self.client.post('/upload', data=data_txt, content_type='multipart/form-data', headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Only PDF documents are allowed', res.get_json().get('message', ''))

        # 4b. Empty filename rejected
        data_empty = {'file': (io.BytesIO(b''), '')}
        res2 = self.client.post('/upload', data=data_empty, content_type='multipart/form-data', headers=headers)
        self.assertEqual(res2.status_code, 400)
        self.assertIn('No file selected', res2.get_json().get('message', ''))

    def test_05_oversized_file_rejected(self):
        """Scenario 5: File exceeding MAX_UPLOAD_SIZE receives a clear 400 error."""
        oversized = io.BytesIO(b'%PDF-1.4' + b'0' * (25 * 1024 * 1024 + 10))
        data = {'file': (oversized, 'oversized.pdf')}
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}

        res = self.client.post('/upload', data=data, content_type='multipart/form-data', headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn('25 MB or smaller', res.get_json().get('message', ''))

    def test_06_unauthenticated_request_returns_401_json(self):
        """Scenario 6: Unauthenticated AJAX upload returns 401 JSON redirecting to login."""
        unauth_client = self.app.test_client(use_cookies=False)
        pdf_bytes = self._create_synthetic_pdf(pages=1)
        data = {'file': (pdf_bytes, 'unauth.pdf')}
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}

        res = unauth_client.post('/upload', data=data, content_type='multipart/form-data', headers=headers)
        self.assertEqual(res.status_code, 401)
        self.assertIn('application/json', res.headers.get('Content-Type', ''))
        json_data = res.get_json()
        self.assertEqual(json_data.get('status'), 'error')
        self.assertIn('/login', json_data.get('redirect', ''))

    def test_07_non_ajax_form_submission(self):
        """Scenario 7: Standard non-AJAX form submissions return 302 redirect to dashboard."""
        pdf_bytes = self._create_synthetic_pdf(pages=1)
        data = {'file': (pdf_bytes, 'synthetic_standard_form.pdf')}

        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

        doc = self.Document.query.filter_by(original_filename='synthetic_standard_form.pdf').order_by(self.Document.id.desc()).first()
        self.assertIsNotNone(doc)

if __name__ == '__main__':
    unittest.main()
