import geometry as geom
import traffic_load as tl
from dataclasses import dataclass
import pandas as pd
import plotly.express as px

@dataclass
class LoadDistribution:
    """
    A data class to define a load distribution with one of the following assumption:

    - Courbon theory: 1) Diaphragms have infinite flexural stiffness;
                      2) Beams have infinite torsional stiffness;
                      3) Diaphragms are supposed as continuosly distributed along the length of longitudinal beams (infinite number of diaphragms).

    - Engesser theory: 1) Diaphragms have infinite flexural stiffness;
                       2) Beams have infinite torsional stiffness.

    - Guyon-Massonnet-Bares theory: 1) Real grillage may be considered with an infinite continuos matrix having mean values of flexural and torsional stiffness;
                                    2) Harmonic analysis can be performed in longitudinal direction, so that means that a simple supported scheme is considered.

    Parameters:
    cs: geometry.Bridge_cross_section type
    traffic_load: trafficload.Vehicle type
    """
    cs: geom.Bridge_configuration
    tl_config: tl.TL_Configuration

    def courbon(self):
        """
        The function returns a load distribution for every beam of the cross section, using the Courbon theory.

        Returns
        -------
        [resultant, ki_conc , ki_dist, resultant_conc, resultant_dist]

        resultant: a list of total vertical reaction force and moment for concentrated and distributed loads
        ki_conc: repartition coefficient for i-th beam referred to concentrated loads
        ki_dist: repartition coefficient for i-th beam referred to distributed loads
        resultant_conc: resultant vertical force for i-th beam referred to concentrated loads
        resultant_dist: resultant vertical distributed load for i-th beam referred to distributed loads
        """
        if self.cs.n_diaph == 0:
            raise ValueError(f"Number of internal diaphragms is less than 1, so Courbon theory cannot be used")
        else:
            # Calculate the polar inertia of the beams
            dist_square = [] #outer acc
            for distance in self.cs.beam_distance:
                dist_square.append(distance ** 2)
            polar_inertia = sum(dist_square)

            # Calculate the eccentricity of concentrated/distributed resultant load
            load_per_ecc_conc = [] # (load * eccentricity) for every concentrated loads
            for idx, item in enumerate(self.tl_config.tl_conc()[0]):
                product = self.tl_config.tl_conc()[0][idx] * self.tl_config.tl_conc()[1][idx]    
                load_per_ecc_conc.append(product)
            ecc_conc = sum(load_per_ecc_conc) / sum(self.tl_config.tl_conc()[0])
            
            load_per_ecc_dist = [] # (load * eccentricity) for every distritubed loads
            for idx, item in enumerate(self.tl_config.tl_dist()[0]):
                product = self.tl_config.tl_dist()[0][idx] * self.tl_config.tl_dist()[1][idx]    
                load_per_ecc_dist.append(product)
            ecc_dist = sum(load_per_ecc_dist) / sum(self.tl_config.tl_dist()[0])
            
            # Calculate the resultant forces/moments of concentrated/distributed definition for traffic_load      
            resultant_conc_force = round(sum(self.tl_config.tl_conc()[0]), 2)
            resultant_conc_moment = resultant_conc_force * ecc_conc
            resultant_dist_force = sum(self.tl_config.tl_dist()[0])
            resultant_dist_moment = round(resultant_dist_force * ecc_dist, 2)
            resultant = [resultant_conc_force, resultant_conc_moment, resultant_dist_force, resultant_dist_moment]

            # Calculate the repartition coefficients
            ki_conc = []
            for distance in self.cs.beam_distance:
                k_conc = round((1 / self.cs.n_beams ) + ecc_conc * distance / polar_inertia, 3)
                ki_conc.append(k_conc)

            ki_dist = []
            for distance in self.cs.beam_distance:
                k_dist = round((1 / self.cs.n_beams ) + ecc_dist * distance / polar_inertia, 3)
                ki_dist.append(k_dist)

            # Calculate the load per beam after the load distribution
            resultant_conc = []
            for k in ki_conc:
                r_conc = round(k * resultant_conc_force, 2)
                resultant_conc.append(r_conc)

            resultant_dist = []
            for k in ki_dist:
                r_dist = round(k * resultant_dist_force, 2)
                resultant_dist.append(r_dist)

        return resultant, ki_conc , ki_dist, resultant_conc, resultant_dist
    
    def courbon_plot(self):
        """
        Plot the results of the Corboun load distribution

        Returns
        -------
        None.
        """
        distance = self.cs.beam_distance
        ki_conc = self.courbon()[1]
        d = { 'distance' : distance, 'k': ki_conc}
        df = pd.DataFrame(data=d)
        fig = px.bar(data_frame=df, x='distance', y='k',
                    color='k', color_continuous_scale='Sunsetdark', opacity=0.7, text_auto='.3f')
        fig.update_traces(textfont_size=10, textangle=0, textposition='outside', cliponaxis=False)
        fig.show()



    def engesser(self):
        """
        The infinite number of diaphragms is removed, so the function takes n_diaph and beam_length and returns a load distribution.
        
        n_diaph: Number of internal diaphragms positioned in beam length

        Returns
        -------

        resultant: a list of total vertical reaction force and moment for concentrated and distributed loads

        """
        if self.cs.n_diaph == 0:
            raise ValueError(f"Number of internal diaphragms is less than 1, so Engesser theory cannot be used")
        elif self.cs.n_diaph > 3:
            raise ValueError(f"Number of internal diaphragms is greater than 3, not currently supported. Use Courbon theory!")
        else:
            # Calculate the polar inertia of the beams
            dist_square = [] #outer acc
            for distance in self.cs.beam_distance:
                dist_square.append(distance ** 2)
            polar_inertia = sum(dist_square)

            # Calculate the eccentricity of concentrated/distributed resultant load
            load_per_ecc_conc = [] # (load * eccentricity) for every concentrated loads
            for idx, item in enumerate(self.tl_config.tl_conc()[0]):
                product = self.tl_config.tl_conc()[0][idx] * self.tl_config.tl_conc()[1][idx]    
                load_per_ecc_conc.append(product)
            ecc_conc = sum(load_per_ecc_conc) / sum(self.tl_config.tl_conc()[0])
            
            load_per_ecc_dist = [] # (load * eccentricity) for every distritubed loads
            for idx, item in enumerate(self.tl_config.tl_dist()[0]):
                product = self.tl_config.tl_dist()[0][idx] * self.tl_config.tl_dist()[1][idx]    
                load_per_ecc_dist.append(product)
            ecc_dist = sum(load_per_ecc_dist) / sum(self.tl_config.tl_dist()[0])
            
            # Calculate the resultant forces/moments of concentrated/distributed definition for traffic_load      
            resultant_conc_force = round(sum(self.tl_config.tl_conc()[0]), 2)
            resultant_conc_moment = resultant_conc_force * ecc_conc
            resultant_dist_force = sum(self.tl_config.tl_dist()[0])
            resultant_dist_moment = round(resultant_dist_force * ecc_dist, 2)
            resultant = [resultant_conc_force, resultant_conc_moment, resultant_dist_force, resultant_dist_moment]

            # Calculate the repartition coefficients as per Courbon theory
            ki_conc = []
            for distance in self.cs.beam_distance:
                k_conc = round((1 / self.cs.n_beams ) + ecc_conc * distance / polar_inertia, 3)
                ki_conc.append(k_conc)

            ki_dist = []
            for distance in self.cs.beam_distance:
                k_dist = round((1 / self.cs.n_beams ) + ecc_dist * distance / polar_inertia, 3)
                ki_dist.append(k_dist)

            # Calculate the load per beam after the load distribution
            resultant_conc = []
            for k in ki_conc:
                r_conc = round(k * resultant_conc_force, 2)
                resultant_conc.append(r_conc)

            resultant_dist = []
            for k in ki_dist:
                r_dist = round(k * resultant_dist_force, 2)
                resultant_dist.append(r_dist)


            # if self.cs.n_diaph == 1:

            # elif self.cs.n_diaph == 2:

            # elif self.cs.n_diaph == 3:       

        return None


    def gmb(self, 
            E: list[float],
            nu: float, 
            I_l: list[float], 
            I_t: list[float]):
        """

        E: Elasticity modulusus of beams, diaphragms and slab [E_beams, E_diaphragms, E_slab]
        nu: Poisson modulus
        I_l: Inertia of sections [I_l_beams, I_l_diaphragms]
        I_t: Torsional inertia of sections [I_t_beams, I_t_diaphragms]
        """
        b = self.cs.cw_width / 2
        l = self.cs.beam_length
        b_t = self.cs.beam_spacing

        G_beam = E[0] / (2*(1+nu))
        G_diaph = E[1] / (2*(1+nu))  

        #Flexural stiffness per unit
        D_x_beam = E[0] * I_l[0]  / l         
        D_x_diaph = E[1] * I_l[1]  / b_t   

        #Torsional stiffness per unit
        D_y_beam = G_beam * I_t  / b_t      
        D_y_diaph = G_diaph * I_t  / l  

        #Flexural parameter     
        theta = (b / l) * (D_x_beam / D_y_beam)^(1/4)
        
        #Torsional parameter
        alpha = (D_y_beam + D_y_diaph) / (2 * (D_x_beam * D_x_diaph)^(1/2))

        #Calculation of k_0, k_1 and k parameters

        
        return
