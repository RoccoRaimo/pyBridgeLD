"""
Tests for pyBridgeLD
"""

import pytest
import pyBridgeLD as pybld


def test_geometry():
    """
    Test for definition of bridge cross section geometry and beam distances
    """

    cw_width = 11.28 # m
    n_beams = 3 
    beam_spacing = 3.76 # m
    beam_cantilever_left = 1.88 # m
    beam_cantilever_right = 1.88 # m

    geom = pybld.geometry.Bridge_configuration(cw_width= cw_width, n_beams=n_beams, beam_spacing=beam_spacing, beam_cantilever_left=beam_cantilever_left, beam_cantilever_right=beam_cantilever_right)
    distances = geom.beam_distance

    control_distances = [-3.76, 0.0, 3.76]

    assert distances == pytest.approx(control_distances)