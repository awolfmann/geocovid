"""Heat Map."""
import glob
import logging
import os

import click
import folium
from folium.plugins import HeatMapWithTime
import pandas as pd

from geocovid.constants import MAP_COORDS, OUTPUT_DIR


def generate_basemap(default_location=MAP_COORDS, default_zoom_start=11):
    """Generate Folium base map on a default location."""
    base_map = folium.Map(
        location=default_location, control_scale=True, zoom_start=default_zoom_start
    )
    return base_map


@click.command()
@click.option(
    "--output_file", type=click.STRING, default="heatmap.html", help="Output filename"
)
def main(output_file: str) -> None:
    """Heatmap script."""
    files = glob.glob(os.path.join(OUTPUT_DIR, "results_agents_*.json"))
    sorted_files = sorted(files)
    last_agent_filename = sorted_files[-1]
    a_df = pd.read_json(last_agent_filename, orient="table")
    heat_data = [
        [
            [row["lat"], row["lon"]]
            for index, row in a_df.loc[i, :].iterrows()
            if row["status"] == -1
        ]
        for i in a_df.index.levels[0]
    ]
    base_map = generate_basemap()
    hm = HeatMapWithTime(heat_data, auto_play=True, max_opacity=0.3)
    hm.add_to(base_map)
    base_map.save(os.path.join(OUTPUT_DIR, output_file))


if __name__ == "__main__":
    main()
