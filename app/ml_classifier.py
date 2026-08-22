import os
import pickle
import PyPDF2

class DocumentClassifier:
    def __init__(self, models_dir=None):
        if models_dir is None:
            # Default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.models_dir = os.path.join(base_dir, 'models_ml')
        else:
            self.models_dir = models_dir
            
        self.vectorizer_path = os.path.join(self.models_dir, 'vectorizer.pkl')
        self.classifier_path = os.path.join(self.models_dir, 'classifier.pkl')
        
        self.vectorizer = None
        self.classifier = None

    def load_models(self):
        """Loads vectorizer and classifier PKL files. Auto-trains if missing."""
        if os.path.exists(self.vectorizer_path) and os.path.exists(self.classifier_path):
            try:
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                with open(self.classifier_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                return True
            except Exception as e:
                print(f"Error loading models: {e}. Will attempt auto-training.")
        
        # If files are missing or loading failed, let's attempt to train them
        return self.auto_train()

    def auto_train(self):
        """Attempts to auto-train the classifier if the training script and dataset exist."""
        base_dir = os.path.dirname(self.models_dir)
        train_script = os.path.join(base_dir, 'scripts', 'train_classifier.py')
        dataset_path = os.path.join(base_dir, 'data', 'sample_dataset.csv')
        
        if os.path.exists(train_script) and os.path.exists(dataset_path):
            print("Model files missing. Auto-training the model using sample dataset...")
            try:
                # Import the train_model function locally to run it
                import sys
                sys.path.append(base_dir)
                from scripts.train_classifier import train_model
                train_model()
                
                # Try reloading
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                with open(self.classifier_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                return True
            except Exception as e:
                print(f"Failed to auto-train model: {e}")
        return False

    def extract_text_from_pdf(self, pdf_path):
        """Extracts text from a PDF file using PyPDF2."""
        text = ""
        try:
            reader = PyPDF2.PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
        return text.strip()

    def classify_text(self, text):
        """Predicts the category of a text string."""
        if not text:
            return "Discharge Summary"  # Safe default if text is empty
            
        if not self.vectorizer or not self.classifier:
            loaded = self.load_models()
            if not loaded:
                # Fallback rule-based matching if models are not available/trained yet
                text_lower = text.lower()
                if any(kw in text_lower for kw in ["rx", "tablet", "capsule", "dosage", "prescribed", "daily"]):
                    return "Prescription"
                elif any(kw in text_lower for kw in ["hemoglobin", "wbc", "rbc", "lipid", "cholesterol", "serum", "blood"]):
                    return "Lab Report"
                elif any(kw in text_lower for kw in ["x-ray", "mri", "ct scan", "ultrasound", "scan", "consolidation"]):
                    return "Scan Report"
                return "Discharge Summary"
        
        try:
            # Vectorize text
            vec_text = self.vectorizer.transform([text])
            # Predict category
            prediction = self.classifier.predict(vec_text)[0]
            return prediction
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Discharge Summary"  # Fallback

    def classify_pdf(self, pdf_path):
        """Extracts text from PDF and returns the predicted category."""
        text = self.extract_text_from_pdf(pdf_path)
        return self.classify_text(text)
