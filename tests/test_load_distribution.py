"""
Tests for pyBridgeLD
"""

import pytest
import pyBridgeLD as pybld


def test_singlevehicle():
    """
    Test for load distribution for single vehicle
    """
    #Bridge geometry
    bridge_geometry = pybld.geometry.Bridge_configuration(cw_width=11.28, 
                                                          n_beams=3, 
                                                          beam_spacing=3.76, 
                                                          beam_cantilever_left=1.88,
                                                          beam_cantilever_right=1.88)
    distance = bridge_geometry.beam_distance

    #Vehicle configuration
    vehicle = pybld.traffic_load.Vehicle(veh_width= 3.50, 
                                          veh_load_conc=[1], 
                                          veh_load_conc_spacing=[0], 
                                          veh_load_dist=0)
    
    traffic_load_configuration = pybld.traffic_load.TL_configuration(veh_list=[vehicle], 
                                                                     veh_ecc=[-3.50])
    
    load_distribution = pybld.load_distribution.LoadDistribution(cs = bridge_geometry, 
                                                                 tl_config = traffic_load_configuration)

    ki_conc = [0.799, 0.333, -0.132]

    assert load_distribution.courbon()[1]  == pytest.approx(ki_conc)


    