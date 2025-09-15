
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
    open_time: str  # "08:00"
    close_time: str # "23:00"
    gold_time: str  # "19:00"
    date_start: str # "2025-09-15"
    date_end: str   # "2025-09-15"
    movies: List[Movie]
    halls: List[Hall]

# --------- API nhận JSON body ----------
@app.post("/convert")
def convert_data(data: RequestData):

    # with open('test.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)

    import datetime
    def to_timestamp(date_str, time_str):
        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return int(dt.timestamp())

    # Tạo danh sách ngày từ date_start đến date_end
    date_list = []
    start = datetime.datetime.strptime(data.date_start, "%Y-%m-%d")
    end = datetime.datetime.strptime(data.date_end, "%Y-%m-%d")
    delta = (end - start).days
    for i in range(delta + 1):
        d = start + datetime.timedelta(days=i)
        date_list.append(d.strftime("%Y-%m-%d"))

    movies = {
        str(movie.id): [movie.duration, movie.rating, movie.type, movie.title]
        for movie in data.movies
    }

    results = {}
    for date_str in date_list:
        START_TIME = to_timestamp(date_str, data.open_time)
        END_TIME = to_timestamp(date_str, data.close_time)
        gtime = to_timestamp(date_str, data.gold_time)

        halls = {
            str(hall.id): (hall.capacity, START_TIME, END_TIME, hall.max_showtimes, hall.name)
            for hall in data.halls
        }

        manager = Manager.from_data(halls, movies, gtime=gtime)
        Population = HOFPopulation[Individual]
        individuals = []
        for _ in range(50):
            try:
                ind = Individual(manager.initSchedule(), manager=manager)
                individuals.append(ind)
            except IndexError:
                # Nếu không đủ phim cho suất chiếu, bỏ qua cá thể này
                pass
        if not individuals:
            raise Exception("Không đủ phim cho số lượng suất chiếu yêu cầu!")
        pop = Population(individuals)
        pop.evolve()
        ind = pop.best_individual
        manager.schedule(ind)
        manager.print_fitness()

        manager.check_duplicate_showtimes()
        manager.dumps()
        pop.hall_of_fame.clear()
        # Ghi log schedule của ngày
        print(f"\nLịch chiếu ngày {date_str}:")
        print(manager.dumps_json())

        # Vẽ hình, tên file là ngày
        try:
            manager.plot(filename=f"{date_str}.png")
        except Exception as e:
            print(f"Plot error for {date_str}: {e}")

        results[date_str] = manager.dumps_json()

    return results

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


    # manager = Manager.from_data(halls, movies, gtime=gtime)
    # Population = HOFPopulation[Individual]


    # pop = Population([
    # Individual(manager.initSchedule(), manager=manager)
    #     for _ in range(5)
    # ])



    # pop.evolve()

    # ind = pop.best_individual

    # manager.schedule(ind)
    # # manager.print_fitness()

    # # manager.check()
    # manager.dumps()
    # # manager.plot()
    # # manager.print_criterion()

    # return manager.dumps_json()
