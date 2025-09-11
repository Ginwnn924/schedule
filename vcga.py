#!/usr/bin/env python

'''Variants of canonical genetic algorithm
'''

import copy
from random import randint
import numpy as np

from deap import tools


class VCGA:
    '''AdaptiveGA has 3 (principal) propteries
    algorithm: an genetic algorithm
    epochs: iterations of the algorithm
    groups: groups [2]
    '''

    def __init__(self, algorithm):
        self.algorithm = algorithm

    def __call__(self, population, toolbox, *args, **kwargs):
        raise NotImplementedError('subclasses of VCGA must provide a __call__() method')

    def get_cxpb(self, population):
        pass

    def get_mutpb(self, population):
        pass

    def get_groups(self, population):
        pass

    def select(self, population, N, method=tools.selBest):
        return method(population, N)

    def get_fitness(self, population):
        return [pop.fitness.values for pop in population]


class BaseAdaptiveGA(VCGA):
    '''BaseAdaptiveGA: base class for adpative ga
    algorithm: an genetic algorithm
    epochs: iterations of the algorithm
    groups: groups [2]
    '''

    def __init__(self, algorithm, epochs=5):
        super().__init__(algorithm)
        self.epochs = epochs

    def __call__(self, population, toolbox, cxpb=0.5, mutpb=0.2, *args, **kwargs):
        cxpb0, mutpb0 = cxpb, mutpb
        for _ in range(self.epochs):
            self.algorithm(population, toolbox, cxpb=cxpb, mutpb=mutpb, *args, **kwargs)
            cxpb, mutpb = self.update_cxmutpb(cxpb0, mutpb0, population)

    def get_cxpb_mutpb(self, cxpb0, r):
        raise NotImplementedError


class AdaptiveGA(BaseAdaptiveGA):
    '''AdaptiveGA < BaseAdaptiveGA
    '''

    cxpbmax = 0.6
    mutpbmax = 0.4

    def update_cxmutpb(self, cxpb0, mutpb0, population):
        r = self.coef(population)
        return self.get_cxpb(cxpb0, r), self.get_mutpb(mutpb0, r)

    def coef(self, population):
        # adaptive coefficents
        vs = self.get_fitness(population)
        N = len(population)
        va = np.array(list(map(np.mean, vs)))
        vmax = np.array(list(map(np.max, vs)))
        vmin = np.array(list(map(np.min, vs)))
        return np.mean((va-vmin) / max(vmax-vmin + 0.0001))

    def get_cxpb(self, cxpb0, r):
        return (1 - r) * self.cxpbmax + r * cxpb0

    def get_mutpb(self, mutpb0, r):
        return (1 - r) * self.mutpbmax + r * mutpb0


