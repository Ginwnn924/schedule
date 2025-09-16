import numpy as np
from helper import stamp2str
from scipy import stats
import uuid
class Hall:
    # Đại diện cho một phòng chiếu, chứa thông tin id, số ghế, thời gian, loại, tên, danh sách phim
    '''Hall has 6 (principal) propteries

    id_: id 
    seat: seat
    start: start
    last: last
    type_: type
    '''

    def __init__(self, id_, seatn, start, last, type_=6, name=None):
        # Khởi tạo đối tượng Hall với các thuộc tính cơ bản
        if isinstance(id_, uuid.UUID):
            self.id_ = id_
        else:
            self.id_ = uuid.UUID(str(id_))
        self.seatn = seatn
        self.start = start
        self.last = last
        self.type_ = type_
        self.name = name
        self.movies = []
        self.admission = None
        self.manager = None
        self.min_interval = 300

    @staticmethod
    def from_db(data):
        return Hall(id_=data[0], seatn=data[2], type_=data[3])

    def __getitem__(self, key):
        for m in self.movies:
            if m.id_ == key:
                return m

    def __str__(self):
        return 'hall_%s'%str(self.id_)

    def __repr__(self):
        return 'hall %s (%d)'%(str(self.id_), self.seatn)

    def random(self):
        AM = self.admission
        if AM is None:
            p = np.array([m.hot for m in self.manager.movies])
            M = stats.rv_discrete(name='movie', values=(np.arange(len(self.manager.movies)), p / np.sum(p)))
        else:
            p = np.array([self.manager.movies[k].hot for k in AM])
            M = stats.rv_discrete(name='movie', values=(AM, p / np.sum(p)))
        return M.rvs(size=1)[0]

    def dumps(self):
        # In ra thông tin phòng chiếu và các phim được chiếu trong phòng
        print(f'Phòng: {self.name} ({str(self.id_)})')
        for m in self.movies:
            if m.start <= self.last:
                print(f'  Phim: {m.name} ({str(m.id_)}) | Thời gian: {stamp2str(m.start)} - {stamp2str(m.end)}')

    def insert(self, i, movie, t=0):
        # Chèn một phim vào vị trí i trong danh sách phim của phòng
        self.movies.insert(i, movie)
        if i == 0:
            movie.start = movie.start + t
            self.movies[i+1].start += movie.length + t
        else:
            movie.start = self.movies[i-1].start + self.min_interval + t
            self.movies[i+1].start += movie.length + self.min_interval + t
        if self.movies[i+2].start - self.movies[i+1].end < self.min_interval:
            self.movies[i+1].start = self.movies[i].end + self.min_interval
        else:
            return
        for k in range(i+1, len(self.movies)-1):
            if self.movies[k+1].start - self.movies[k].end < self.min_interval:
                self.movies[k+1].start = self.movies[k].end + self.min_interval
            else:
                return

    def append(self, movie, t=0):
        # Thêm một phim vào cuối danh sách phim của phòng
        if self.movies:
            movie.start = self.movies[-1].end + t + self.min_interval
        else:
            movie.start = self.start + t
        self.movies.append(movie)

    def count(self):
        # Đếm số lần chiếu của từng phim trong phòng
        # count movies in a hall
        dict_ = {}
        for m in self.movies:
            if m.id_ in dict_:
                dict_[m.id_] += 1
            else:
                dict_.update({m.id_:1})
        return dict_

    def dist(self, other):
        # Tính khoảng cách thời gian giữa các phim chiếu ở hai phòng khác nhau
        k = 0
        d2 = d1 = 2100
        movies1 = [m for m in self.movies if m.start <= self.last]
        movies2 = [m for m in other.movies if m.start <= other.last]
        for m in movies1:
            for l, mm in enumerate(movies2[k:]):
                d = mm.start - m.start
                if d <= -2100:
                    k = l + 1
                    continue
                else:
                    if d <= 2100:
                        if m.id_ == mm.id_:
                            d1 = min(abs(d), d1)
                        else:
                            d2 = min(abs(d), d2)
                        k = l + 1
                    else:
                        k = l
                    break
        return d1, d2

