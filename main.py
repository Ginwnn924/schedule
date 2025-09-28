
import json
from models.manager import Manager
from pyrimidine import HOFPopulation
from individual import Individual
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import create_engine
import pandas as pd

app = FastAPI()


engine = create_engine(
    "postgresql+psycopg2://cineme_db:MgyzzizOWwpf7IoCqHM5n62ZnlGx1Qyn@dpg-d30j88ffte5s73efq5q0-a.singapore-postgres.render.com:5432/cineme_db_muz4"
)


# --------- Định nghĩa schema ----------
class Movie(BaseModel):
    id: UUID
    duration: int
    rating: float
    type: int
    title: str

class Hall(BaseModel):
    id: UUID
    name: str
    capacity: int
    maxShowtimes: int

class RequestData(BaseModel):
    openTime: str  # "08:00"
    closeTime: str # "23:00"
    goldenTime: str  # "19:00"
    startDate: str # "2025-09-15"
    endDate: str   # "2025-09-15"
    movies: List[Movie]
    hallId: UUID


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
    start = datetime.datetime.strptime(data.startDate, "%Y-%m-%d")
    end = datetime.datetime.strptime(data.endDate, "%Y-%m-%d")
    delta = (end - start).days
    hall_id = data.hallId
    max_showtimes = 6
    for i in range(delta + 1):
        d = start + datetime.timedelta(days=i)
        date_list.append(d.strftime("%Y-%m-%d"))

    movies = {
        str(movie.id): [movie.duration, movie.rating, movie.type, movie.title]
        for movie in data.movies
    }
    print(f"Movies: {movies}")

    query = """
        SELECT r.id, r.name, COUNT(s.id) AS capacity
        FROM rooms r
        LEFT JOIN seats s ON s.room_id = r.id
        WHERE r.theater_id = %(hall_id)s
        AND s.seat_type_id IS NOT NULL
        GROUP BY r.id, r.name
    """

    data_query = pd.read_sql(query, con=engine, params={"hall_id": hall_id})

    results = []
    for date_str in date_list:
        START_TIME = to_timestamp(str(date_str), str(data.openTime))
        END_TIME = to_timestamp(str(date_str), str(data.closeTime))
        gtime = to_timestamp(str(date_str), str(data.goldenTime))

        halls = {
            str(row["id"]): (row["capacity"], START_TIME, END_TIME, max_showtimes, row["name"])
            for _, row in data_query.iterrows()
        }

        manager = Manager.from_data(halls, movies, gtime=gtime)
        Population = HOFPopulation[Individual]
        individuals = []
        for _ in range(50):
            try:
                ind = Individual(manager.initSchedule(), manager=manager)
                individuals.append(ind)
            except IndexError:
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
        # print(f"\nLịch chiếu ngày {date_str}:")
        # print(manager.dumps_json())

        results.append({
            "date": date_str,
            "showtimes": manager.dumps_json()
        })

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