class HierarchicGA(VCGA):
    '''HierarchicGA has 2 (principal) propteries
    algorithm: an genetic algorithm
    groupn: groupn
    '''

    def __init__(self, algorithm, groupn=10):
        super().__init__(algorithm)
        self.groupn = groupn

    def generate_populations(self, creator):
        return toolbox.register("populations", tools.initRepeat, list, creator, self.groupn)

    def __call__(self, populations, toolbox, *args, **kwargs):
        toolbox = self.set_toolbox()
        for pop in populations:
            self.algorithm(pop, toolbox, *args, **kwargs)
        self.algorithm(populations, toolbox, *args, **kwargs)

    def mate(self, *args, **kwargs):
        raise NotImplementedError

    def mutate(self, *args, **kwargs):
        raise NotImplementedError

    def set_toolbox(self):
        toolbox = base.Toolbox()
        def evalfit(original):
            def f(pop):
                N = len(pop)
                vs = pop[0].fitness.values
                for ind in pop[1:]:
                    for k, v in enumerate(ind.fitness.values):
                        vs[k] += v
                return tuple(map(lambda x:x/N, vs))
            return f

        toolbox.decorate("evaluate", evalfit)
        toolbox.register("mate", self.mate)
        toolbox.register("mutate", self.mutate, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        return toolbox


import threading

class BaseParallelGA(VCGA):
    '''BaseParallelGA: base class for parallel GA
    algorithm: an genetic algorithm
    epochs: iterations of the algorithm
    send_best: send best [5]
    '''

    def __init__(self, algorithm, epochs, send_best=5):
        super().__init__(algorithm)
        self.epochs = epochs
        self.send_best = send_best

    def __call__(self, populations, toolbox, *args, **kwargs):
        for _ in range(self.epochs):
            self.evolute(populations, toolbox, *args, **kwargs)
            self.migrate(populations)

    def evolute(self, populations, toolbox, *args, **kwargs):
        #for pop in populations:
        #    self.algorithm(pop, toolbox, *args, **kwargs)
        threads = [threading.Thread(target=self.algorithm, args=(pop, toolbox)+args, kwargs=kwargs) for pop in populations]

        for t in threads:
            t.daemon = True
            t.start()
        for t in threads:
            t.join()

    def migrate(self, populations):
        raise NotImplementedError

    @classmethod
    def selBest(cls, populations):
        best_pop = [tools.selBest(pop, 1)[0] for pop in populations]
        return tools.selBest(best_pop, 1)[0]

    @classmethod
    def generate_populations(self, toolbox, creator, npop=5):
        # creator: create a population
        return toolbox.register("populations", tools.initRepeat, list, creator, self.npop)


def replace(lst, worst, best):
    for w in worst:
        if w in lst:
            lst.remove(w)
    lst.extend(best)


class NetParallelGA(BaseParallelGA):
    '''parallel ga with network topology
    '''

    def migrate(self, populations):
        for k, pop in enumerate(populations):
            best = tools.selBest(pop, self.send_best)
            for l, pop in enumerate(populations):
                if l !=  k:
                    worst = tools.selWorst(pop, self.send_best)
                    replace(pop, worst, best)

        
class RandomParallelGA(BaseParallelGA):
    '''parallel ga with network topology
    '''

    def migrate(self, populations):
        N = len(populations)
        for k, pop in enumerate(populations):
            best, worst = tools.selBest(pop, self.send_best), tools.selWorst(pop, self.send_best)
            l = randint(0, N-1)
            pop1 = populations[l]
            if l != k:
                best1, worst1 = tools.selBest(pop1, self.send_best), tools.selWorst(pop1, self.send_best)
                replace(pop, worst, best1)
                replace(pop1, worst1, best)


class ExchangeParallelGA(BaseParallelGA):
    '''parallel ga with network topology
    '''

    def migrate(self, populations):
        for k, pop in enumerate(populations[:-1]):
            best, worst = tools.selBest(pop, self.send_best), tools.selWorst(pop, self.send_best)
            for pop1 in populations[k+1:]:
                best1, worst1 = tools.selBest(pop1, self.send_best), tools.selWorst(pop1, self.send_best)
                replace(pop, worst, best1)
                replace(pop1, worst1, best)


class RingParallelGA(BaseParallelGA):
    '''parallel ga with network topology
    '''

    def migrate(self, populations):
        for k, pop in enumerate(populations[:-1]):
            best, worst = tools.selBest(pop, self.send_best), tools.selWorst(pop, self.send_best)
            pop1 = populations[k+1]
            best1, worst1 = tools.selBest(pop1, self.send_best), tools.selWorst(pop1, self.send_best)
            replace(pop1, worst1, best)
            replace(pop, worst, best1)
        pop = populations[-1]
        best, worst = tools.selBest(pop, self.send_best), tools.selWorst(pop, self.send_best)
        pop1 = populations[0]
        best1, worst1 = tools.selBest(pop1, self.send_best), tools.selWorst(pop1, self.send_best)
        replace(pop1, worst1, best)
        replace(pop, worst, best1)


class BaseMimeticGA(VCGA):
    '''BaseMimeticGA has 2 (principal) propteries
    algorithm: an genetic algorithm
    epochs: iterations of the algorithm
    '''

    def __init__(self, algorithm, epochs):
        super().__init__(algorithm)
        self.epochs = epochs

    def __call__(self, population, toolbox, *args, **kwargs):
        for _ in range(self.epochs):
            self.algorithm(population, toolbox, *args, **kwargs)
            self.local_search(population, toolbox)

    def local_search(self, population, toolbox):
        raise NotImplementedError


class MimeticGA(BaseMimeticGA):
    '''MimeticGA has 2 (principal) propteries
    algorithm: algorithm
    epochs: epochs'''

    def local_search(self, population, toolbox):
        pass


class BaseNeuralGA:
    '''BaseNeuralGA: Base class of neural ga
    algorithm: algorithm
    ann: ann
    epochs: epochs'''

    def __init__(self, algorithm, ann, epochs=10):
        super().__init__(algorithm)
        self.ann = ann
        self.epochs = epochs

    def __call__(self, population, toolbox, *args, **kwargs):
        # template of neural ga
        def evalfit(ind):
            return self.evaluate(ind),
        toolbox.register("evaluate", evalfit)
        for _ in range(self.epochs):
            pop, fit = self.select(population)
            if pop:
                self.train(pop, fit)
            self.algorithm(population, toolbox, *args, **kwargs)
            # self.modify(toolbox)

    def select(self):
        raise NotImplementedError

    def train(self, pop, fit, epochs=500):
        raise NotImplementedError

    def evaluate(self, ind):
        raise NotImplementedError

    def modify(self, toolbox):
        pass


class NeuralGA(BaseNeuralGA):
    '''NeuralGA < BaseNeuralGA
    '''

    lim = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.popdata = []
        self.fitdata = []

    @staticmethod
    def add_data(X, Y, X1, Y1):
        for x, y in zip(X1, Y1):
            if x not in X:
                X = np.concatenate((X, [x]))
                Y = np.concatenate((Y, [y]))
        n = X.shape[0]
        if n > NeuralGA.lim:
            return X[n-NeuralGA.lim:], Y[n-NeuralGA.lim:]
        else:
            return X, Y

    @staticmethod
    def append_data(x, y):
        if isinstance(x, np.ndarray):
            n = x.shape[0]
        else:
            n = len(x)
        if n == 0:
            return np.array([y])
        elif n + 1 > NeuralGA.lim:
            return np.concatenate((x[NeuralGA.lim-1-n:], [y]))
        else:
            return np.concatenate((x, [y]))

    # def select(self, population):
    #     # select pop
    #     pop = population[10:]
    #     fits = []
    #     inds = []
    #     for k, ind in enumerate(pop, 1):
    #         s = input('give fitness:')
    #         if s != '':
    #             fits.append(float(s))
    #             inds.append(ind)
    #     return inds, fits

    def train(self, pop, fit, epochs=500):
        popdata = np.array([ind for ind in pop])
        fitdata = np.array([[f] for f in fit])
        self.popdata = NeuralGA.add_data(self.popdata, popdata)
        self.fitdata = NeuralGA.add_data(self.fitdata, fitdata)
        self.ann.train(self.popdata, self.fitdata, epochs=epochs)

    def evaluate(self, ind):
        return self.ann.predict([ind])[0][0]


def purform(algorithm, pop, N=25, *args, **kwargs):
    values = 0
    inipop = copy.deepcopy(pop)
    for _ in range(N):
        pop = inipop
        algorithm(pop, *args, **kwargs)
        ind = tools.selBest(pop, 1)[0]
        values += np.array(ind.fitness.values)
    return values / N


def toolbox_purform(algorithm, toolbox, n=20, N=25, *args, **kwargs):
    values = 0
    for _ in range(N):
        pop = toolbox.population(n)
        algorithm(pop, toolbox, *args, **kwargs)
        ind = tools.selBest(pop, 1)[0]
        values += np.array(ind.fitness.values)
    return values / N
