"""Tests for data loading functions."""

import pandas as pd

from src.data.make_dataset import load_iris_dataset


def test_load_iris_dataset():
    """Test that Iris dataset loads correctly."""
    df = load_iris_dataset()

    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 150
    assert df.shape[1] == 6  # 4 features + target + target_name
    assert "target" in df.columns
    assert "target_name" in df.columns


def test_iris_dataset_columns():
    """Test that Iris dataset has correct columns."""
    df = load_iris_dataset()

    expected_columns = [
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
        "target",
        "target_name",
    ]

    for col in expected_columns:
        assert col in df.columns
