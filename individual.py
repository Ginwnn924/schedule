from pyrimidine import BaseIndividual
from pyrimidine.deco import side_effect, fitness_cache
import numpy as np
from mutation import mutRandom
from random import random
from models.chromosome import Chromosome

@fitness_cache
class Individual(BaseIndividual):
    def __new__(cls, *args, **kwargs):
        # Ensure params['manager'] is always set
        if 'manager' not in kwargs or kwargs['manager'] is None:
            if 'params' in kwargs and 'manager' in kwargs['params']:
                kwargs['manager'] = kwargs['params']['manager']
        return super().__new__(cls)
    # Đại diện cho một cá thể (individual) trong quần thể tiến hóa

    element_class = Chromosome
    params = {'manager': None}


    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Always set manager from argument or params
        if manager is not None:
            self.manager = manager
            self.params['manager'] = manager
        else:
            self.manager = self.params.get('manager', None)

    def copy(self):
        # Ensure manager is preserved when copying
        new = super().copy()
        new.manager = self.manager
        new.params['manager'] = self.manager
        return new

    @side_effect
    def mutate(self):
        # Đột biến cá thể
        # Ensure manager is not None
        if self.manager is None:
            self.manager = self.params.get('manager', None)
        self[:] = mutRandom(self, self.manager, indpb1=0.15, indpb2=0.8)


    def cross(self, other):
        # Lai ghép hai cá thể
        s1 = set(h[0] for h in self)
        s2 = set(h[0] for h in other)
        if random() > 1/(len(s1.symmetric_difference(s2))+1):
            child = super().cross(other)
            # Ensure manager is not None
            if getattr(child, 'manager', None) is None:
                child.manager = self.manager
                child.params['manager'] = self.manager
            return child
        else:
            return self.copy()

    def _fitness(self):
        # Tính toán fitness cho cá thể
        self.manager.schedule(self)
        return np.dot((50, 20, 2, 1), self.manager.fitness())

    @property
    def fitness(self):
        return self._fitness()
