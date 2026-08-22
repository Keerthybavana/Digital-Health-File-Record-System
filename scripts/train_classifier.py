import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

def train_model():
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'data', 'sample_dataset.csv')
    models_dir = os.path.join(base_dir, 'models_ml')
    
    # Create models_ml directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"Loading dataset from: {dataset_path}")
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return
        
    df = pd.read_csv(dataset_path)
    
    print(f"Dataset size: {len(df)} samples")
    print(f"Categories distribution:\n{df['category'].value_counts()}")
    
    X = df['text']
    y = df['category']
    
    # Split the dataset for validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\nTraining TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training Logistic Regression Classifier...")
    classifier = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    classifier.fit(X_train_vec, y_train)
    
    # Evaluation
    y_pred = classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Validation Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Fit on the entire dataset for final production use
    print("Re-fitting vectorizer and classifier on full dataset for production use...")
    X_full_vec = vectorizer.fit_transform(X)
    classifier.fit(X_full_vec, y)
    
    # Paths to savepkl files
    vectorizer_path = os.path.join(models_dir, 'vectorizer.pkl')
    classifier_path = os.path.join(models_dir, 'classifier.pkl')
    
    print(f"Saving vectorizer to {vectorizer_path}")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    print(f"Saving classifier to {classifier_path}")
    with open(classifier_path, 'wb') as f:
        pickle.dump(classifier, f)
        
    print("\nModel training completed successfully!")

if __name__ == '__main__':
    train_model()
