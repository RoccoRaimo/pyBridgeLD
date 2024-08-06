from dataclasses import dataclass

@dataclass
class Vehicle:
    """
    A data class that contains all the information about the considered vehicle in the transversal direction.

    Parameters:
    - veh_width: Width of the vehicle
    - veh_load_conc: A list of all the concentrated loads for the considered vehicle
    - veh_load_conc_spacing: A list of all the spacing between the concentrated loads, referred to the middle of vehicle
    - veh_load_dist: Distributed load value for the considered vehicle (0 as default)

    """
    veh_width: float
    veh_load_conc: list[float]
    veh_load_conc_spacing: list[float]
    veh_load_dist: float = 0
    
@dataclass
class TL_configuration:
    """
    A data class that defines a transversal Traffic Load Configuration.
    Arbitrary number of Vehicle objects can be used.

    Parameters:
    - veh_list: A list of pre-defined Vehicle objects
    - veh_ecc: A list of the Vehicle's eccentricity, measured from the middle of vehicle to the centerline of cross section
    """
    veh_list: list[Vehicle]
    veh_ecc: list[float]

    def tl_dist(self):
        """
        A function that takes the configuration of the distributed load and returns two list:
        - Traffic load weights for distributed loads (concentated loads obtained as veh_width * veh_load_dist)
        - Traffic load eccentricity for distributed loads (coincident with the veh_ecc list)
        """
        load_weights = []
        for vehicle in self.veh_list:
            load_weight = vehicle.veh_load_dist * vehicle.veh_width
            load_weights.append(load_weight)
        load_ecc = self.veh_ecc
        return load_weights, load_ecc
    
    def tl_conc(self):
        """
        A function that takes the configuration of the concentrated load and returns two list:
        - Traffic load weights for concentrated loads (a list of all the concentrated load, from left to right direction)
        - Traffic load eccentricity for concentrated loads (a list of all the eccentricity for the load weights)
        """
        load_weights = []
        load_ecc = []
        for idx, vehicle in enumerate(self.veh_list):
            for weight in vehicle.veh_load_conc:
                load_weights.append(weight)
            for ecc in vehicle.veh_load_conc_spacing:
                eccentricity = ecc + self.veh_ecc[idx]
                eccentricity_rounded = round(eccentricity, 2)
                load_ecc.append(eccentricity_rounded)
        return load_weights, load_ecc