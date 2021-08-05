"""Scheduler based on Mesa project."""
from mesa.time import BaseScheduler
from mesa_geo.geoagent import GeoAgent


class DataScheduler(BaseScheduler):
    """Scheduler with data consumption on each step."""

    def agent_buffer(self, shuffled: bool = False) -> Iterator[GeoAgent]:
        """Simple generator that yields the agents while letting the user
        remove and/or add agents during stepping.
        """
        agent_keys = list(self._agents.keys())
        if shuffled:
            self.model.random.shuffle(agent_keys)

        for key in agent_keys:
            if key in self._agents:
                yield key, self._agents[key]

    def step(self, gdf) -> None:
        """Execute the step of all agents, one at a time, in random order."""
        for key, agent in self.agent_buffer():
            shape = gdf[gdf['id'] == key]['geometry']
            if shape.empty:
                shape = None
            agent.step(shape)
        self.steps += 1
        self.time += 1
