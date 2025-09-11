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




    def _fitness(self):
        if self.manager is None:
            raise ValueError("Manager chưa được gán!")
        self.manager.schedule(self)
        return np.dot((50, 20, 2, 1), self.manager.fitness())


    @side_effect
    def mutate(self, movien, halln):
        self[:] = mutRandom(self, movien=movien, halln=halln)

    def cross(self, other):
        # Lai ghép hai cá thể
        s1 = set(h[0] for h in self)
        s2 = set(h[0] for h in other)
        if random() > 1/(len(s1.symmetric_difference(s2))+1):
            return super().cross(other)
        else:
            return self.copy()