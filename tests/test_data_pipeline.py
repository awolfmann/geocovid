"""Data pipeline tests."""

from pyspark.sql import SparkSession
import pytest


@pytest.fixture(scope="session")
def spark():
    """Create Spark Session fixture."""
    return SparkSession.builder.master("local").appName("tests").getOrCreate()
