import numpy as np
from random import random, randint
from deap import tools
from constant import GAPUP as gapub

def mutRandom(individual, movien, halln, indpb1=0.15, indpb2=0.8):
    ts = np.random.permutation(gapub)
    for k, hall in enumerate(individual):
        hall[0] = ts[k]
    for k, hall in enumerate(individual):
        if random() < indpb1:
            for i in range(1, len(hall), 2):
                if random() < indpb2:
                    if random() < 0.7:
                        if hall[i] == 0:
                            hall[i] += 1
                        else:
                            hall[i] -= 1
                    else:
                        if hall[i] == movien:
                            hall[i] -= 1
                        else:
                            hall[i] += 1
        else:
            for i in range(2, len(hall)-1, 2):
                if random() < indpb2:
                    hall[i] = np.random.choice([t for t in range(gapub) if t != hall[i]])
        h = randint(0, halln-2)
        if random() < 0.3:
            individual[h], individual[h+1] = individual[h+1], individual[h]
        else:
            individual[h], individual[h+1] = tools.cxTwoPoint(individual[h+1], individual[h])
    return individual
