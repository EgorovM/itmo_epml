"""Script to download and prepare datasets."""

import pandas as pd
from sklearn.datasets import load_iris


def load_iris_dataset() -> pd.DataFrame:
    """Load Iris dataset from sklearn.

    Returns:
        DataFrame with Iris dataset including target column.
    """
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    df["target_name"] = df["target"].map(dict(enumerate(iris.target_names)))
    return df


if __name__ == "__main__":
    df = load_iris_dataset()
    print(f"Dataset shape: {df.shape}")
    print(f"\nFirst few rows:\n{df.head()}")
    print(f"\nDataset info:\n{df.info()}")
