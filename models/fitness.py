import numpy as np

class FitnessManager:
    def __init__(self, manager):
        self.manager = manager

    def print_fitness(self):
        # In ra giá trị fitness của lịch chiếu
        print('fitness: %.4f, %.4f, %.4f, %d' % (
            self.time_interval(), 
            self.check_rate(), 
            self.total_hot(), 
            self.check_time()
        ))


    def print_criterion(self):
        # In ra giá trị các tiêu chí đánh giá lịch chiếu
        for k in range(1, 13):
            if k != 10 and k!=11:
                print('criterion%d:'%k, getattr(self, 'criterion%d'%k)())
                
    def criterion1(self):
        # Tiêu chí 1: Đánh giá sự hợp lý khi sắp xếp phim vào phòng
        # Rationality of arranging movie screening halls(安排影片放映厅的合理性)
        c = self.count()
        alpha = 0
        for m in self.manager.movies:
            for k, h in enumerate(self.manager.halls):
                hc = h.count()
                if m.id_ in hc and c[m.id_] < hc[m.id_] * 2:
                    alpha += abs(m.hot - h.seat_rate)
                    break
        return alpha

    def criterion2(self):
        # Tiêu chí 2: Đánh giá độ tương đồng giữa tỷ lệ chiếu thực tế và tỷ lệ đề xuất
        # The degree of similarity between the system recommended screening rate and the actual screening rate(系统推荐排片率与实际排片率接近程度)
        return self.check_rate()

    def criterion3(self):
        # Tiêu chí 3: Số lượng phim chiếu trong khung giờ vàng
        # the number of movies shown during the prime time(黄金时间段放映电影数)
        hot = 0
        for h in self.manager.halls:
            for m in h.movies[::-1]:
                if m.isgolden():
                    hot += 1
                    break
        return hot

    def criterion4(self):
        # Tiêu chí 4: Phim hot nhất có được chiếu ở phòng tốt nhất trong khung giờ vàng không
        # the most popular movie screened in the optimal hall during the prime time(最火的影片排入最优厅黄金时间段)
        for m in self.manager.halls[0].movies:
            if m.id_ == self.manager.movies[0].id_ and m.isgolden():
                return 1
        return 0

    def criterion5(self):
        # Tiêu chí 5: (placeholder, luôn trả về 1)
        return 1

    def criterion6(self):
        # Tiêu chí 6: Đánh giá khoảng cách giữa các phim chiếu trong khung giờ vàng
        # Rationality of the interval between the opening of all movies in prime time (所有电影黄金时段开映间隔合理性)
        times = np.sort([m.start for h in self.manager.halls for m in h.movies if m.isgolden()])
        times = np.diff(times)
        return 1

    def criterion7(self):
        # Tiêu chí 7: Đánh giá khoảng cách giữa các phim chiếu ngoài khung giờ vàng
        # (所有电影非黄金时段开映间隔合理性)
        times = np.sort([m.start for h in self.manager.halls for m in h.movies if not m.isgolden()])
        times = np.diff(times)
        return 1

    def criterion8(self):
        # Tiêu chí 8: Tránh các phim chiếu cùng lúc
        # (避免同时开场)
        return 1

    def criterion9(self):
        # Tiêu chí 9: Đảm bảo khoảng cách ngắn cho các phim có doanh thu cao
        # (高票房日子场间隔尽量短)
        times = np.sort([m.start for h in self.manager.halls for m in h.movies])
        return 1

    def criterion10(self, latest='22'):
        # Tiêu chí 10: Đánh giá thời gian chiếu của phim hoạt hình ít hot
        # (低热度动画片开映时间合理性)
        n = 0
        for h in self.manager.halls:
            for m in h.movies:
                if '动画' in m.type and m.hot < 1/len(self.manager.halls) and m.end > latest:
                    n += 1
        return n

    def criterion11(self, earliest='22'):
        # Tiêu chí 11: Đánh giá thời gian chiếu của phim kinh dị ít hot
        # (低热度动画片开映时间合理性)
        n = 0
        for h in self.manager.halls:
            for m in h.movies:
                if '恐怖' in m.type and m.hot < 0.5/len(self.manager.halls) and m.start < earliest:
                    n += 1
        return n

    def hasbighall(self):
        # Kiểm tra có phòng chiếu lớn vượt trội không
        return self.manager.halls[0].seatn > self.manager.halls[1].seatn * 1.5

    def criterion12(self):
        # Tiêu chí 12: Đánh giá việc chia sẻ phòng lớn cho các phim hot
        # Hall sharing status(大厅共用情况)
        m, mm = self.manager.movies[:2]
        if self.hasbighall() and abs(m.hot - mm.hot) < 0.05:
            gm = [m for m in self.manager.halls[0].movies() if m.isgolden]
            if set(m.id_ for m in gm) == {m.id_, mm.id_}:
                return 1
            else:
                return 0

    def criterion13(self):
        # Tiêu chí 13: Đánh giá độ đa dạng của lịch chiếu
        # The richness of screening(影片排映丰富度)
        if len(self.manager.halls) >= 6 and sum(m.hot for m in self.manager.movies[:5])> .05:
            return len(self.count())

    def criterion14(self, minhot=0.1):
        # Tiêu chí 14: Đảm bảo phim ít hot không chiếu trong khung giờ vàng
        # not popular movie (小片不在黄金时段)
        n = 0
        for h in self.manager.halls:
            for m in h:
                if m.isgolden() and m.hot < minhot:
                    n += 1
        return n
