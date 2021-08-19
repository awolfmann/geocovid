"""Agent tests."""

import pytest
from shapely.geometry import Point

from geocovid.agent import PersonAgent


class TestAgentCreator(unittest.TestCase):
    def test_create_agent(self):
        AC = AgentCreator(agent_class=PersonAgent, agent_kwargs={"model": None})
        shape = Point(1, 1)
        agent = AC.create_agent(shape=shape, unique_id=0)
        assert isinstance(agent, PersonAgent)
        assert agent.shape == shape
        assert agent.model is None
