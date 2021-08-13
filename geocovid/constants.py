"""Constants file."""
import os

DEATH_PROB = 0.05
INFECTION_PROB = 0.05
TREATMENT_PERIOD = 14
EXPOSURE_DISTANCE = 0.0001
INIT_INFECTED = 100
MIN_DEATH_PERIOD = 1
STEPS_PER_DAY = 24

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data/")
TMP_DIR = "/tmp/geocovid"
