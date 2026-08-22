# Application Workflow Diagrams - Digital Health File System

Below are the primary workflows executed by the Digital Health File System, illustrated using Mermaid flowcharts.

---

## 1. Document Upload & Machine Learning Classification Flow

This diagram describes the sequence of actions that occur when a patient uploads a PDF medical report.

```mermaid
sequenceDiagram
    autonumber
    actor Patient as Patient (Browser)
    participant Server as Flask Server (routes.py)
    participant Disk as File System (uploads/)
    participant ML as ML Module (ml_classifier.py)
    participant DB as SQLite DB
    participant QR as QR Generator (qrcode)

    Patient->>Server: Submits PDF file via dashboard form
    Server->>Server: Validates file type is PDF
    Server->>Disk: Saves file under secure, unique UUID filename
    Server->>ML: Triggers classify_pdf(file_path)
    ML->>ML: Extracts text from PDF using PyPDF2
    ML->>ML: Transforms text to TF-IDF features
    ML->>ML: Classifies features using Logistic Regression
    ML-->>Server: Returns category (Prescription, Lab Report, etc.)
    Server->>DB: Inserts Document record (obtains doc_id)
    Server->>QR: Generates QR code pointing to /document/<doc_id>
    QR->>Disk: Saves QR code image in static/qrcodes/
    Server->>DB: Updates Document record with qr_path & commits
    Server->>DB: Logs Activity: "Uploaded document..."
    Server-->>Patient: Redirects to dashboard with Success Toast
```

---

## 2. Authentication & Security Session Flow

This workflow illustrates how user identity is authenticated and maintained.

```mermaid
graph TD
    Start([User navigates to App]) --> IsAuth{Is Authenticated?}
    IsAuth -->|Yes| GoDash[Redirect to Dashboard]
    IsAuth -->|No| Login[Show Login Page]
    
    Login --> Register{New User?}
    Register -->|Yes| SignUp[Show Sign Up Form]
    SignUp --> SubmitSignUp[Submit Register Form]
    SubmitSignUp --> Hashing[Hash Password via PBKDF2]
    Hashing --> SaveUser[Save User to SQLite DB]
    SaveUser --> RedirectLogin[Redirect to Login with success flash]
    RedirectLogin --> Login
    
    Register -->|No| InputLogin[Enter Email & Password]
    InputLogin --> Verify{Verify Credentials?}
    Verify -->|Failed| FlashErr[Flash Error Message]
    FlashErr --> Login
    Verify -->|Passed| SessionInit[Create User Session via Flask-Login]
    SessionInit --> AuditLog[Log Activity: "Logged in successfully"]
    AuditLog --> GoDash
```

---

## 3. QR Code Access & Sharing Flow

This workflow illustrates how QR codes bridge physical reports and digital details.

```mermaid
graph TD
    Scan([Patient Scans QR Code on phone]) --> Resolve[Smartphone resolves details URL]
    Resolve --> Request[Request page: /document/doc_id]
    Request --> CheckSession{Is Patient Logged In?}
    
    CheckSession -->|No| ForceLogin[Redirect to Login Page]
    ForceLogin --> Auth[Patient logs in]
    Auth --> CheckOwner
    
    CheckSession -->|Yes| CheckOwner{Is Document Owned by Current User?}
    
    CheckOwner -->|No| AccessDenied[Show Unauthorized Error]
    CheckOwner -->|Yes| RenderDetail[Render Document Details page]
    
    RenderDetail --> Actions[Patient can view text snippet, download original PDF, or delete]
```
