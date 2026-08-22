# Cloud-Based Digital Health File System with ML-Assisted Document Classification

A clean, modular, and beginner-friendly web application designed as a final-year engineering project and campus placement demo. This system allows patients to securely upload medical reports (PDFs), automatically extracts their text content, classifies them into four categories using machine learning, and generates unique QR codes pointing to document details.

---

## 🌟 Key Features

1. **Patient Authentication**: Secure user signup, login, and logout processes powered by `Flask-Login` and hashed passwords via `Werkzeug`.
2. **Interactive Dashboard**: Healthcare metrics dashboard showcasing overall document stats and lists of all uploaded records.
3. **Automated ML Classification**: Uses standard `scikit-learn` algorithms (TF-IDF vectorizer + Logistic Regression) to automatically categorize PDFs into:
   - 📄 **Prescription**
   - 🔬 **Lab Report**
   - 🩺 **Scan Report**
   - 🏥 **Discharge Summary**
4. **QR Code Sharing**: Generates unique QR codes dynamically for each uploaded document. Scanning the QR code takes authorized users directly to the document details page.
5. **Activity Audit History**: Logs patient activities (registration, logins, uploads, classifications, and deletions) for transparency and auditing.
6. **Secure Document Management**: Implements user authorization boundaries (users can only access, download, or delete their own documents) and renames file uploads using UUID hashes to prevent overrides.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5 (crisp corporate-medical UI, no complex dependencies), Vanilla JavaScript (drag-and-drop file inputs and alerts).
- **Backend Framework**: Python Flask.
- **Database Engine**: SQLite (SQLAlchemy ORM).
- **Machine Learning Library**: Scikit-Learn (TF-IDF Vectorizer + Logistic Regression).
- **Helper Utilities**: PyPDF2 (PDF text extraction), qrcode (QR code image rendering), Pandas (data loading).

---

## 📂 Project Structure

```
digital-health-file-system/
├── app.py                      # Main entrypoint to run the Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # Setup, execution, and project details
├── architecture.md             # System architecture diagram (Mermaid)
├── flow.md                     # Application logic flow diagram (Mermaid)
├── uploads/                    # Top-level directory for uploaded patient PDFs (Created automatically)
├── models_ml/                  # Top-level directory for serialized ML binaries (Created automatically)
├── app/
│   ├── __init__.py             # Flask application factory, DB, and Login configuration
│   ├── models.py               # SQLAlchemy models (Users, Documents, Activities)
│   ├── routes.py               # Flask routes (auth, dashboard, upload, detail, history)
│   ├── ml_classifier.py        # Text extraction (PyPDF2) and classification logic
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Clean healthcare styling overrides
│   │   ├── js/
│   │   │   └── main.js         # Interactive JS (drag-and-drop file select helper)
│   │   └── qrcodes/            # Directory for generated QR code images (Created automatically)
│   └── templates/
│       ├── base.html           # Main template containing layout, navbar, and imports
│       ├── login.html          # Clean Bootstrap 5 login card
│       ├── register.html       # Clean Bootstrap 5 registration card
│       ├── dashboard.html      # Healthcare dashboard (upload box, stats, files list)
│       ├── document_detail.html# Detail page showing metadata, QR code, and download/delete
│       └── history.html        # Clean activities table
├── data/
│   └── sample_dataset.csv      # CSV dataset containing labeled clinical text samples
└── scripts/
    └── train_classifier.py     # Script to train Scikit-learn model and save PKL objects to models_ml/
```

---

## 🗄️ Database Schema (SQLite)

The database schema is mapped using **Flask-SQLAlchemy**:

### 1. `users` Table
- `id` (INT, Primary Key): Unique patient ID.
- `name` (VARCHAR): Patient's full name.
- `email` (VARCHAR, Unique): Patient's email (login credential).
- `password` (VARCHAR): Hashed password string.

### 2. `documents` Table
- `id` (INT, Primary Key): Unique document ID.
- `user_id` (INT, Foreign Key): Links to `users.id` (Cascades on delete).
- `filename` (VARCHAR): Hashed file name saved on server disk (e.g. `uuid_filename.pdf`).
- `original_filename` (VARCHAR): Actual filename uploaded by the patient.
- `category` (VARCHAR): Predicted label (Prescription, Lab Report, Scan Report, Discharge Summary).
- `upload_date` (DATETIME): Timestamp of upload.
- `qr_path` (VARCHAR): Path to the generated QR code PNG file on server.

