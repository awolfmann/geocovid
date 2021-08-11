"""Data Pipeline."""

import geopandas as gpd
import pandas as pd
import os
import tarfile

from pyspark.sql import SparkSession
from pandas import DataFrame as p_df
from geopandas import GeoDataFrame


def extract_data_spark(path, spark: SparkSession):
    """Read and return dataframe."""
    sdf = spark.read.parquet(path)
    return sdf


def transform_data_spark(sdf, spark: SparkSession) -> GeoDataFrame:
    """Transform Data."""
    agg_df = aggregate_spatial_data(sdf, spark)
    clean_df = remove_outliers(agg_df, spark)
    gdf = spark_to_geopandas(clean_df)
    set_index_df(gdf)
    return gdf


def aggregate_spatial_data(sdf, spark: SparkSession):
    """
    Aggregate spatial data by hour and id.

    Parameters
    """
    sdf.createOrReplaceTempView("points")
    point_df = spark.sql(
        """
        SELECT points.id, hour(cast(points.timestamp AS timestamp)) AS h,
                ST_Envelope_Aggr(ST_Point(cast(points.latitude AS Decimal(24,20)),
                                          cast(points.longitude AS Decimal(24,20)))) 
                AS geometry
        FROM points group by h, id
        """
    )
    return point_df


def remove_outliers(sdf, spark: SparkSession):
    """
    Remove outliers when the aggregated area is too big.

    If the area is too big it returns the centroid.
    """
    sdf.createOrReplaceTempView("points_agg")
    clean_df = spark.sql(
        """
        SELECT id, h,
            CASE WHEN ST_Area(points_agg.geometry) < 0.0001
            THEN points_agg.geometry
            ELSE ST_Centroid(points_agg.geometry)
            END as geometry
        FROM points_agg
        """
    )
    return clean_df


def spark_to_geopandas(sdf) -> GeoDataFrame:
    """Convert Spark DF to GeoPandas DF."""
    pandas_df = sdf.toPandas()
    gdf = gpd.GeoDataFrame(pandas_df, geometry="geometry")
    return gdf


def set_index_df(gdf: GeoDataFrame) -> None:
    """Set index for a geodf."""
    gdf.set_index(['h', 'id'], inplace=True)


def preprocess_time(df: p_df):
    """Preprocess time."""
    df['datetime'] = pd.to_datetime(df.timestamp, unit='s')
    df['hour'] = df['datetime'].dt.hour
    df['date'] = df['datetime'].dt.date
    return df


def preprocess_id(df: p_df) -> None:
    """Preprocess id as index."""
    df.set_index('id', inplace=True)


def preprocess_geo(df: p_df) -> GeoDataFrame:
    """Transform df to geo df."""
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df['longitude'], df['latitude']))
    return gdf


def preprocess_aggregate(gdf: GeoDataFrame):
    """Preprocess Aggregate points by hour."""
    gdf_dis = gdf.dissolve(by=['hour', 'id'])
    return gdf_dis
