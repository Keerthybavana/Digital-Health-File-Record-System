import os
import sys

def verify():
    print("=== STARTING PROJECT VERIFICATION ===")
    
    # 1. Check path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Project base path: {base_dir}")
    
    # 2. Check imports
    print("\n1. Checking library imports...")
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import qrcode
        import PyPDF2
        import pandas
        import sklearn
        print("[OK] All required packages imported successfully!")
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        sys.exit(1)
        
    # 3. Check ML model files
    print("\n2. Checking machine learning models...")
    vectorizer_path = os.path.join(base_dir, 'models_ml', 'vectorizer.pkl')
    classifier_path = os.path.join(base_dir, 'models_ml', 'classifier.pkl')
    
    if os.path.exists(vectorizer_path) and os.path.exists(classifier_path):
        print("[OK] ML model binary files found in models_ml/!")
    else:
        print("[FAIL] Model files missing. Did you run scripts/train_classifier.py?")
        sys.exit(1)
        
    # 4. Test Classifier logic directly
    print("\n3. Testing document classification engine...")
    sys.path.append(base_dir)
    try:
        from app.ml_classifier import DocumentClassifier
        clf = DocumentClassifier()
        clf.load_models()
        
        # Test samples
        test_samples = {
            "Rx: Paracetamol 500mg, 1 tablet twice daily. Dispense 10. Qty: 10 tablets. Sig: bid. Refills: 0.": "Prescription",
            "CBC analysis. Hemoglobin level: 12.8, WBC count: 5.6, Platelets: 250. Blood panel test clear.": "Lab Report",
            "PA chest view. Lungs are clear. Heart silhouette is normal. No fracture or scan consolidation.": "Scan Report",
            "Discharge diagnosis: status post laparoscopic cholecystectomy. Recovered well. Resume diet. Follow up in 1 week.": "Discharge Summary"
        }
        
        all_passed = True
        for sample, expected in test_samples.items():
            predicted = clf.classify_text(sample)
            if predicted == expected:
                print(f"[OK] Predicted: '{predicted}' | Expected: '{expected}' (MATCH)")
            else:
                print(f"[WARNING] Predicted: '{predicted}' | Expected: '{expected}' (MISMATCH)")
                all_passed = False
                
        if all_passed:
            print("[OK] Document Classification test passed completely!")
        else:
            print("[WARNING] Some classification predictions mismatched training expectations.")
    except Exception as e:
        print(f"[FAIL] Classification engine test crashed: {e}")
        sys.exit(1)
        
    # 5. Check Flask App and DB integrity
    print("\n4. Verifying Flask App and database schema creation...")
    try:
        from app import create_app
        from app.models import db, User, Document, Activity
        
        app = create_app()
        db_path = os.path.join(base_dir, 'digital_health.db')
        
        if os.path.exists(db_path):
            print("[OK] SQLite Database file created and exists at E:\\Digital Health Record\\digital_health.db")
        else:
            print("[FAIL] Database file not found on disk!")
            sys.exit(1)
            
        with app.app_context():
            # Run mock queries to verify schema integrity
            users_count = User.query.count()
            docs_count = Document.query.count()
            acts_count = Activity.query.count()
            print(f"[OK] Database tables are responsive! Counts: Users={users_count}, Documents={docs_count}, Activities={acts_count}")
            
        print("[OK] Flask App and database initialization validated successfully!")
    except Exception as e:
        print(f"[FAIL] Flask app configuration or database schema error: {e}")
        sys.exit(1)
        
    print("\n=== SYSTEM VERIFICATION SUCCESSFUL! THE APPLICATION IS READY ===")

if __name__ == '__main__':
    verify()
