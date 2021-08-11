"""Main file CLI for run the simulation of the Geo Covid Model."""

import glob
import logging
import os
import tarfile

import click

from geocovid.data_pipeline import extract_data_spark, transform_data_spark
from geocovid.model import GeoCovidModel
from geocovid.utils import start_spark

logger = logging.getLogger(__name__)


@click.command()
def main():
    """Main function to run geo covid simulation.

    Parameters
    ----------

    """
    gcm = GeoCovidModel()
    path_gz = """/Users/awolfmann/Documents/data_eng_challenge/grandata-challenge/
                geocovid/data/iso_date=2020-06-01.tar.gz"""
    files = [file for file in glob.glob("""/Users/awolfmann/Documents/data_eng_challenge/grandata-challenge/
                geocovid/data/*.tar.gz""")]
    sorted_files = sorted(files)
    spark = start_spark()
    with tarfile.open(path_gz, "r:gz") as tfile:
        for member in tfile.getmembers():
            if member.isdir():
                logger.info(" dirname %s", member.name)
                sdf = extract_data_spark(os.path.basename(member.name), spark)
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
