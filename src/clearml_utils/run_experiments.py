"""Run multiple experiments with ClearML tracking."""

import logging

from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from src.clearml_utils.train_with_clearml import load_data, train_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_all_experiments():
    """Run experiments with different algorithms."""
    # Load data
    X_train, X_test, y_train, y_test = load_data()

    from typing import Any

    experiments: list[tuple[str, Any, dict[str, Any]]] = [
        (
            "LogisticRegression",
            LogisticRegression(random_state=42, max_iter=1000),
            {"max_iter": 1000, "solver": "lbfgs", "algorithm": "LogisticRegression"},
        ),
        (
            "RandomForest",
            RandomForestClassifier(n_estimators=100, random_state=42),
            {"n_estimators": 100, "max_depth": None, "algorithm": "RandomForest"},
        ),
        (
            "SVM",
            SVC(kernel="rbf", random_state=42),
            {"kernel": "rbf", "C": 1.0, "algorithm": "SVM"},
        ),
        (
            "KNN",
            KNeighborsClassifier(n_neighbors=5),
            {"n_neighbors": 5, "algorithm": "KNN"},
        ),
        (
            "DecisionTree",
            DecisionTreeClassifier(random_state=42),
            {"max_depth": None, "algorithm": "DecisionTree"},
        ),
        (
            "GradientBoosting",
            GradientBoostingClassifier(random_state=42),
            {"n_estimators": 100, "algorithm": "GradientBoosting"},
        ),
        (
            "AdaBoost",
            AdaBoostClassifier(random_state=42),
            {"n_estimators": 50, "algorithm": "AdaBoost"},
        ),
        (
            "NaiveBayes",
            GaussianNB(),
            {"algorithm": "NaiveBayes"},
        ),
        (
            "MLP",
            MLPClassifier(random_state=42, max_iter=1000),
            {"max_iter": 1000, "algorithm": "MLP"},
        ),
    ]

    logger.info(f"🚀 Running {len(experiments)} experiments...")

    results = []
    for algorithm_name, model, params in experiments:
        try:
            accuracy = train_model(
                algorithm_name,
                model,
                X_train,
                X_test,
                y_train,
                y_test,
                params,
            )
            results.append({"algorithm": algorithm_name, "accuracy": accuracy, "status": "success"})
            logger.info(f"✅ {algorithm_name}: accuracy={accuracy:.4f}")
        except Exception as e:
            results.append({"algorithm": algorithm_name, "status": "error", "error": str(e)})
            logger.error(f"❌ {algorithm_name}: {e}")

    logger.info(f"✅ Completed {len(results)} experiments")
    return results


if __name__ == "__main__":
    run_all_experiments()
