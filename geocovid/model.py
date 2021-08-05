"""Geo Covid Model."""

from mesa.datacollection import DataCollector
from mesa import Model
from mesa_geo import GeoSpace

from agent import PersonAgent
from scheduler import DataScheduler


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

        self.datacollector = DataCollector(model_reporters={"S": compute_S,
                                                            "I": compute_I,
                                                            "R": compute_R,
                                                            "D": compute_D},
                                           agent_reporters={"Status": "status",
                                                            "Position": "pos"}
                                           )


    def create_new_agents(self, gdf):
        """
        Create new agents not currently present in the model.

        Based on a given GeoDataFrame.
        """
        new_agents = []
        step_agents_ids = set(gdf['id'].unique())
        current_agents_ids = set(self.schedule._agents.keys())
        new_agents_ids = list(step_agents_ids - current_agents_ids)
        new_gdf = gdf[gdf['id'].isin(new_agents_ids)]
        for _, r in new_gdf.iterrows():
            a = PersonAgent(r['id'], self, r['geometry'])
            self.schedule.add(a)
            new_agents.append(a)

        self.grid.add_agents(new_agents)

    def step(self, gdf):
        """Run one step of the model."""
        self.create_new_agents(gdf)
        self.schedule.step(gdf)
        self.grid._recreate_rtree()  # Recalculate spatial tree, because agents are moving

        self.datacollector.collect(self)




def compute_S(model):
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.SUSCEPTIBLE])
    return agents


def compute_I(model):
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.INFECTED])
    return agents


def compute_R(model):
    agents = len([agent.status for agent in model.schedule.agents if agent.status == Status.RECOVERED])
    return agents


def compute_D(model):
    agents = model.num_agents - len(model.schedule.agents)
    return  agents