import numpy as np
from random import random, randint
from constant import GTIME as gtime, GAPUP as gapub
from helper import mymin
from models.hall import Hall
from models.movie import Movie

class Manager:
    # Quản lý toàn bộ lịch chiếu, gồm danh sách phòng và phim, các hàm tối ưu và đánh giá lịch
    '''Manager has 1 (principal) proptery
    halls: halls
    '''

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
                N = sum(h.type_ for h in self.halls) + len(halls) / 2
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

    def initSchedule2(self, hook=list):
        # Khởi tạo lịch chiếu ngẫu nhiên kiểu 2 cho các phòng (dùng cho giải thuật tiến hóa)
        # minlen = min(m.length for m in self.movies)
        individual = hook(list([] for _ in range(len(self.halls))))
        # individual.gmovies = {}
        lst = self.estimate.copy()
        i = 0
        ts = np.random.permutation(len(self.halls))
        for k, h in enumerate(self.halls):
            # golden period
            h.movies = [self.movies[i].copy()]
            h.movies[0].start = gtime - 75 * 60 + ts[k] * 300
            individual[k] = [i]
            lst[i] -= 1
            if lst[i] == 0:
                i += 1
        for k, h in enumerate(self.halls):
            # common period
            n = h.type_
            times = np.random.randint(0, gapub, size=n)
            for l in range(1, n):
                end = h.movies[0].start - (times[l]+1) * 300
                start = end - self.movies[i].length
                if h.start <= start and end <= h.movies[0].start + 300:
                    h.movies.insert(0, self.movies[i].copy())
                    h.movies[0].start = start
                    t = times[l]
                    while lst[i] <= 0:
                        i += 1
                    individual[k] = [i, t] + individual[k]
                    lst[i] -= 1
                elif start < h.start:
                    gap = (h.movies[0].start - h.start)//300
                    if gap <= gapub:
                        individual[k] = [gap] + individual[k]
                    else:
                        for j, m in enumerate(self.movies):
                            if gap * 300 - 300 * gapub <= m.length + 300 <= gap * 300 and lst[j] > 0:
                                h.movies.insert(0, m.copy())
                                h.movies[0].end = h.movies[1].start - 300
                                t0 = (h.movies[0].start - h.start)//300
                                individual[k] = [t0, i, 1] + individual[k]
                                lst[j] -= 1
                                break
                        else:
                            while lst[i] <= 0:
                                i += 1
                            lst[i] -= 1
                            t0 = randint(0, gapub-1)
                            individual[k] = [t0, i, 1] + individual[k]
                            h.movies[0].start = self.movies[i].length + 300 * (t0 +1)
                            h.movies.insert(0, self.movies[i].copy())
                            h.movies[0].start = t0 * 300
                            for l in range(1, len(h.movies)-1):
                                m, mm = self.movies[l], self.movies[l+1]
                                if m.end <= mm.start - 300:
                                    break
                                else:
                                    mm.start = m.end + 300
                                individual[k][l*2+2] = 1
                    break

                    # if h.movies[-1].isgolden():
                    #     individual.gmovies.update({k:l})
                    # break

            t = times[-1]
            start = h.movies[-1].end + t * 300
            if start <= h.last:
                while lst[i] <= 0:
                    i += 1
                h.movies.insert(0, self.movies[i].copy())
                h.movies[-1].start = start
                individual[k] = individual[k] + [t, i]
                lst[i] -= 1
            d = h.type_ - len(h.movies)
            if d > 0:
                for _ in range(d):
                    if h.movies[-1].end + 300 <= h.last:
                        h.append(self.movies[i].copy())
                    individual[k] = individual[k] + [1, i]
            elif d < 0:
                individual[k] = individual[k][:2*d]
                h.movies = h.movies[:d]
        return individual

    def initSchedule1(self, hook=list):
        # Khởi tạo lịch chiếu ngẫu nhiên kiểu 1 cho các phòng (dùng cho giải thuật tiến hóa)
        # minlen = min(m.length for m in self.movies)
        individual = hook(list([] for _ in range(len(self.halls))))
        # individual.gmovies = {}
        lst = self.estimate.copy()
        i = 0
        ts = np.random.permutation(len(self.halls))
        for k, h in enumerate(self.halls):
            # Arrange movies in prime time
            h.movies = [self.movies[i].copy()]
            h.movies[0].start = gtime - 75 * 60 + ts[k] * 300
            individual[k] = [i]
            lst[i] -= 1
            if lst[i] == 0:
                i += 1
            # Arrange movies in common time
            n = h.type_
            times = np.random.randint(0, gapub, size=n)
            for l in range(1, n):
                end = h.movies[0].start - (times[l]+1) * 300
                start = end - self.movies[i].length
                if h.start <= start and end <= h.movies[0].start + 300:
                    h.movies.insert(0, self.movies[i].copy())
                    h.movies[0].start = start
                    t = times[l]
                    while lst[i] <= 0:
                        i += 1
                    individual[k] = [i, t] + individual[k]
                    lst[i] -= 1
                elif start < h.start:
                    gap = (h.movies[0].start - h.start)//300
                    if gap <= gapub:
                        individual[k] = [gap] + individual[k]
                    else:
                        for j, m in enumerate(self.movies):
                            if gap * 300 - 300 * gapub <= m.length + 300 <= gap * 300 and lst[j] > 0:
                                h.movies.insert(0, m.copy())
                                h.movies[0].end = h.movies[1].start - 300
                                t0 = (h.movies[0].start - h.start)//300
                                individual[k] = [t0, i, 1] + individual[k]
                                lst[j] -= 1
                                break
                        else:
                            while lst[i] <= 0:
                                i += 1
                            lst[i] -= 1
                            t0 = randint(0, gapub-1)
                            individual[k] = [t0, i, 1] + individual[k]
                            h.movies[0].start = self.movies[i].length + 300 * (t0 +1)
                            h.movies.insert(0, self.movies[i].copy())
                            h.movies[0].start = t0 * 300
                            for l in range(1, len(h.movies)-1):
                                m, mm = self.movies[l], self.movies[l+1]
                                if m.end <= mm.start - 300:
                                    break
                                else:
                                    mm.start = m.end + 300
                                individual[k][l*2+2] = 1
                    break

                    # if h.movies[-1].isgolden():
                    #     individual.gmovies.update({k:l})
                    # break

            t = times[-1]
            start = h.movies[-1].end + t * 300
            if start <= h.last:
                while lst[i] <= 0:
                    i += 1
                h.movies.insert(0, self.movies[i].copy())
                h.movies[-1].start = start
                individual[k] = individual[k] + [t, i]
                lst[i] -= 1
            d = h.type_ - len(h.movies)
            if d > 0:
                for _ in range(d):
                    if h.movies[-1].end + 300 <= h.last:
                        h.append(self.movies[i].copy())
                    individual[k] = individual[k] + [1, i]
            elif d < 0:
                individual[k] = individual[k][:2*d]
                h.movies = h.movies[:d]
        return individual

    def initSchedule(self, hook=list):
        # Chọn ngẫu nhiên một trong hai kiểu khởi tạo lịch chiếu
        if random() < .5:
            return self.initSchedule1(hook)
        else:
            return self.initSchedule2(hook)


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
        hotp /= S
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

    def dumps(self):
        # In ra thông tin chi tiết lịch chiếu của từng phòng
        for h in self.halls:
            h.dumps()
            print()

    def stat(self):
        # In ra thống kê tỷ lệ chiếu của từng phim
        dict_ = self.count()
        for id_, rate in dict_.items():
            print(movies[id_][1]/100, rate)

    def plot(self, axes=None):
        # Vẽ biểu đồ lịch chiếu phim cho các phòng
        from matplotlib.ticker import FuncFormatter, MaxNLocator
        if axes is None:
            fig = plt.figure(figsize=(14, 10))
            axes = fig.add_subplot(111)
        axes.invert_yaxis()

        def format_fn(tick_val, tick_pos):
            return stamp2str(tick_val)
        axes.xaxis.set_major_formatter(FuncFormatter(format_fn))
        axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        def format_fn(tick_val, tick_pos):
            k = int(tick_val)
            if k < len(self.halls):
                h = self.halls[k]
                return '%s(%d)'%(h.id_, h.seatn)
            else:
                return ''
        axes.yaxis.set_major_formatter(FuncFormatter(format_fn))
        axes.yaxis.set_major_locator(MaxNLocator(integer=True))

        H = len(self.halls)
        for k, h in enumerate(self.halls):
            for m in h.movies:
                if m.hot > 0.2:
                    color = 'r'
                elif m.hot > 0.15:
                    color = 'y'
                elif m.hot > 0.1:
                    color = 'g'
                elif m.hot > 0.05:
                    color = 'c'
                else:
                    color = 'b'
                axes.text(m.start, k, '%s'%m.id_)
                axes.plot((m.start, m.end), (k, k), color=color, linestyle='-')
            axes.plot((h.start, h.start), (k-1/2, k+1/2), color='k')
            axes.plot((h.last, h.last), (k-1/2, k+1/2), color='k')
        axes.plot((gtime-75*60, gtime-75*60), (0, H), color='y', linestyle='--')
        axes.plot((gtime+75*60, gtime+75*60), (0, H), color='y', linestyle='--')
        axes.set_xlabel('time')
        axes.set_ylabel('hall')
        axes.set_title('movie schedule')
        # Tạo chú thích phim
        movie_legend = 'Phim:\n' + '\n'.join([f'{m.id_} - {m.name}' for m in self.movies])
        # Tạo chú thích phòng
        hall_legend = 'Phòng:\n' + '\n'.join([f'{h.id_} - {h.name}' for h in self.halls])
        # Hiển thị chú thích ở góc phải dưới ảnh
        plt.gcf().text(0.99, 0.01, movie_legend + '\n\n' + hall_legend, fontsize=8, va='bottom', ha='right', family='monospace', bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
        plt.savefig('movie.png')
        plt.close()
        print('Đã lưu ảnh movie.png!')