"""Main file CLI for run the simulation of the Geo Covid Model."""

import glob
import logging
import os
import tarfile

import click

from geocovid.constants import DATA_DIR, TMP_DIR
from geocovid.data_pipeline import extract_data_spark, transform_data_spark
from geocovid.model import GeoCovidModel
from geocovid.utils import start_spark

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info("test")


@click.command()
def main():
    """Main function to run geo covid simulation.

    Parameters
    ----------

    """
    gcm = GeoCovidModel()
    files = glob.glob(os.path.join(DATA_DIR, "*.tar.gz"))
    sorted_files = sorted(files)
    spark = start_spark()
    for file in sorted_files[:1]:
        with tarfile.open(file, "r:gz") as tfile:
            path = os.path.join(TMP_DIR, os.path.basename(file).split(".")[0])
            tfile.extractall(path=path, members=tfile)
            logger.info("dirname %s", path)
            sdf = extract_data_spark(path, spark)
            logger.info("extracted data")
            gdf = transform_data_spark(sdf, spark)
            logger.info("transformed data")
            hours = gdf.index.levels[0]

            for hour in hours:
                gcm.step(gdf.loc[hour, :])
                logger.info("data collector %s", gcm.datacollector.model_vars)
            tfile.close()


if __name__ == "__main__":
    main()
