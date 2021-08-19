"""Model tests."""

import pytest

from geocovid.model import GeoCovidModel


def test_model_set_up():
    """Test model setup."""
    model = GeoCovidModel()
    assert model.running is True
    assert model.schedule is None
    assert model.current_id == 0
    assert model.current_id + 1 == model.next_id()
    assert model.current_id == 1
    model.step()


def test_model_create_new_agents():
    """Test agents creation."""
    model = GeoCovidModel()
    model._create_new_agents(gdf)
