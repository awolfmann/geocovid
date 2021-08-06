"""Geo Covid Model."""

from mesa.datacollection import DataCollector
from mesa import Model
from mesa_geo import GeoSpace

from geopandas import GeoDataFrame

from geocovid.agent import PersonAgent, Status
from geocovid.scheduler import DataScheduler


class GeoCovidModel(Model):
    """A model with some number of agents."""

    def __init__(self,
                 infection_prob,
                 death_prob,
                 treatment_period,
                 exposure_distance,
                 seed=None):
        """Model initialization."""
        self.schedule = DataScheduler(self)
        self.grid = GeoSpace()
        self.steps = 0
        self.infection_prob = infection_prob
        self.death_prob = death_prob
        self.treatment_period = treatment_period
        self.exposure_distance = exposure_distance
        self.deaths = 0
        self.running = True
        self.current_hour = None
        self.current_date = None

        self.datacollector = DataCollector(model_reporters={"S": compute_s,
                                                            "I": compute_i,
                                                            "R": compute_r,
                                                            "D": compute_d
                                                            },
                                           agent_reporters={"Status": "status",
                                                            "Position": "pos"}
                                           )
        print("model initialized")


    def create_new_agents(
        self,
        gdf: GeoDataFrame
        ):
        """
        Create new agents not currently present in the model.

        Based on a given GeoDataFrame.
        """
        new_agents = []
        step_agents_ids = set(gdf.index)
        current_agents_ids = set(self.schedule._agents.keys())
        new_agents_ids = list(step_agents_ids - current_agents_ids)
        new_gdf = gdf[gdf.index.isin(new_agents_ids)]
        for ix, r in new_gdf.iterrows():
            a = PersonAgent(ix, self, r['geometry'])
            self.schedule.add(a)
            new_agents.append(a)

        self.grid.add_agents(new_agents)
        print("new agents created")

    def step(self, gdf: GeoDataFrame):
        """Run one step of the model."""
        self.create_new_agents(gdf)
        self.schedule.step(gdf)
        self.grid._recreate_rtree()  # Recalculate spatial tree, agents are moving
        # self.datacollector.collect(self)


def compute_s(model: Model):
    """Compute suceptible."""
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.SUSCEPTIBLE])
    return agents


def compute_i(model: Model):
    """Compute infected."""
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.INFECTED])
    return agents


def compute_r(model: Model):
    """Compute Recovered."""
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.RECOVERED])
    return agents


def compute_d(model: Model):
    """Compute deaths."""
    # TO DO!
    return 0
