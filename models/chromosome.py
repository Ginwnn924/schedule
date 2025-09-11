from random import randint
import copy
import numpy as np

class Chromosome(list):
    # Đại diện cho một cá thể (chromosome) trong giải thuật tiến hóa

    def copy(self, type_=None):
        # Tạo bản sao của chromosome
        return copy.deepcopy(self)

    def cross(self, other):
        # Lai ghép hai chromosome
        k = randint(1, len(self)-1)
        return self.__class__(np.concatenate((self[:k], other[k:]), axis=0))