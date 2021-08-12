# Geocovid
Covid simulation based on a SIR Model, using Geospatial data from cellphones GPS.

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
│   └── server: Visualization server based on Mesa and mesa-geo libraries.
├── run: script to launch the visualization server.
├── data: folder with the provided data.
└── tests: tests for all the package.

```

## Running
For running purpose, a [main.py](./geocovid/main.py) file was created that instantiate the extractors and execute them depending on the configuration set. It is also executable with CLI using [Click](https://click.palletsprojects.com/en/8.0.x/) package.

### Running Procedure
Example command to run this package:
```
$ poetry run main.py
```

## Testing
For testing purposes, pytest is used. Pytest sits on top of unittest and adds some capabilities like fixtures and an easier test creation process.

## Linting
For this module it was used tools to lint code with coding good practice.
- black : code formatter.
- isort : sort imports.
- pylint : static code analysis tool.
- pre-commit : to run all the linting process before commit.
