"""Main file CLI for run the simulation of the Geo Covid Model."""

import click

from geocovid.model import GeoCovidModel

@click.command()
def main():
    """Main function to run geo covid simulation.

    Parameters
    ----------

    """
    cm = GeoCovidModel()
    # listar todos los archivos
    # iterar sobre ellos, extrayendolo
    files = os.path(path)
    for f in files:
        df = read(f)
        df = preprocess_time(df)
        df = preprocess_id(df)
        gdf = preprocess_geo(df)
        gdf_agg = preprocess_aggregate(gdf)
        hours = gdf_agg.hour.unique()

        for h in hours:
            cm.step(gdf_agg[gdf_agg['hour'] == h])

if __name__ == "__main__":
    main()
