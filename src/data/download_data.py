"""Script to download and save raw data for DVC tracking."""

from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris


def download_iris_data():
    """Download Iris dataset and save as raw data."""
    # Load data
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    df["target_name"] = df["target"].map(dict(enumerate(iris.target_names)))

    # Create output directory
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw data
    output_file = output_dir / "iris.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Raw data saved to {output_file}")
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")

    return df


if __name__ == "__main__":
    download_iris_data()
