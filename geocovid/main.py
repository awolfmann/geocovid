"""Main file CLI for run the simulation of the Geo Covid Model."""

from datetime import datetime
import glob
import logging
import os
import tarfile

import click

from geocovid.constants import DATA_DIR, OUTPUT_DIR, TMP_DIR
from geocovid.data_pipeline import extract_data_spark, transform_data_spark
from geocovid.model import GeoCovidModel
from geocovid.utils import start_spark

LOG_FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FMT)
logger = logging.getLogger(__name__)


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
    for file in sorted_files:
        with tarfile.open(file, "r:gz") as tfile:
            try:
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

            except EOFError as eof:
                logger.info("FAILED dirname %s", eof)

            tfile.close()

    date = datetime.now().strftime("%Y_%m_%d-%I:%M")
    logger.info("dumping model vars results to json")
    model_vars_df = gcm.datacollector.get_model_vars_dataframe()
    model_vars_df.to_json(
        os.path.join(OUTPUT_DIR, "results_model_{}.json".format(date))
    )

    logger.info("dumping agent vars results to json")
    agent_vars_df = gcm.datacollector.get_agent_vars_dataframe()
    agent_vars_df.to_json(
        os.path.join(OUTPUT_DIR, "results_agents_{}.json".format(date)), orient="table"
    )


if __name__ == "__main__":
    main()
