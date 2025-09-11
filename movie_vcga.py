#!/usr/bin/env python

from movie_problem import *


# define the multi-population
toolbox.register("populations", tools.initRepeat, list, lambda:toolbox.population(40), 20)


if __name__ == "__main__":
    import multiprocessing
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    import vcga
    pops = toolbox.populations()
    ind = tools.selBest(pops[0], 1)[0]
    manager.schedule(ind)
    manager.print_fitness()
    aga = vcga.AdaptiveGA(algorithms.eaSimple, epochs=4)
    pga = vcga.RandomParallelGA(aga, epochs=5, send_best=5) 
    pga(pops, toolbox, cxpb=0.7, mutpb=0.32, ngen=5, verbose=False)
    ind = pga.selBest(pops)
    manager.schedule(ind)
    manager.check()
    manager.print_fitness()
    manager.dumps()
    manager.plot()
    manager.print_criterion()
