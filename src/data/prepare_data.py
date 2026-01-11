"""Script to prepare data for training."""

import json
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris


def prepare_iris_data():
    """Prepare Iris dataset and save to processed folder."""
    # Load data
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    df["target_name"] = df["target"].map(dict(enumerate(iris.target_names)))

    # Create output directory
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save processed data
    output_file = output_dir / "iris_processed.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Data saved to {output_file}")

    # Calculate and save statistics
    stats = {
        "n_samples": len(df),
        "n_features": len(iris.feature_names),
        "n_classes": len(iris.target_names),
        "class_distribution": df["target_name"].value_counts().to_dict(),
    }

    metrics_dir = Path("metrics")
    metrics_dir.mkdir(exist_ok=True)
    stats_file = metrics_dir / "data_stats.json"
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"✅ Statistics saved to {stats_file}")

    # Create distribution plot data
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)
    plot_data = {
        "sepal_length": df["sepal length (cm)"].tolist(),
        "sepal_width": df["sepal width (cm)"].tolist(),
        "petal_length": df["petal length (cm)"].tolist(),
        "petal_width": df["petal width (cm)"].tolist(),
    }
    plot_file = plots_dir / "data_distribution.json"
    with open(plot_file, "w") as f:
        json.dump(plot_data, f, indent=2)
    print(f"✅ Plot data saved to {plot_file}")

    return df


if __name__ == "__main__":
    prepare_iris_data()
