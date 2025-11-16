"""Tests for model training functions."""

import os

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def test_train_iris_classifier():
    """Test that model training works correctly."""
    # Load data
    iris = load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    assert accuracy > 0.9  # Should achieve high accuracy on Iris dataset
    assert model.n_estimators == 10


def test_model_saves_correctly():
    """Test that trained model can be saved."""
    import joblib

    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)

    # Train and save model
    iris = load_iris()
    X, y = iris.data, iris.target
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)

    model_path = "models/test_model.pkl"
    joblib.dump(model, model_path)

    # Check that file exists
    assert os.path.exists(model_path)

    # Clean up
    if os.path.exists(model_path):
        os.remove(model_path)
