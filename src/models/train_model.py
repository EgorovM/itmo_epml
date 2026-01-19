"""Script to train machine learning models."""

import os

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def train_iris_classifier():
    """Train a Random Forest classifier on Iris dataset."""
    # Load data
    iris = load_iris()
    X, y = iris.data, iris.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))

    # Save model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/iris_classifier.pkl")
    print("\nModel saved to models/iris_classifier.pkl")

    return model


if __name__ == "__main__":
    train_iris_classifier()
