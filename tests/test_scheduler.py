"""Scheduler tests."""

import pytest

from geocovid.scheduler import DataScheduler


def test_model_set_up():
    """Test model setup."""
    scheduler = DataScheduler()
    assert model.running is True
    assert model.schedule is None
    assert model.current_id == 0
    assert model.current_id + 1 == model.next_id()
    assert model.current_id == 1
    model.step()
