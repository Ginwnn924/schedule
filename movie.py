#!/usr/bin/env python

import json
from pyrimidine import HOFPopulation
from individual import Individual



from models.manager import Manager
from models.fitness import FitnessManager
# from models.chromosome import Chromosome
# data
with open('movies.json', 'r', encoding='utf-8') as f:
    movies = json.load(f)

halls = {
    '37756': (154, 1489111200, 1489158000, 1, 6, "Hall A"),
    '37757': (147, 1489111200, 1489158000, 1, 6, "Hall B"),
    '37758': (146, 1489111200, 1489158000, 1, 6, "Hall C"),
    '37755': (235, 1489111200, 1489158000, 1, 6, "Hall D"),
    '37759': (126, 1489111200, 1489158000, 1, 6, "Hall E"),
    '37762': (146, 1489111200, 1489158000, 1, 6, "Hall F"),
    '37754': (410, 1489111200, 1489158000, 1, 6, "Hall G"),
    '37761': (186, 1489111200, 1489158000, 1, 6, "Hall H"),
}




                           
if __name__ == '__main__':
    manager = Manager.from_data(halls, movies)
    print("Initial fitness:", manager)

    Population = HOFPopulation[Individual]

    # Khởi tạo quần thể, tiến hóa để tìm lịch chiếu tối ưu, in kết quả và vẽ biểu đồ

    individuals = [Individual(manager.initSchedule()) for _ in range(50)]
    pop = Population(individuals)
    for ind in individuals:
        ind.manager = manager

    pop.evolve()
    ind = pop.best_individual

    manager.schedule(ind)

    fitness_manager = FitnessManager(manager)
    fitness_manager.print_fitness()

    manager.check()
    manager.dumps()
    manager.plot()
    fitness_manager = FitnessManager(manager)
    fitness_manager.print_criterion()

    