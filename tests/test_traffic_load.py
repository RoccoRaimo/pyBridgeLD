"""
Tests for pyBridgeLD
"""

import pytest
import pyBridgeLD as pybld


def test_traffic_load():
    """
    Test for definition of vehicles and traffic load configuration
    """

    #Vehicle 1
    v_width_1 = 3.00 # m
    veh_load_conc_1 = [200, 200] # kN
    veh_load_conc_spacing_1 = [2.00] # m
    veh_load_dist_1 = 9 # kN/m2

    vehicle1 = pybld.traffic_load.Vehicle(veh_width=v_width_1,
                                          veh_load_conc=veh_load_conc_1,
                                          veh_load_conc_spacing= veh_load_conc_spacing_1,
                                          veh_load_dist=veh_load_dist_1)

    #Vehicle 2
    v_width_2 = 3.00 # m
    veh_load_conc_2 = [100, 100] # kN
    veh_load_conc_spacing_2 = [2.00] # m
    veh_load_dist_2 = 2.5 # kN/m2

    vehicle2 = pybld.traffic_load.Vehicle(veh_width=v_width_2,
                                          veh_load_conc=veh_load_conc_2,
                                          veh_load_conc_spacing= veh_load_conc_spacing_2,
                                          veh_load_dist=veh_load_dist_2)
    
    vehicles_ecc = [-1.00, -4.50] # m
    load_config = pybld.traffic_load.TL_configuration([vehicle1,vehicle2], veh_ecc=vehicles_ecc)

    load_weights_conc = [200, 200, 100, 100]
    load_ecc_conc = [-2.00, 0.00, -5.50, -3.50]

    load_weights_dist = [27.00, 7.50]
    load_ecc_dist = [-1.00, -4.50]

    assert load_config.tl_conc()[0]  == pytest.approx(load_weights_conc)
    assert load_config.tl_conc()[1]  == pytest.approx(load_ecc_conc)

    assert load_config.tl_dist()[0]  == pytest.approx(load_weights_dist)
    assert load_config.tl_dist()[1]  == pytest.approx(load_ecc_dist)
    