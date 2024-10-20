from pyBridgeLD import geometry as geom
from pyBridgeLD import traffic_load as tl
from dataclasses import dataclass
import pandas as pd
import plotly.express as px

import math

@dataclass
class LoadDistribution:
    """
    A data class to define a load distribution with one of the following assumption:

    - Courbon theory: 1) Diaphragms have infinite flexural stiffness;
                      2) Beams have infinite torsional stiffness;
                      3) Diaphragms are supposed as continuously distributed along the length of longitudinal beams (infinite number of diaphragms).

    - Engesser theory: 1) Diaphragms have infinite flexural stiffness;
                       2) Beams have infinite torsional stiffness.

    - Guyon-Massonnet-Bares theory: 1) Real grillage may be considered with an infinite continuos matrix having mean values of flexural and torsional stiffness;
                                    2) Harmonic analysis can be performed in longitudinal direction, so that means that a simple supported scheme is considered.

    Parameters:
    cs: geometry.Bridge_configuration
    tl_config: tl.TL_configuration
    """
    cs: geom.Bridge_configuration
    tl_config: tl.TL_configuration

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
            if item == 0:
                ecc_dist = 0
            else: 
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

    # def engesser(self):
    #     """
    #     The infinite number of diaphragms is removed, so the function takes n_diaph and beam_length and returns a load distribution.
        
    #     n_diaph: Number of internal diaphragms positioned in beam length

    #     Returns
    #     -------

    #     resultant: a list of total vertical reaction force and moment for concentrated and distributed loads

    #     """
    #     if self.cs.n_diaph == 0:
    #         raise ValueError(f"Number of internal diaphragms is less than 1, so Engesser theory cannot be used")
    #     elif self.cs.n_diaph > 3:
    #         raise ValueError(f"Number of internal diaphragms is greater than 3, not currently supported. Use Courbon theory!")
    #     else:
    #         # Calculate the polar inertia of the beams
    #         dist_square = [] #outer acc
    #         for distance in self.cs.beam_distance:
    #             dist_square.append(distance ** 2)
    #         polar_inertia = sum(dist_square)

    #         # Calculate the eccentricity of concentrated/distributed resultant load
    #         load_per_ecc_conc = [] # (load * eccentricity) for every concentrated loads
    #         for idx, item in enumerate(self.tl_config.tl_conc()[0]):
    #             product = self.tl_config.tl_conc()[0][idx] * self.tl_config.tl_conc()[1][idx]    
    #             load_per_ecc_conc.append(product)
    #         ecc_conc = sum(load_per_ecc_conc) / sum(self.tl_config.tl_conc()[0])
            
    #         load_per_ecc_dist = [] # (load * eccentricity) for every distritubed loads
    #         for idx, item in enumerate(self.tl_config.tl_dist()[0]):
    #             product = self.tl_config.tl_dist()[0][idx] * self.tl_config.tl_dist()[1][idx]    
    #             load_per_ecc_dist.append(product)
    #         ecc_dist = sum(load_per_ecc_dist) / sum(self.tl_config.tl_dist()[0])
            
    #         # Calculate the resultant forces/moments of concentrated/distributed definition for traffic_load      
    #         resultant_conc_force = round(sum(self.tl_config.tl_conc()[0]), 2)
    #         resultant_conc_moment = resultant_conc_force * ecc_conc
    #         resultant_dist_force = sum(self.tl_config.tl_dist()[0])
    #         resultant_dist_moment = round(resultant_dist_force * ecc_dist, 2)
    #         resultant = [resultant_conc_force, resultant_conc_moment, resultant_dist_force, resultant_dist_moment]

    #         # Calculate the repartition coefficients as per Courbon theory
    #         ki_conc = []
    #         for distance in self.cs.beam_distance:
    #             k_conc = round((1 / self.cs.n_beams ) + ecc_conc * distance / polar_inertia, 3)
    #             ki_conc.append(k_conc)

    #         ki_dist = []
    #         for distance in self.cs.beam_distance:
    #             k_dist = round((1 / self.cs.n_beams ) + ecc_dist * distance / polar_inertia, 3)
    #             ki_dist.append(k_dist)

    #         # Calculate the load per beam after the load distribution
    #         resultant_conc = []
    #         for k in ki_conc:
    #             r_conc = round(k * resultant_conc_force, 2)
    #             resultant_conc.append(r_conc)

    #         resultant_dist = []
    #         for k in ki_dist:
    #             r_dist = round(k * resultant_dist_force, 2)
    #             resultant_dist.append(r_dist)


    #         # if self.cs.n_diaph == 1:

    #         # elif self.cs.n_diaph == 2:

    #         # elif self.cs.n_diaph == 3:       

    #     return None


    def gmb(self, 
            E: list[float],
            nu: float, 
            I_l: list[float], 
            I_t: list[float]
            ):
        """
        Parameters
        -------

        E: Elasticity modulusus of beams, diaphragms and slab [E_beams, E_diaphragms, E_slab]
        nu: Poisson modulus
        I_l: Inertia of sections [I_l_beams, I_l_diaphragms]
        I_t: Torsional inertia of sections [I_t_beams, I_t_diaphragms]

        Returns
        -------

        k_dist: dictionary containing the repartition coefficient for all the beams, for every distributed load
        k_conc: dictionary containing the repartition coefficient for all the beams, for every concentrated load

        """
        b = self.cs.cw_width / 2
        l = self.cs.beam_length
        b_1 = self.cs.beam_spacing
        l_1 = self.cs.diaph_spacing

        G_beam = E[0] / (2*(1+nu))
        G_diaph = E[1] / (2*(1+nu))  

        #Flexural stiffness per unit
        rho_p = E[0] * I_l[0]  / b_1         
        rho_e = E[1] * I_l[1]  / l_1   

        #Torsional stiffness per unit
        gamma_p = G_beam * I_t[0]  / b_1      
        gamma_e = G_diaph * I_t[1]  / l_1  

        #Flexural parameter     
        theta = (b / l) * (rho_p / rho_e)**(1/4)
        
        #Torsional parameter
        alpha = (gamma_p + gamma_e) / (2 * (rho_p * rho_e)**(1/2))

        #Calculation of k_0, k_1 and k parameters for concentrated loads
        k_0_conc = {}
        k_1_conc = {}
        k_conc = {}
        for idx, load_conc in enumerate(self.tl_config.tl_conc()[0]):
            e_i = self.tl_config.tl_conc()[1][idx]

            k_0_conc_int = []
            k_1_conc_int = []
            k_conc_int = [] 
            for distance in self.cs.beam_distance:
                y_i = distance #i-th beam
                if e_i<=y_i:
                    y_i = -distance
                    e_i = -e_i

                #Calculation of k_0
                lambd = (math.pi / (self.cs.beam_length * math.sqrt(2))) * (rho_p / rho_e)**(1/4)

                a_low = 2 * math.cosh(lambd*(y_i+b)) * math.cos(lambd*(y_i+b))
                a_upp = math.sinh(2*lambd*b) * math.cos(lambd*(b+e_i)) * math.cosh(lambd*(b-e_i)) - math.sin(2*lambd*b) * math.cosh(lambd*(b + e_i)) * math.cos(lambd* (b-e_i))
                b_low = math.cosh(lambd*(y_i+b)) * math.sin(lambd*(y_i + b)) + math.sinh(lambd * (y_i + b)) * math.cos(lambd*(y_i+b))
                b_upp_1 =  math.sinh(2*lambd*b)*(math.sin(lambd*(b+e_i))*math.cosh(lambd*(b-e_i)) - math.cos(lambd*(b+e_i))*math.sinh(lambd*(b-e_i)))
                b_upp_2 =  math.sin(2*lambd*b)*(math.sinh(lambd*(b+e_i))*math.cos(lambd*(b-e_i)) - math.cosh(lambd*(b+e_i))*math.sin(lambd*(b-e_i)))

                k_0_conc_i = 2 * lambd * b * (a_low * a_upp + b_low * (b_upp_1+b_upp_2)) / (math.sinh(2*lambd*b)**2 - math.sin(2*lambd*b)**2)
            
                #Calculation of k_1
                psi = math.pi * e_i / b 
                beta = math.pi * y_i / b
                sigma = theta * math.pi
                csi = math.pi - abs(beta - psi)

                r_psi = math.cosh(theta * psi) * (sigma*math.cosh(sigma) - math.sinh(sigma)) - theta * psi * math.sinh(sigma) * math.sinh(theta*psi)
                r_beta = math.cosh(theta * beta) * (sigma*math.cosh(sigma) - math.sinh(sigma)) - theta * beta * math.sinh(sigma) * math.sinh(theta*beta)

                q_psi = math.sinh(theta * psi) * (2*math.sinh(sigma) - sigma*math.cosh(sigma)) - theta * psi * math.sinh(sigma) * math.cosh(theta*psi)
                q_beta = math.sinh(theta * beta) * (2*math.sinh(sigma) - sigma*math.cosh(sigma)) - theta * beta * math.sinh(sigma) * math.cosh(theta*beta)

                c = math.cosh(theta * csi) * (sigma * math.cosh(sigma) + math.sinh(sigma))
                d = theta*csi*math.sinh(sigma)*math.sinh(theta*csi)
                e = r_beta*r_psi / (3*math.sinh(sigma)*math.cosh(sigma)-sigma)
                f = q_beta*q_psi / (3*math.sinh(sigma)*math.cosh(sigma)+sigma)

                k_1_conc_i = sigma * (c - d + e + f) / (2*(math.sinh(sigma))**2)

                #Calculation of k for GMB theory
                k_conc_i = k_0_conc_i + (k_1_conc_i - k_0_conc_i) * alpha**(1/2)
                k_0_conc_int.append(k_0_conc_i)
                k_1_conc_int.append(k_1_conc_i)
                k_conc_int.append(k_conc_i)

            k_0_conc[f'dist_load_{idx+1}'] = k_0_conc_int
            k_1_conc[f'dist_load_{idx+1}'] = k_1_conc_int
            k_conc[f'dist_load_{idx+1}'] = k_conc_int

        #Calculation of k_0, k_1 and k parameters for distributed loads
        k_0_dist = {}
        k_1_dist = {}
        k_dist = {} 
        for idx, load_dist in enumerate(self.tl_config.tl_dist()[0]):
            e_i = self.tl_config.tl_dist()[1][idx]
            
            k_0_dist_int = []
            k_1_dist_int = []
            k_dist_int = []
            for distance in self.cs.beam_distance:
                y_i = distance #i-th beam
                if e_i<=y_i:
                    y_i = -distance
                    e_i = -e_i

                #Calculation of k_0
                lambd = (math.pi / (self.cs.beam_length * math.sqrt(2))) * (rho_p / rho_e)**(1/4)

                a_low = 2 * math.cosh(lambd*(y_i+b)) * math.cos(lambd*(y_i+b))
                a_upp = math.sinh(2*lambd*b) * math.cos(lambd*(b+e_i)) * math.cosh(lambd*(b-e_i)) - math.sin(2*lambd*b) * math.cosh(lambd*(b + e_i)) * math.cos(lambd* (b-e_i))
                b_low = math.cosh(lambd*(y_i+b)) * math.sin(lambd*(y_i + b)) + math.sinh(lambd * (y_i + b)) * math.cos(lambd*(y_i+b))
                b_upp_1 =  math.sinh(2*lambd*b)*(math.sin(lambd*(b+e_i))*math.cosh(lambd*(b-e_i)) - math.cos(lambd*(b+e_i))*math.sinh(lambd*(b-e_i)))
                b_upp_2 =  math.sin(2*lambd*b)*(math.sinh(lambd*(b+e_i))*math.cos(lambd*(b-e_i)) - math.cosh(lambd*(b+e_i))*math.sin(lambd*(b-e_i)))

                k_0_dist_i = 2 * lambd * b * (a_low * a_upp + b_low * (b_upp_1+b_upp_2)) / (math.sinh(2*lambd*b)**2 - math.sin(2*lambd*b)**2)
            
                #Calculation of k_1
                psi = math.pi * e_i / b 
                beta = math.pi * y_i / b
                sigma = theta * math.pi
                csi = math.pi - abs(beta - psi)

                r_psi = math.cosh(theta * psi) * (sigma*math.cosh(sigma) - math.sinh(sigma)) - theta * psi * math.sinh(sigma) * math.sinh(theta*psi)
                r_beta = math.cosh(theta * beta) * (sigma*math.cosh(sigma) - math.sinh(sigma)) - theta * beta * math.sinh(sigma) * math.sinh(theta*beta)

                q_psi = math.sinh(theta * psi) * (2*math.sinh(sigma) - sigma*math.cosh(sigma)) - theta * psi * math.sinh(sigma) * math.cosh(theta*psi)
                q_beta = math.sinh(theta * beta) * (2*math.sinh(sigma) - sigma*math.cosh(sigma)) - theta * beta * math.sinh(sigma) * math.cosh(theta*beta)

                c = math.cosh(theta * csi) * (sigma * math.cosh(sigma) + math.sinh(sigma))
                d = theta*csi*math.sinh(sigma)*math.sinh(theta*csi)
                e = r_beta*r_psi / (3*math.sinh(sigma)*math.cosh(sigma)-sigma)
                f = q_beta*q_psi / (3*math.sinh(sigma)*math.cosh(sigma)+sigma)

                k_1_dist_i = sigma * (c - d + e + f) / (2*(math.sinh(sigma))**2)

                #Calculation of k for GMB theory
                k_dist_i = k_0_dist_i + (k_1_dist_i - k_0_dist_i) * alpha**(1/2)
                k_0_dist_int.append(k_0_dist_i)
                k_1_dist_int.append(k_1_dist_i)
                k_dist_int.append(k_dist_i)

            k_0_dist[f'conc_load_{idx+1}'] = k_0_dist_int
            k_1_dist[f'conc_load_{idx+1}'] = k_1_dist_int
            k_dist[f'conc_load_{idx+1}'] = k_dist_int

        #Create the dataframe to visualize the repartition coefficient for every single load
        df_conc = pd.DataFrame(data=k_conc)
        df_dist = pd.DataFrame(data=k_dist)
        df = df_conc.join(df_dist)
        df.index= df.index + 1
        df_t = df.transpose()
        return df_t

    def gmb_plot(self):
        """
        Plot the results of the Guyon-Massonnet-Bares load distribution

        Returns
        -------
        None.
        """
        distance = self.cs.beam_distance
        # ki_conc = self.courbon()[1]
        # d = { 'distance' : distance, 'k': ki_conc}
        df = self.gmb
        fig = px.line(data_frame=df)
        # , x='distance', y='k',
        #              color='k', color_continuous_scale='Sunsetdark', opacity=0.7, text_auto='.3f')
        # fig.update_traces(textfont_size=10, textangle=0, textposition='outside', cliponaxis=False)
        fig.show()