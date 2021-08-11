"""Main file CLI for run the simulation of the Geo Covid Model."""

import click
import glob
import tarfile
import logging
import os

from geocovid.model import GeoCovidModel
from geocovid.utils import start_spark
from geocovid.data_pipeline import extract_data_spark, transform_data_spark


logger = logging.getLogger(__name__)


@click.command()
def main():
    """Main function to run geo covid simulation.

    Parameters
    ----------

    """
    gcm = GeoCovidModel()
    path_gz = '/Users/awolfmann/Documents/data_eng_challenge/Data Engineer - Covid/data/iso_date=2020-06-01.tar.gz'
    spark = start_spark()
    with tarfile.open(path_gz, 'r:gz') as tf:
        for m in tf.getmembers():
            if m.isdir():
                logger.info(' dirname %s' % m.name)
                sdf = extract_data_spark(os.path.basename(m.name), spark)
                logger.info('extracted data')
                gdf = transform_data_spark(sdf, spark)
                logger.info('transformed data')
                hours = gdf.index.levels[0]

                for h in hours:
                    gcm.step(gdf.loc[h, :])
                    logger.info('data collector %s' % gcm.datacollector.model_vars)
        tf.close()


if __name__ == "__main__":
    main()