### 3. `activities` Table
- `id` (INT, Primary Key): Unique log ID.
- `user_id` (INT, Foreign Key): Links to `users.id` (Cascades on delete).
- `activity` (VARCHAR): Detailed log string (e.g. "Uploaded prescription.pdf").
- `timestamp` (DATETIME): Timestamp of event.

---

## ⚙️ Step-by-Step Setup & Execution

### 1. Clone or Copy the Files
Make sure the files are saved inside your project directory (e.g. `E:\Digital Health Record`).

### 2. Install Required Python Packages
Open command prompt or terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Train the Machine Learning Classifier
You must train the TF-IDF and Logistic Regression model before running the application to classify reports. Execute the training script:
```bash
python scripts/train_classifier.py
```
*Note: If you skip this step, the Flask application will automatically run the training script on its first launch if it notices the model files are missing, ensuring it works out-of-the-box.*

### 4. Run the Flask Web Application
Launch the Flask development server:
```bash
python app.py
```

### 5. Access the Web Portal
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```
- Click **Sign Up** to create an account.
- Log in and start uploading medical reports (PDFs) to test the ML classification!

---

## 🧠 Machine Learning Explanation (For Placement Interviews)

If a recruiter or professor asks about the Machine Learning pipeline, explain it using these four steps:

### 1. Text Extraction
We use `PyPDF2` in Python. It parses the PDF structure and extracts the characters as text strings. This is a rule-based pre-processing step that turns unstructured PDFs into raw documents.

### 2. TF-IDF Vectorization (Term Frequency - Inverse Document Frequency)
ML algorithms cannot understand raw text strings; they require numerical feature vectors. 
- **Term Frequency (TF)**: Calculates how frequently a word appears in a document. (e.g. "mg" appearing multiple times in a Prescription).
- **Inverse Document Frequency (IDF)**: Dampens terms that are extremely common across *all* document categories (like "patient", "hospital", "the", "and") and scales up rare, highly descriptive words (like "hemoglobin" for Lab Reports, or "x-ray" for Scan Reports).
- **Mathematical Formula**:
  $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{N}{|\{d \in D : t \in d\}|}\right)$$

### 3. Logistic Regression Classifier
We train a multi-class Logistic Regression classifier.
- **Why Logistic Regression?** It is highly explainable, lightweight, runs instantly in-memory, and requires very little computational overhead compared to deep neural networks.
- It calculates the probability of a document belonging to each of the 4 classes based on the TF-IDF feature weights, and outputs the class with the highest probability.
- Since our dataset is clear and distinct (medical keywords vary heavily between prescriptions, scans, labs, and discharges), a linear classifier is highly accurate and simple to present.

---

## 💬 Frequently Asked Placement Questions (FAQ)

### Q1: Why did you use SQLite instead of MySQL or PostgreSQL?
> **Answer**: SQLite is a serverless, zero-configuration database where the entire database is stored in a single file (`digital_health.db`). It is standard and highly suitable for local engineering project demonstrations. However, since we use SQLAlchemy ORM, switching to an enterprise database like PostgreSQL or MySQL in production requires changing just a single line in the configuration URI.

### Q2: What security measures are implemented in your system?
> **Answer**: 
> - **Password Hashing**: User passwords are encrypted using `Werkzeug` security tools (PBKDF2 with SHA-256 salts) so plain-text passwords are never stored.
> - **Session Security**: Pages are protected with Flask-Login decorators (`@login_required`).
> - **Authorization Check**: Routes verify that the `current_user.id` matches the document's `user_id` before downloading, details, or deleting to prevent IDOR (Insecure Direct Object Reference) vulnerabilities.
> - **Filename Sanitization**: Uploaded files are renamed using UUIDs to prevent directory traversal attacks and namespace conflicts.

### Q3: What happens if the PDF uploaded is a scanned image (has no text)?
> **Answer**: `PyPDF2` extracts text from selectable text PDFs. If a user uploads a scanned image PDF, the extracted text will be blank. The classifier will trigger a fallback warning or assign it to the default category (Discharge Summary). In a commercial app, this would be solved by introducing OCR (Optical Character Recognition) libraries like `pytesseract`.
