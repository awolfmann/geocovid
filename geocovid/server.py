"""Geocovid Visualization server."""
from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from mesa_geo.visualization.MapModule import MapModule
from geocovid.model import GeoCovidModel
from geocovid.agent import PersonAgent, Status
from typing import Dict


class InfectedText(TextElement):
    """Display a text count of how many steps have been taken."""

    def __init__(self):
        pass

    def render(self, model):
        return "Steps: " + str(model.steps)


model_params = {
    "infection_prob": UserSettableParameter(
        "slider", "Infection Probability",
        0.0005,
        0.0005,
        0.5,
        0.0005
    ),
    "init_infected": UserSettableParameter(
        "slider", "Initial infected poblation", 100, 0, 1000, 10
    ),
    "exposure_distance": UserSettableParameter(
        "slider", "Exposure distance",
        0.0001,
        0.0,
        1.0,
        0.0001,
    ),
    "death_prob": UserSettableParameter(
        "slider", "Death Probability",
        0.05,
        0.0,
        1.0,
        0.05,
    ),
    "treatment_period": UserSettableParameter(
        "slider", "Treatment Period duration",
        14,
        0,
        30,
        1,
    ),

}


def infected_draw(agent: PersonAgent) -> Dict:
    """Portrayal Method for canvas."""
    portrayal = dict()
    portrayal["radius"] = "2"
    if agent.status == Status.INFECTED:
        portrayal["color"] = "Red"
    elif agent.status == Status.SUSCEPTIBLE:
        portrayal["color"] = "Green"
    elif agent.status == Status.RECOVERED:
        portrayal["color"] = "Blue"

    return portrayal

MAP_COORDS = [-34.5, -58.5]

infected_text = InfectedText()
map_element = MapModule(infected_draw, MAP_COORDS, 10, 700, 700)
infected_chart = ChartModule(
    [
        {"Label": "Infected", "Color": "Red"},
        {"Label": "Susceptible", "Color": "Green"},
        {"Label": "Recovered", "Color": "Blue"},
    ]
)
server = ModularServer(
    GeoCovidModel,
    [map_element, infected_text, infected_chart],
    "Basic agent-based SIR model",
    model_params,
)
server.launch()
