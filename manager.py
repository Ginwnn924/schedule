import numpy as np
from models.hall import Hall
from models.movie import Movie
from constant import GTIME as gtime, GAPUP as gapub
from helper import mymin

class Manager:
    def __init__(self, halls, movies=None, sorted=True):
    # Khởi tạo đối tượng Manager, sắp xếp phòng và phim, tính toán các thông số ban đầu
        self.halls = halls
        for h in halls:
            h.manager = self
        self.movies = movies
        if sorted:
            self.halls.sort(key=lambda h:h.seatn, reverse=True)
            if movies:
                self.movies.sort(key=lambda h:h.hot, reverse=True)
                N = sum(h.type_ for h in self.halls) + len(self.halls) / 2
                for m in self.movies:
                    p = np.array([m.hot for m in self.movies])
                self.estimate = [int(k) for k in np.round(N * (p / np.sum(p)))]
        # count seat taking
        
        s = np.sum(np.sqrt(h.seatn) for h in self.halls)
        for h in self.halls:
            h.seat_rate = np.sqrt(h.seatn) / s

    @staticmethod
    def from_data(hall_data, movie_data=None):
        # Tạo đối tượng Manager từ dữ liệu phòng và phim (dạng dict)
        if movie_data:
            return Manager(
                [Hall(id_, *propteries) for id_, propteries in hall_data.items()],
                [Movie(id_, propteries[0], propteries[1], propteries[2], propteries[3]) for id_, propteries in movie_data.items()]
            )
        else:
            return Manager([Hall(id_, *propteries) for id_, propteries in hall_data.items()])

    @staticmethod
    def from_db(lst):
        return Manager([Hall.from_db(*args) for args in lst])

    
    def schedule(self, individual):
        # Sắp xếp lịch chiếu cho từng phòng dựa trên cá thể (individual) của giải thuật tiến hóa
        # individual.gmovies = {}
        for k, h in enumerate(self.halls):
            n = h.type_
            h.movies = [self.movies[i].copy() for i in individual[k][1:2*n:2]]
            times = individual[k][:2*n-1:2]
            h.movies[0].start = h.start + times[0] * 300
            for l, m in enumerate(h.movies[1:], start=1):
                m.start = h.movies[l-1].end + (times[l]+1) * 300
                if m.start > h.last:
                    h.movies = h.movies[:l]
                    break

                # if m.isgolden():
                #     individual.gmovies.update({k:l})


    def insert_into(self, j, k, t=None):
        # Chèn một phim vào phòng k tại thời điểm t
        if t is None:
            for time in range(gapub):
                flag = True
                for kk, h in enumerate(self.halls):
                    if kk != k:
                        for m in h.movies:
                            if time == m.start:
                                flag = False
                if flag:
                    t = time
        self.halls[k].insert(0, self.movies[j].copy(), t)

    def count(self):
        # Đếm số lần chiếu của từng phim trên toàn bộ hệ thống
        '''count movies
        dict_ : {id_: number}
        '''

        dict_ = {}
        S = 0
        for h in self.halls:
            S += len(h.movies)
            for m in h.movies:
                if m.start <= h.last:
                    if m.id_ in dict_:
                        dict_[m.id_] += 1
                    else:
                        dict_.update({m.id_:1})

        for id_ in dict_:
            dict_[id_] /= S
        return dict_
    
    def fitness(self):
        # Tính toán các tiêu chí đánh giá lịch chiếu (fitness)
        return self.time_interval(), self.check_rate(), self.total_hot(), self.check_time()

    def check(self):
        # In ra các thông số kiểm tra chất lượng lịch chiếu
        d1, d2 = self.check_interval()
        print('''
Minimum time interval: %.4f+%.4f;
Similarity between popularity and show times: %.4f;
Total popularity (prime time): %.4f(%.4f);
The number of full-screen movie halls: %d'''%(d1, d2, self.check_rate(), self.total_hot(), self.ghot(), self.check_time()))

    def hot(self):
        # Tính tổng độ hot của các phim được chiếu
        # total popularity
        return sum(sum(m.hot for m in h.movies if m.start<=h.last) * h.seatn for h in self.halls)

    def ghot(self):
        # Tính tổng độ hot của các phim chiếu trong khung giờ vàng
        # prime time
        hot = 0
        for h in self.halls:
            for m in h.movies:
                if m.isgolden():
                    hot += m.hot * h.seatn
                    break
        return hot

    def total_hot(self):
        # Tính tổng độ hot có trọng số (bao gồm prime time)
        # Weighted popularity
        return sum(sum(m.hot for m in h.movies if m.start<=h.last) * h.seatn for h in self.halls) + 3 * self.ghot()

    def check_time(self):
        # Kiểm tra số phòng chiếu hết thời gian
        # check time-out
        N = 0
        for h in self.halls:
            if h.movies[-1].start <= h.last:
                N +=1
        return N

    def check_rate(self):
        # Đánh giá độ tương đồng giữa tỷ lệ chiếu thực tế và tỷ lệ đề xuất
        """Popularity ~ Times ratio ~ Screening rate ~ Number ratio ~ Box office rate
        The degree of similarity between the system recommended screening rate and the actual screening rate
        """
        dict_ = self.count()
        d = 0
        movie_ids = list(self.movies.keys())
        hotp = np.array([self.movies[k][1] for k in movie_ids])
        S = np.sum(hotp)
        hotp /= np.sum(hotp)
        for id_, rate in dict_.items():
            d += abs(self.movies[id_][1]/S - rate)
        return 1 / (d + 0.001)

    def check_interval(self):
        # Tính khoảng cách thời gian giữa các phim chiếu ở các phòng
        # opening interval
        d1s = []
        d2s = []
        for k, h in enumerate(self.halls[:-1]):
            for hh in self.halls[k+1:]:
                d1, d2 = h.dist(hh)
                d1s.append(d1)
                d2s.append(d2)
        return min(d1s) / 60, min(d2s) / 60

    def time_interval(self):
        # Tính khoảng cách trung bình giữa các phim chiếu
        # opening interval
        deltas = []
        for k, h in enumerate(self.halls[:-1]):
            for hh in self.halls[k+1:]:
                d1, d2 = h.dist(hh)
                deltas.append((d1*0.5 + d2*0.5))
        delta = mymin(deltas)

        return delta / 60
