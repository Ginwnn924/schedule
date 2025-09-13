
import json
from models.manager import Manager
from pyrimidine import HOFPopulation
from individual import Individual
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

# # data
# with open('movies.json', 'r', encoding='utf-8') as f:
#     movies = json.load(f)

# START_TIME = 1489111200
# END_TIME   = 1489158000

# gtime = 1489147200
# gapub = 10

# halls = {
#     '37756': (154, 1489111200, 1489158000, 6, "Hall A"),
#     '37757': (147, 1489111200, 1489158000, 6, "Hall B"),
#     '37758': (146, 1489111200, 1489158000, 6, "Hall C"),
#     '37755': (235, 1489111200, 1489158000, 6, "Hall D"),
#     '37759': (126, 1489111200, 1489158000, 6, "Hall E"),
#     '37762': (146, 1489111200, 1489158000, 6, "Hall F"),
#     '37754': (410, 1489111200, 1489158000, 6, "Hall G"),
#     '37761': (186, 1489111200, 1489158000, 6, "Hall H"),
# }


app = FastAPI()


# --------- Định nghĩa schema ----------
class Movie(BaseModel):
    id: int
    duration: int
    rating: float
    type: int
    title: str

class Hall(BaseModel):
    id: int
    name: str
    capacity: int
    max_showtimes: int

class RequestData(BaseModel):
    open_time: int
    close_time: int
    gold_time: int
    movies: List[Movie]
    halls: List[Hall]

# --------- API nhận JSON body ----------
@app.post("/convert")
def convert_data(data: RequestData):

    # with open('test.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)

    # START_TIME = data['open_time']
    # END_TIME = data['close_time']
    # gtime = data['gold_time']

    # movies = {
    #     str(movie['id']): [movie['duration'], movie['rating'], movie['type'], movie['title']]
    #     for movie in data['movies']
    # }

    # halls = {
    #     str(hall['id']): (hall['capacity'], START_TIME, END_TIME, hall['max_showtimes'], hall['name'])
    #     for hall in data['halls']
    # }

    START_TIME = data.open_time
    END_TIME = data.close_time
    gtime = data.gold_time

    movies = {
        str(movie.id): [movie.duration, movie.rating, movie.type, movie.title]
        for movie in data.movies
    }

    halls = {
        str(hall.id): (hall.capacity, START_TIME, END_TIME, hall.max_showtimes, hall.name)
        for hall in data.halls
    }

    print(movies)
    print(halls)

    # with open('movies.json', 'r', encoding='utf-8') as f:
    #     movies = json.load(f)

    # START_TIME = 1489111200
    # END_TIME   = 1489158000

    # gtime = 1489147200

    # halls = {
    #     '37756': (154, 1489111200, 1489158000, 6, "Hall A"),
    #     '37757': (147, 1489111200, 1489158000, 6, "Hall B"),
    #     '37758': (146, 1489111200, 1489158000, 6, "Hall C"),
    #     '37755': (235, 1489111200, 1489158000, 6, "Hall D"),
    #     '37759': (126, 1489111200, 1489158000, 6, "Hall E"),
    #     '37762': (146, 1489111200, 1489158000, 6, "Hall F"),
    #     '37754': (410, 1489111200, 1489158000, 6, "Hall G"),
    #     '37761': (186, 1489111200, 1489158000, 6, "Hall H"),
    # }


    manager = Manager.from_data(halls, movies, gtime=gtime)
    Population = HOFPopulation[Individual]


    pop = Population([
    Individual(manager.initSchedule(), manager=manager)
        for _ in range(5)
    ])



    pop.evolve()

    ind = pop.best_individual

    manager.schedule(ind)
    # manager.print_fitness()

    # manager.check()
    manager.dumps()
    # manager.plot()
    # manager.print_criterion()

    return manager.dumps_json()
