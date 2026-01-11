"""Script to run multiple ML experiments with different algorithms."""

import json
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from src.utils.mlflow_utils import setup_mlflow


def load_data():
    """Load and prepare data."""
    data_file = Path("data/processed/iris_processed.csv")
    if data_file.exists():
        df = pd.read_csv(data_file)
        X = df.drop(["target", "target_name"], axis=1).values
        y = df["target"].values
    else:
        iris = load_iris()
        X, y = iris.data, iris.target

    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_and_log(
    algorithm_name: str,
    model,
    X_train,
    X_test,
    y_train,
    y_test,
    params: dict,
):
    """Train model and log to MLflow."""
    with mlflow.start_run(run_name=algorithm_name):
        # Log algorithm name as both tag and param
        mlflow.set_tag("algorithm", algorithm_name)
        mlflow.log_param("algorithm", algorithm_name)

        # Log parameters
        mlflow.log_params(params)

        # Train model
        model.fit(X_train, y_train)

        # Evaluate
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)

        # Log metrics
        mlflow.log_metric("train_accuracy", train_score)
        mlflow.log_metric("test_accuracy", test_score)
        mlflow.log_metric("accuracy", test_score)  # Main metric

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Log additional info
        mlflow.log_param("n_samples", len(X_train))
        mlflow.log_param("n_features", X_train.shape[1])

        print(f"✅ {algorithm_name}: accuracy={test_score:.4f}")

        return test_score


def run_all_experiments():
    """Run experiments with different algorithms."""
    # Setup MLflow
    setup_mlflow(tracking_uri="sqlite:///mlflow.db", experiment_name="iris-classification")

    # Load data
    X_train, X_test, y_train, y_test = load_data()

    experiments = []

    # 1. Logistic Regression
    experiments.append(
        (
            "LogisticRegression",
            LogisticRegression(random_state=42, max_iter=1000),
            {"max_iter": 1000, "solver": "lbfgs"},
        )
    )

    # 2. Random Forest (baseline)
    experiments.append(
        (
            "RandomForest",
            RandomForestClassifier(n_estimators=100, random_state=42),
            {"n_estimators": 100, "max_depth": None},
        )
    )

    # 3. Random Forest (more trees)
    experiments.append(
        (
            "RandomForest_200",
            RandomForestClassifier(n_estimators=200, random_state=42),
            {"n_estimators": 200, "max_depth": None},
        )
    )

    # 4. Random Forest (deeper)
    experiments.append(
        (
            "RandomForest_deep",
            RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            {"n_estimators": 100, "max_depth": 10},
        )
    )

    # 5. Decision Tree
    experiments.append(
        (
            "DecisionTree",
            DecisionTreeClassifier(random_state=42),
            {"max_depth": None, "min_samples_split": 2},
        )
    )

    # 6. Decision Tree (pruned)
    experiments.append(
        (
            "DecisionTree_pruned",
            DecisionTreeClassifier(max_depth=5, random_state=42),
            {"max_depth": 5, "min_samples_split": 2},
        )
    )

    # 7. SVM (linear)
    experiments.append(
        (
            "SVM_linear",
            SVC(kernel="linear", random_state=42),
            {"kernel": "linear", "C": 1.0},
        )
    )

    # 8. SVM (RBF)
    experiments.append(
        (
            "SVM_rbf",
            SVC(kernel="rbf", random_state=42),
            {"kernel": "rbf", "C": 1.0, "gamma": "scale"},
        )
    )

    # 9. SVM (polynomial)
    experiments.append(
        (
            "SVM_poly",
            SVC(kernel="poly", degree=3, random_state=42),
            {"kernel": "poly", "degree": 3, "C": 1.0},
        )
    )

    # 10. K-Nearest Neighbors (k=3)
    experiments.append(
        (
            "KNN_3",
            KNeighborsClassifier(n_neighbors=3),
            {"n_neighbors": 3, "weights": "uniform"},
        )
    )

    # 11. K-Nearest Neighbors (k=5)
    experiments.append(
        (
            "KNN_5",
            KNeighborsClassifier(n_neighbors=5),
            {"n_neighbors": 5, "weights": "uniform"},
        )
    )

    # 12. K-Nearest Neighbors (k=7)
    experiments.append(
        (
            "KNN_7",
            KNeighborsClassifier(n_neighbors=7),
            {"n_neighbors": 7, "weights": "uniform"},
        )
    )

    # 13. Naive Bayes
    experiments.append(
        (
            "NaiveBayes",
            GaussianNB(),
            {"var_smoothing": 1e-9},
        )
    )

    # 14. Gradient Boosting
    experiments.append(
        (
            "GradientBoosting",
            GradientBoostingClassifier(n_estimators=100, random_state=42),
            {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
        )
    )

    # 15. AdaBoost
    experiments.append(
        (
            "AdaBoost",
            AdaBoostClassifier(n_estimators=100, random_state=42),
            {"n_estimators": 100, "learning_rate": 1.0},
        )
    )

    # 16. MLP (Neural Network)
    experiments.append(
        (
            "MLP",
            MLPClassifier(hidden_layer_sizes=(100,), max_iter=1000, random_state=42),
            {"hidden_layer_sizes": "(100,)", "max_iter": 1000, "activation": "relu"},
        )
    )

    # 17. SGD Classifier
    experiments.append(
        (
            "SGD",
            SGDClassifier(random_state=42, max_iter=1000),
            {"max_iter": 1000, "loss": "hinge"},
        )
    )

    # 18. Voting Classifier
    experiments.append(
        (
            "Voting",
            VotingClassifier(
                estimators=[
                    ("rf", RandomForestClassifier(n_estimators=50, random_state=42)),
                    ("svm", SVC(probability=True, random_state=42)),
                    ("nb", GaussianNB()),
                ],
                voting="soft",
            ),
            {"voting": "soft", "n_estimators_rf": 50},
        )
    )

    print(f"\n🚀 Running {len(experiments)} experiments...\n")

    results = []
    for name, model, params in experiments:
        try:
            accuracy = train_and_log(name, model, X_train, X_test, y_train, y_test, params)
            results.append({"algorithm": name, "accuracy": accuracy, "status": "success"})
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append({"algorithm": name, "accuracy": 0.0, "status": "error", "error": str(e)})

    # Save results summary
    results_file = Path("metrics/experiments_summary.json")
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Completed {len([r for r in results if r['status'] == 'success'])} experiments")
    print(f"📊 Results saved to {results_file}")

    return results


if __name__ == "__main__":
    run_all_experiments()
