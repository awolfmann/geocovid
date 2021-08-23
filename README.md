# Geocovid
Covid simulation based on a Agent Based - [SIR Model](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SIR_model), using Geospatial data from cellphones GPS.
The package assumes [Spark 3.0](https://spark.apache.org/) and [Sedona](https://sedona.apache.org/) previously installed.
Data provided can be download from [here](https://drive.google.com/drive/folders/1lR8_ijSqXj7orvrlmvIXe5flbxI31PMP).

## Main steps
* Data processing: data provided are in a compressed files with a set of parquet files inside, for 21 consecutive days.
    - Data columns: Id, timestamp, latitude, longitude, geohash_12.
    - For the extraction process, data is unpacked to tmp/ directory and then loaded as Spark Dataframes.
    - Apache Sedona is used to build and operate over the Geospatial Data. Specially for aggregating data per hour to build a Polygon.
    - Grouped data of each user per hour building a Polygon. If the Polygon is too big, the centroid is imputed as its position.
    - Finally the output is a GeoPandas Dataframe in order to serve as input for the simulation.

* Model simulation
    - A [SIR Model](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SIR_model) is implemented based on [Mesa](https://mesa.readthedocs.io/en/stable/#) and [Mesa-geo](https://github.com/Corvince/mesa-geo) Python libraries, but extendend to consume data about positions at each step.
    - Data collection extended to collect agents info once per day instead of each 24hs.
* Visualization
    - Mesa and Mesa-geo provides some visualization modules.
    - A 2d (lat, long) histogram is provided as result of the simulation.
    - Timeline evolution with main metrics.

## Modelling Asumptions
* Discretized modelling by 1hour step.
* Grouped data of each user per hour building a Polygon. If the Polygon is too big, the centroid is imputed as its position.
* Latitude and Longitude information is used, even geohash_12 has a better precision.
* Exposed time is ignored. If there is a contact between the Polygon in the one hour step, the model add the contact as a possible candidate for a new infected agent.

## Improvement Opportunities
* Data processing:
    - Reduce timeframe aggregation.
    - Remove Pandas/GeoPandas dependency.
    - Remove hardcoded values in SparkSQL.
    - Remove duplicates.
    - Degrees to meters projection.
* Modelling:
    - Include exposure time and confidence intervals.
    - Explore more complex models like SEIR, or Network based.
    - Batch run with different parameter configs.
* Visualization:
    - Better usage and extend the  MapModules provided by Mesa-geo library.
* Productionalization:
    - Dockerize the project.
    - Increase test coverage.
    - Parallelize data procesing with Spark on an EMR cluster.
    - Use Airflow as orchestrator for monitoring each step of the pipeline.
    - Improve Error handling.
    - CI integrations.
    - Improve processing performance.
    - Improve logging levels.


# Installation
## Installation with Poetry (Recommended)

This package was developed with [Poetry](https://python-poetry.org/docs/) as an environment isolation and dependencies solving tool.

To install Poetry download the source and run it:

install and add it to the shell:
```
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
$ source $HOME/.poetry/env
```

to uninstall Poetry:
```
$ python get-poetry.py --uninstall
$ POETRY_UNINSTALL=1 python get-poetry.py
```

#### Install package

To install the package run:
```
$ poetry install
```

## Project structure
```
geocovid
├── geocovid:
│   ├── main: script that run the project, with CLI.
│   ├── utils: utilities file to use in the package.
│   ├── constants: constants values.
│   ├── model: GeoCovidModel based on Mesa and mesa-geo libraries.
│   ├── agent: Agent based on Mesa and mesa-geo libraries.
│   ├── data_pipeline: Pipeline for extracting and transforming data using Spark and GeoPandas.
│   ├── scheduler: DataScheduler based on Mesa and mesa-geo libraries.
│   ├── server: Visualization server based on Mesa and mesa-geo libraries.
│   └── datacollection: AggDataCollector, extended version to collect data once per day.
├── run: script to launch the visualization server.
├── data: folder with the provided data.
└── tests: tests for all the package.

```

## Running
For running purpose, a [main.py](./geocovid/main.py) was created. It is also executable with CLI using [Click](https://click.palletsprojects.com/en/8.0.x/) package.

### Running Procedure
Example command to run this package:
```
$ poetry run main.py
```
#### Visualization
```
$ poetry run geocovid/visualization/heatmap.py
```

## Testing
For testing purposes, pytest is used. Pytest sits on top of unittest and adds some capabilities like fixtures and an easier test creation process.
- DISCLAIMER: pending to implement.

## Linting
For this module it was used tools to lint code with coding best practices.
- black : code formatter.
- isort : sort imports.
- pylint : static code analysis tool. Disabled arguments-differ rule.
- pre-commit : to run all the linting process before commit.
- DISCLAIMER: some were intentionally ignored.

## References
* https://github.com/Corvince/mesa-geo/blob/master/examples/GeoSIR/model.py
* https://github.com/nickmancol/covid-sim-mesa/blob/main/ABMCovid.ipynb
* https://sedona.apache.org/tutorial/sql-python/#integration-with-geopandas-and-shapely
