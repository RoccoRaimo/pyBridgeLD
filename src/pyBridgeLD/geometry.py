from dataclasses import dataclass
    
#Definition of geometry Class

@dataclass
class Bridge_configuration:
    """
    A class that contains all the information to describe a configuration of a bridge (longitudinal and transversal directions)

    Parameters:
    -cw_width: width of carriageway
    -n_beams: number of beams
    -beam_spacing: spacing between beams, supposed constant
    -beam_cantilever_right: lenght of cantilever for the right side of deck (0 as default)
    -beam_cantilever_left: lenght of cantilever for the left side of deck (0 as default)
    -beam_length: beam total length
    -n_diaph: number of internal transversal diaphragms, the external diaphragms near supports are not considered (3 as default)
    -diaph_spacing: longitudinal spacing between diaphragms, supposed constant (0 as default)

    """
    cw_width: float
    n_beams: int
    beam_spacing: float
    beam_cantilever_right: float = 0
    beam_cantilever_left: float = 0
    beam_length: float = 0
    n_diaph: int = 3
    diaph_spacing: float = 0

    @property
    def beam_distance(self) -> list[float]:
        """
        Returns a list of floats containing the relative distance between i-th beam and the centerline of cross section's bridge.
        """
        if self.n_beams < 2:
            raise ValueError(f"Number of beams can't be {self.n_beams}, but at least > 2")
        elif self.n_beams == 2:
            dist_1 = self.beams_spacing/2
            dist_2 = self.beams_spacing/2 
            dist = [-dist_1, +dist_2]
        elif self.n_beams > 2 and (self.n_beams % 2) == 0:
            beam_idx_mid = int(round(self.n_beams/2, 0)) #index of middle beam
            dist = [] #outer accumulator
            for beam_idx in range(1, beam_idx_mid+1):
                dist_left = - round(self.beam_spacing/2 + self.beam_spacing * (beam_idx_mid - beam_idx), 2)
                dist.append(dist_left)
            for beam_idx in range(beam_idx_mid+1, (self.n_beams +1)):
                dist_right = - round(self.beam_spacing/2 + self.beam_spacing * (beam_idx_mid - beam_idx), 2)
                dist.append(dist_right)
        elif self.n_beams > 2 and (self.n_beams % 2) != 0:    
            beam_idx_mid = int(self.n_beams/2) + 1 #index of middle beam
            dist = [] #outer accumulator
            for beam_idx in range(1, beam_idx_mid+1):
                dist_left = - round(self.beam_spacing * (beam_idx_mid - beam_idx), 2)
                dist.append(dist_left)
            for beam_idx in range(beam_idx_mid+1, (self.n_beams +1)):
                dist_right = - round(self.beam_spacing * (beam_idx_mid - beam_idx), 2)
                dist.append(dist_right)
        return dist

