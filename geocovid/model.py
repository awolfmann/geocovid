"""Geo Covid Model."""
import logging

from mesa.datacollection import DataCollector
from mesa import Model
from mesa_geo import GeoSpace

from geopandas import GeoDataFrame

from geocovid.agent import PersonAgent, Status
from geocovid.scheduler import DataScheduler

logger = logging.getLogger(__name__)


class GeoCovidModel(Model):
    """A model with some number of agents."""

    def __init__(self,
                 infection_prob: float,
                 death_prob: float,
                 treatment_period: int,
                 exposure_distance: float,
                 init_infected: int,
                 seed: int = None
                 ):
        """Model initialization."""
        self.schedule = DataScheduler(self)
        self.grid = GeoSpace()
        self.infection_prob = infection_prob
        self.death_prob = death_prob
        self.treatment_period = treatment_period
        self.exposure_distance = exposure_distance
        self.init_infected = init_infected
        self.steps = 0
        self.deaths = 0
        self.running = True
        self.current_hour = None
        self.current_date = None
        self.infections_step = 0

        self.datacollector = DataCollector(model_reporters={"S": compute_s,
                                                            "I": compute_i,
                                                            "R": compute_r,
                                                            "D": compute_d,
                                                            "IS": compute_is
                                                            },
                                           agent_reporters={"Status": "status",
                                                            "Position": "shape"}
                                           )
        logger.info("model initialized")

    def _create_new_agents(
        self, 
        # gdf: GeoDataFrame
        gdf
        ) -> None:
        """
        Create new agents not currently present in the model.

        Based on a given GeoDataFrame.
        """
        new_agents = []
        # step_agents_ids = set(gdf.index)
        step_agents_ids = set([i.id for i in gdf.select('id')
                                                .distinct()
                                                .collect()])
        current_agents_ids = set(self.schedule._agents.keys())
        new_agents_ids = list(step_agents_ids - current_agents_ids)
        new_gdf = gdf[gdf.id.isin(new_agents_ids)]
        # new_gdf = gdf[gdf.index.isin(new_agents_ids)]
        # for ix, r in new_gdf.iterrows():
        #    a = PersonAgent(ix, self, r['geometry'])
        for r in new_gdf.collect():
            a = PersonAgent(r['id'], self, r['geometry'])
            self.schedule.add(a)
            new_agents.append(a)

        self.grid.add_agents(new_agents)
        logger.info("new %f agents created" % len(new_agents))

    def _init_infected(self) -> None:
        selected_agents = self.random.choices(self.schedule.agents,
                                              k=self.init_infected)
        for a in selected_agents:
            a.status = Status.INFECTED

        logger.info("int %f agents infected" % len(selected_agents))

    def step(self, gdf: GeoDataFrame) -> None:
        """Run one step of the model."""
        self._create_new_agents(gdf)
        if self.steps == 0:
            self._init_infected()
        self.schedule.step(gdf)
        self.grid._recreate_rtree()  # Recalculate spatial tree, agents are moving
        self.datacollector.collect(self)
        logger.info("model step %f executed" % self.steps)
        self.steps += 1
        self.infections_step = 0  # reset infections per step


def compute_s(model: Model) -> int:
    """Compute suceptible."""
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.SUSCEPTIBLE])
    return agents


def compute_i(model: Model) -> int:
    """Compute infected."""
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.INFECTED])
    return agents


def compute_r(model: Model) -> int:
    """Compute Recovered."""
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.RECOVERED])
    return agents


def compute_d(model: Model) -> int:
    """Compute deaths."""
    return model.deaths


def compute_is(model: Model) -> int:
    """Compute infections per step."""
    return model.infections_step

