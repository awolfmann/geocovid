"""Geocovid Visualization server."""
from typing import Dict

from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule, TextElement
from mesa_geo.visualization.MapModule import MapModule
from mesa_geo.visualization.ModularVisualization import ModularServer

from geocovid.agent import PersonAgent, Status
from geocovid.constants import MAP_COORDS
from geocovid.model import GeoCovidModel


class InfectedText(TextElement):
    """Display a text count of how many steps have been taken."""

    def __init__(self):
        """Init Element."""
        super().__init__()

    def render(self, model):
        """Render text."""
        return "Steps: " + str(model.steps)


model_params = {
    "infection_prob": UserSettableParameter(
        "slider", "Infection Probability", 0.0005, 0.0005, 0.5, 0.0005
    ),
    "init_infected": UserSettableParameter(
        "slider", "Initial infected poblation", 100, 0, 1000, 10
    ),
    "exposure_distance": UserSettableParameter(
        "slider", "Exposure distance", 0.0001, 0.0, 1.0, 0.0001,
    ),
    "death_prob": UserSettableParameter(
        "slider", "Death Probability", 0.05, 0.0, 1.0, 0.05,
    ),
    "treatment_period": UserSettableParameter(
        "slider", "Treatment Period duration", 14, 0, 30, 1,
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
