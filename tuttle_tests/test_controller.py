#!/usr/bin/env python

"""Tests for `tuttle` package."""

import pytest

from tuttle import controller, preferences


def test_eval_time_planning():
    # TODO:
    pass


def test_instantiate_controller():
    """Test that the controller can be instantiated."""
    con = controller.Controller(in_memory=True, preferences=preferences.Preferences())
    assert con is not None