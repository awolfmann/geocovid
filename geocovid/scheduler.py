"""Scheduler based on Mesa project."""
from typing import Iterator, Tuple

from geopandas import GeoDataFrame
from mesa.time import BaseScheduler
from mesa_geo.geoagent import GeoAgent


class DataScheduler(BaseScheduler):
    """Scheduler with data consumption on each step."""

    def agent_buffer(self, shuffled: bool = False) -> Iterator[Tuple]:
        """Simple generator that yields the agents while letting the user
        remove and/or add agents during stepping.
        """
        agent_keys = list(self._agents.keys())
        if shuffled:
            self.model.random.shuffle(agent_keys)

        for key in agent_keys:
            if key in self._agents:
                yield key, self._agents[key]

    def step(self, gdf: GeoDataFrame) -> None:
        """Execute the step of all agents, one at a time, in random order."""
        for key, agent in self.agent_buffer():
            try:
                shape = gdf.loc[key]['geometry']
            except:
                shape = None
            agent.step(shape)
        self.steps += 1
        self.time += 1
