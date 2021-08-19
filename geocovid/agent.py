"""Agents for a SIR Model."""

import enum

from mesa import Model
from mesa_geo.geoagent import GeoAgent
import numpy as np
from shapely.geometry.base import BaseGeometry

from geocovid.constants import STEPS_PER_DAY


class Status(enum.IntEnum):
    """Agent Status."""

    SUSCEPTIBLE = 0
    INFECTED = -1
    RECOVERED = 1
    DEAD = -2


class PersonAgent(GeoAgent):
    """An agent with fixed initial position and status."""

    def __init__(self, unique_id: str, model: Model, shape: BaseGeometry):
        """Init method."""
        super().__init__(unique_id, model, shape)
        self.pos = None
        self.status = Status.SUSCEPTIBLE
        self.infection_time = 0
        self.infected_at = 0

    def step(self, shape: BaseGeometry = None) -> None:
        """One step of the agent."""
        self.check()
        self.interact()
        self.move(shape)

    def check(self) -> None:
        """Check agent status."""
        if self.status == Status.INFECTED:
            death_prob = self.model.death_prob
            min_death_period = self.model.min_death_period * STEPS_PER_DAY
            elapsed_time = self.model.schedule.time - self.infected_at
            treatment_period = self.model.treatment_period * STEPS_PER_DAY
            np.random.seed = self.random.seed

            if elapsed_time >= min_death_period:
                is_alive = np.random.choice([0, 1], p=[death_prob, 1 - death_prob])
                if is_alive == 0:
                    self.status = Status.DEAD
                    self.model.deaths += 1
                elif elapsed_time >= treatment_period:
                    self.status = Status.RECOVERED

    def move(self, shape: BaseGeometry = None) -> None:
        """
        Move the agent in the space.

        If shape is None, it stays in the same place.
        """
        if shape:
            self.shape = shape

    def interact(self):
        """An agent interacts with others and may infect them."""
        if self.status is Status.INFECTED:
            contacts = self.model.grid.get_neighbors_within_distance(
                self, self.model.exposure_distance
            )
            for contact in contacts:
                if contact.status is not Status.INFECTED:
                    infect = self.random.random() <= self.model.infection_prob
                    if infect:
                        contact.status = Status.INFECTED
                        contact.infected_at = self.model.schedule.time
                        self.model.infections_step += 1
