"""Geo Covid Model."""
import enum
import logging
from typing import List, Any

from geopandas import GeoDataFrame
from mesa import Model
from mesa.datacollection import DataCollector
from mesa_geo import GeoSpace

from geocovid.agent import PersonAgent, Status
from geocovid.constants import (
    DEATH_PROB,
    EXPOSURE_DISTANCE,
    INFECTION_PROB,
    INIT_INFECTED,
    MIN_DEATH_PERIOD,
    TREATMENT_PERIOD,
)
from geocovid.scheduler import DataScheduler

logger = logging.getLogger(__name__)


class StepSize(enum.IntEnum):
    """Agent Status."""

    DAY = 1
    HOUR = 24
    MINUTE = 24 * 60


class GeoCovidModel(Model):
    """A model with some number of agents."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Geo Covid Model initialization.

        Parameters
        ----------
        infection_prob: float = INFECTION_PROB,
        death_prob: float = DEATH_PROB,
        treatment_period: int = TREATMENT_PERIOD,
        exposure_distance: float = EXPOSURE_DISTANCE,
        init_infected: Union[int, List] = INIT_INFECTED,
        min_death_period: int = MIN_DEATH_PERIOD,
        seed: int = None

        """
        super().__init__()
        self.schedule = DataScheduler(self)
        self.grid = GeoSpace()
        self.infection_prob = INFECTION_PROB
        self.death_prob = DEATH_PROB
        self.treatment_period = TREATMENT_PERIOD
        self.exposure_distance = EXPOSURE_DISTANCE
        self.init_infected = INIT_INFECTED
        self.min_death_period = MIN_DEATH_PERIOD
        self.steps = 0
        self.deaths = 0
        self.infections_step = 0

        self.datacollector = DataCollector(
            model_reporters={
                "S": compute_s,
                "I": compute_i,
                "R": compute_r,
                "D": compute_d,
                "IS": compute_is,
            },
            agent_reporters={
                "status": "status",
                "lat": lambda agent: agent.shape.centroid.x,
                "lon": lambda agent: agent.shape.centroid.y,
            },
        )
        logger.info("model initialized")

    def _create_new_agents(self, gdf: GeoDataFrame) -> None:
        """
        Create new agents not currently present in the model.

        Based on a given GeoDataFrame.
        """
        new_agents = []
        step_agents_ids = set(gdf.index)
        current_agents_ids = set(self.schedule._agents.keys())
        new_agents_ids = list(step_agents_ids - current_agents_ids)
        new_gdf = gdf[gdf.index.isin(new_agents_ids)]
        for idx, row in new_gdf.iterrows():
            agent = PersonAgent(idx, self, row["geometry"])
            self.schedule.add(agent)
            new_agents.append(agent)

        self.grid.add_agents(new_agents)
        logger.info("new %f agents created", len(new_agents))

    def _init_infected(self) -> None:
        if isinstance(self.init_infected, List):
            selected_agents = [
                agent for agent in self.init_infected if agent in self.schedule.agents
            ]
            proportion = len(selected_agents) / len(self.init_infected)
            logger.info("init infected from list, with a proportion %f", proportion)
        else:
            selected_agents = self.random.choices(
                self.schedule.agents, k=self.init_infected
            )
        for agent in selected_agents:
            agent.status = Status.INFECTED

        logger.info("int %f agents infected", len(selected_agents))

    def step(self, gdf: GeoDataFrame) -> None:
        """Run one step of the model."""
        self._create_new_agents(gdf)
        if self.steps == 0:
            self._init_infected()
        self.schedule.step(gdf)
        self.grid._recreate_rtree()  # Recalculate spatial tree, agents are moving
        self.datacollector.collect(self)
        logger.info("model step %f executed", self.steps)
        self.steps += 1
        self.infections_step = 0  # reset infections per step


def compute_s(model: Model) -> int:
    """
    Compute suceptible.

    Parameters
    ----------
    model : Model
        Model to compute metrics from.
    Returns
    -------
    int
        amount of suceptible agents.
    """
    agents = len(
        [
            agent.status
            for agent in model.schedule.agents
            if agent.status == Status.SUSCEPTIBLE
        ]
    )
    return agents


def compute_i(model: Model) -> int:
    """
    Compute infected.

    Parameters
    ----------
    model : Model
        Model to compute metrics from.
    Returns
    -------
    int
        amount of infected agents.
    """
    agents = len(
        [
            agent.status
            for agent in model.schedule.agents
            if agent.status == Status.INFECTED
        ]
    )
    return agents


def compute_r(model: Model) -> int:
    """
    Compute Recovered.

    Parameters
    ----------
    model : Model
        Model to compute metrics from.
    Returns
    -------
    int
        amount of recovered agents.

    """
    agents = len(
        [
            agent.status
            for agent in model.schedule.agents
            if agent.status == Status.RECOVERED
        ]
    )
    return agents


def compute_d(model: Model) -> int:
    """
    Compute deaths.

    Parameters
    ----------
    model : Model
        Model to compute metrics from.
    Returns
    -------
    int
        amount of dead agents.

    """
    return model.deaths


def compute_is(model: Model) -> int:
    """
    Compute infections per step.

    Parameters
    ----------
    model : Model
        Model to compute metrics from.
    Returns
    -------
    int
        amount of new infected agents in a step.
    """
    return model.infections_step
