import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
import PyPDF2

from app.models import db, User, Document, Activity
from app.ml_classifier import DocumentClassifier

main_bp = Blueprint('main', __name__)
classifier = DocumentClassifier()

def log_activity(user_id, activity_text):
    """Utility to log patient activity."""
    activity = Activity(user_id=user_id, activity=activity_text, timestamp=datetime.now())
    db.session.add(activity)
    db.session.commit()

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Calculate stats for landing page counter animations
    try:
        total_reports = Document.query.count()
        total_users = User.query.count()
    except Exception:
        total_reports = 0
        total_users = 0
        
    return render_template('index.html', total_reports=total_reports, total_users=total_users)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'danger')
            return render_template('register.html')
            
        hashed_password = generate_password_hash(password, method='scikit-learn' if hasattr(generate_password_hash, 'scikit-learn') else 'pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        log_activity(new_user.id, "Registered new account")
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html')
            
        login_user(user, remember=remember)
        log_activity(user.id, "Logged in successfully")
        return redirect(url_for('main.dashboard'))
        
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    logout_user()
    # Log activity before logout session is cleared completely
    log_activity(user_id, "Logged out of the system")
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    docs = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_date.desc()).all()
    
    # Calculate stats
    total_docs = len(docs)
    category_counts = {
        'Prescription': 0,
        'Lab Report': 0,
        'Scan Report': 0,
        'Discharge Summary': 0
    }
    for doc in docs:
        if doc.category in category_counts:
            category_counts[doc.category] += 1
            
    # Fetch recent activities for timeline
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).limit(5).all()
            
    return render_template('dashboard.html', 
                           documents=docs, 
                           total_docs=total_docs,
                           category_counts=category_counts,
                           activities=activities)

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.accept_mimetypes.best == 'application/json' or
        'application/json' in request.headers.get('Accept', '')
    )

    def respond(message, status='error', redirect_to=None, status_code=200):
        if is_ajax:
            payload = {'status': status, 'message': message}
            if redirect_to:
                payload['redirect'] = redirect_to
            return jsonify(payload), status_code

        if status == 'error':
            flash(message, 'danger')
        else:
            flash(message, 'success')

        return redirect(redirect_to or url_for('main.dashboard'))

    if 'file' not in request.files:
        return respond('No file part in the request.', status_code=400)
        
    file = request.files['file']
    if file.filename == '':
        return respond('No file selected.', status_code=400)

    if not file.filename.lower().endswith('.pdf'):
        return respond('Only PDF documents are allowed.', status_code=400)

    file.stream.seek(0, os.SEEK_END)
    file_size = file.stream.tell()
    file.stream.seek(0)
    if file_size > current_app.config['MAX_UPLOAD_SIZE']:
        return respond('PDF files must be 25 MB or smaller.', status_code=400)
        
    original_filename = secure_filename(file.filename) or f"document_{uuid.uuid4().hex[:8]}.pdf"
    # Generate unique filename to store on disk
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    qr_file_path = None
    
    try:
        # Save file to uploads folder
        file.save(file_path)

        # Validate PDF integrity before classification
        try:
            reader = PyPDF2.PdfReader(file_path)
            if reader.is_encrypted:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return respond('The PDF file is encrypted and cannot be processed.', status_code=400)
            # Ensure PDF structure has readable pages
            _ = len(reader.pages)
        except Exception as pdf_err:
            if os.path.exists(file_path):
                os.remove(file_path)
            current_app.logger.warning("Corrupted or invalid PDF uploaded: %s (%s)", original_filename, pdf_err)
            return respond('The uploaded file is corrupted or is not a valid PDF.', status_code=400)
        
        # Run ML Classification
        extracted_text = classifier.extract_text_from_pdf(file_path)
        category = classifier.classify_text(extracted_text)
        
        # Create database entry first to get the unique document ID via flush (not committed yet)
        new_doc = Document(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=original_filename,
            category=category,
            qr_path=''  # To be assigned below
        )
        db.session.add(new_doc)
        db.session.flush()
        
        # Generate QR Code pointing directly to the file via public share route
        details_url = url_for('main.share', doc_id=new_doc.id, _external=True)
        
        # Override 127.0.0.1/localhost with local Wi-Fi IP so mobile devices can access it
        import socket
        def get_local_ip():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('10.254.254.254', 1))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()
            return ip
            
        local_ip = get_local_ip()
        details_url = details_url.replace('127.0.0.1', local_ip).replace('localhost', local_ip)
        
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(details_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_filename = f"qr_{new_doc.id}.png"
        qr_file_path = os.path.join(current_app.config['QRCODES_FOLDER'], qr_filename)
        qr_img.save(qr_file_path)
        
        # Update QR path in DB
        new_doc.qr_path = f"qrcodes/{qr_filename}"
        
        # Log activity within the same transaction
        activity = Activity(
            user_id=current_user.id,
            activity=f"Uploaded document: {original_filename} (Classified as: {category})",
            timestamp=datetime.now()
        )
        db.session.add(activity)

        # Atomically commit document, QR path, and activity together
        db.session.commit()

        success_message = f'Document "{original_filename}" uploaded and classified as {category}!'

        if is_ajax:
            return jsonify({'status': 'success', 'message': success_message, 'redirect': url_for('main.dashboard')})

        flash(success_message, 'success')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error("Upload failure for file %s: %s", original_filename, error_details)
        try:
            with open(os.path.join(current_app.config['UPLOAD_FOLDER'], 'last_error.txt'), 'w', encoding='utf-8') as f:
                f.write(error_details)
        except Exception as log_err:
            current_app.logger.warning("Could not write last_error.txt: %s", log_err)

        db.session.rollback()
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        if qr_file_path and os.path.exists(qr_file_path):
            try:
                os.remove(qr_file_path)
            except OSError:
                pass

        return respond('An error occurred during upload or classification. Please try again.', status='error', status_code=500)

@main_bp.route('/document/<int:doc_id>')
@login_required
def document_detail(doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Ownership authorization check
    if doc.user_id != current_user.id:
        flash('Unauthorized access to this document.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    # Log view activity
    log_activity(current_user.id, f"Viewed document: {doc.original_filename}")
        
    # Read snippet of the document text for display
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    extracted_snippet = ""
    if os.path.exists(file_path):
        extracted_snippet = classifier.extract_text_from_pdf(file_path)
        # Limit snippet size to avoid huge page loads
        if len(extracted_snippet) > 800:
            extracted_snippet = extracted_snippet[:800] + "..."
    else:
        extracted_snippet = "[Physical document file not found on server disk]"
        
    return render_template('document_detail.html', document=doc, text_snippet=extracted_snippet)

@main_bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Security check
    if doc.user_id != current_user.id:
        flash('Unauthorized access to this document.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    # Log download activity
    log_activity(current_user.id, f"Downloaded document: {doc.original_filename}")
        
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'], 
        doc.filename,
        as_attachment=True,
        download_name=doc.original_filename
    )

@main_bp.route('/share/<int:doc_id>')
def share(doc_id):
    """Public route to view the file via QR Code without login."""
    doc = Document.query.get_or_404(doc_id)
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'], 
        doc.filename,
        as_attachment=False,
        download_name=doc.original_filename
    )

@main_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Security check
    if doc.user_id != current_user.id:
        flash('Unauthorized access to this document.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    original_filename = doc.original_filename
    
    # File cleanup from disk
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing PDF file: {e}")
            
    # QR code cleanup from disk
    if doc.qr_path:
        qr_filename = os.path.basename(doc.qr_path)
        qr_path = os.path.join(current_app.config['QRCODES_FOLDER'], qr_filename)
        if os.path.exists(qr_path):
            try:
                os.remove(qr_path)
            except Exception as e:
                print(f"Error removing QR code image: {e}")
                
    # Database removal
    try:
        db.session.delete(doc)
        db.session.commit()
        log_activity(current_user.id, f"Deleted document: {original_filename}")
        flash(f'Document "{original_filename}" has been successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting document from database: {e}', 'danger')
        
    return redirect(url_for('main.dashboard'))

@main_bp.route('/history')
@login_required
def history():
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).all()
    return render_template('history.html', activities=activities)
