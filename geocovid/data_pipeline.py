"""Data Pipeline."""

import geopandas as gpd
import pandas as pd
import os
import tarfile

def read(path):
    df = pd.read_parquet(PATH)
    return df


def preprocess_time(df):
    df['datetime'] = pd.to_datetime(df.timestamp, unit='s')
    df['hour'] = df['datetime'].dt.hour
    df['date'] = df['datetime'].dt.date
    return df


def preprocess_geo(df):
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df['longitude'], df['latitude']))
    return gdf


def preprocess_aggregate(gdf):
    gdf_dis = gdf.dissolve(by=['date', 'hour', 'id'], as_index=False)
    return gdf_dis


def main(path):
    cm = CovidModel()
    # listar todos los archivos
    # iterar sobre ellos, extrayendolo
    files = os.path(path)
    for f in files:
        df = read(f)
        df = preprocess_time(df)
        gdf = preprocess_geo(df)
        gdf_agg = preprocess_aggregate(gdf)
        hours = gdf_agg.hour.unique()

        for h in hours:
            cm.step(gdf_agg[gdf_agg['hour'] == h])