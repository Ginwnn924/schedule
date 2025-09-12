from pyrimidine import BaseIndividual
from pyrimidine.deco import side_effect, fitness_cache
import numpy as np
from mutation import mutRandom
from random import random
from models.chromosome import Chromosome

@fitness_cache
class Individual(BaseIndividual):
    # Đại diện cho một cá thể (individual) trong quần thể tiến hóa

    element_class = Chromosome

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if (self.manager is None):
    #         raise ValueError("Manager must be provided")
    #     # self.manager = manager  # lưu manager vào cá thể



    @side_effect
    def mutate(self, manager):
        # Đột biến cá thể
        self[:] = mutRandom(self, manager, indpb1=0.15, indpb2=0.8)

    def cross(self, other):
        # Lai ghép hai cá thể
        s1 = set(h[0] for h in self)
        s2 = set(h[0] for h in other)
        if random() > 1/(len(s1.symmetric_difference(s2))+1):
            return super().cross(other)
        else:
            return self.copy()

    def _fitness(self, manager):
        # Tính toán fitness cho cá thể
        manager.schedule(self)
        return np.dot((50, 20, 2, 1), manager.fitness())