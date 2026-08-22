# System Architecture - Digital Health File System

Below is the high-level system architecture of the Cloud-Based Digital Health File System with ML-Assisted Document Classification.

```mermaid
graph TD
    %% User Interface Layer
    subgraph UI [Frontend - User Interface]
        Browser[Web Browser - HTML5/JS/Bootstrap 5]
    end

    %% Web Server Layer
    subgraph Backend [Backend - Python Flask App]
        Routes[App Routes - routes.py]
        Auth[Authentication & Session - Flask-Login]
        Classifier[ML Inference - ml_classifier.py]
    end

    %% Database Layer
    subgraph DB [Database Storage]
        SQLite[(SQLite Database - digital_health.db)]
        UsersT[Users Table]
        DocsT[Documents Table]
        ActT[Activities Table]
    end

    %% Machine Learning Layer
    subgraph ML [Machine Learning Model Pipeline]
        PDFReader[PyPDF2 Text Extractor]
        TFIDF[TF-IDF Vectorizer - vectorizer.pkl]
        LogReg[Logistic Regression Model - classifier.pkl]
    end

    %% Storage Layer
    subgraph FileSystem [Server File System Storage]
        UploadDir[PDF Uploads Folder - uploads/]
        QRDir[QR Codes Static Folder - app/static/qrcodes/]
    end

    %% Connection Links
    Browser <-->|HTTP Requests/Responses| Routes
    Routes -->|User Sessions| Auth
    Routes -->|Read/Write Records| SQLite
    
    %% DB Structure Details
    SQLite --- UsersT
    SQLite --- DocsT
    SQLite --- ActT

    %% File Upload and ML classification flow
    Routes -->|Save PDF| UploadDir
    Routes -->|Trigger Extraction| Classifier
    Classifier -->|1. Extract text| PDFReader
    PDFReader -->|2. Vectorize text| TFIDF
    TFIDF -->|3. Predict category| LogReg
    LogReg -->|4. Return classification| Routes
    
    %% QR Generation and storage
    Routes -->|Generate & Save QR code| QRDir
    Routes -->|Display Details & download PDF| Browser
```

## Architectural Components Explanation

1. **Frontend (Browser UI)**: Responsive web application powered by HTML5, JavaScript (main.js), and Bootstrap 5. Provides pages for Authentication (Login/Register), Dashboard (PDF uploader, file explorer, stats counter), and Document Details (displays classification details, text snippet, and download/share buttons).
2. **Backend Engine (Python Flask)**: Modular controller structure matching the MVC architecture patterns. Utilizes blueprints to partition authentication and main app functions. Manages database transactions, files on disk, and machine learning inferences.
3. **Database Layer (SQLite)**: Standard relational file database mapping `User`, `Document`, and `Activity` records using Python SQLAlchemy ORM.
4. **Machine Learning Pipeline**: Uses `PyPDF2` to read files on disk and extract ASCII/UTF-8 texts. The extracted string is then transformed using an offline-trained TF-IDF vectorizer and classified using a Logistic Regression model to distinguish between `Prescription`, `Lab Report`, `Scan Report`, and `Discharge Summary`.
5. **Storage System (File System)**:
   - `uploads/`: Secured top-level folder storing medical PDF files under random hashes (UUID) to prevent duplication or override vulnerabilities.
   - `app/static/qrcodes/`: Hosts PNG images containing generated QR codes mapping specific document URL endpoints for offline sharing.
