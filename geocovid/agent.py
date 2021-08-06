"""Agents for a SIR Model."""

import enum
import numpy as np

from mesa import Model
from mesa_geo.geoagent import GeoAgent
from shapely.geometry.base import BaseGeometry


class Status(enum.IntEnum):
    """Agent Status."""

    SUSCEPTIBLE = 0
    INFECTED = -1
    RECOVERED = 1


class PersonAgent(GeoAgent):
    """An agent with fixed initial position and status."""

    def __init__(
        self,
        unique_id: str,
        model: Model,
        shape: BaseGeometry
    ):
        """Init method."""
        super().__init__(unique_id, model, shape)
        self.position = None
        self.status = Status.SUSCEPTIBLE
        self.infection_time = 0
        self.infected_at = 0

    def step(self,
        shape: BaseGeometry = None
        ) -> None:
        """One step of the agent."""
        self.check()
        self.interact()
        self.move(shape)

    def check(self) -> None:
        """Check agent status."""
        if self.status == Status.INFECTED:
            death_prob = self.model.death_prob
            np.random.seed = self.random.seed
            is_alive = np.random.choice([0, 1], p=[death_prob, 1 - death_prob])
            if is_alive == 0:
                self.model.schedule.remove(self)
                # removerlo del geospace
                self.model.deaths += 1
            elif self.model.schedule.time - self.infected_at >= self.model.treatment_period:
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
            contacts = self.model.grid.get_neighbors_within_distance(self,
                                                                     self.model.exposure_distance)
            for c in contacts:
                if c.status is not Status.INFECTED:
                    infect = self.random.random() <= self.model.infection_prob
                    if infect:
                        c.status = Status.INFECTED
                        c.infected_at = self.model.schedule.time
