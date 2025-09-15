import copy 
from helper import stamp2str

class Movie(object):
    # Đại diện cho một bộ phim, chứa thông tin id, độ dài, độ hot, loại, tên, thời gian bắt đầu/kết thúc
    '''Movie has 4 (principal) propteries
    id_: id 
    length: length
    hot: hot
    type_: type
    '''
    
    __slots__ = ('id_', 'length', 'hot', 'type_', 'name', '__start', '__end', 'gtime', 'gapub')
    def __init__(self, id_, length, hot, type_, name, gtime=None, gapub=None):
        # Khởi tạo đối tượng Movie với các thuộc tính cơ bản
        self.id_ = id_
        self.length = length * 60
        self.hot = hot / 100
        self.type_ = type_
        self.name = name
        self.__start = 0
        self.__end = length * 60
        self.gtime = gtime
        self.gapub = gapub

    def __str__(self):
        # Trả về chuỗi mô tả phim, gồm id, độ hot, thời gian chiếu
        if self.isgolden():
            return 'movie %d(%.4s)*: %s - %s'%(self.id_, self.hot, stamp2str(self.start), stamp2str(self.end))
        else:
            return 'movie %d(%.4s): %s - %s'%(self.id_, self.hot, stamp2str(self.start), stamp2str(self.end))

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @start.setter
    def start(self, time):
        self.__start = time
        self.__end = time + self.length

    @end.setter
    def end(self, time):
        self.__end = time
        self.__start = time - self.length

    def isgolden(self):
        # Kiểm tra phim có chiếu trong khung giờ vàng (prime time) không
        return self.__end - 75 * 60 <= self.gtime <= self.__start + 75 * 60

    def copy(self):
        # Tạo Movie mới với metadata ban đầu
        new_movie = Movie(
            id_=self.id_,
            length=self.length // 60,  # vì self.length đang tính bằng giây
            hot=int(self.hot * 100),   # hot lưu dạng %
            type_=self.type_,
            name=self.name,
            gtime=self.gtime,
            gapub=self.gapub
        )
        # reset giờ về mặc định
        new_movie._Movie__start = 0
        new_movie._Movie__end = new_movie.length
        # print(f"[DEBUG] copy movie {self.id_}: m1({self.start}, {self.end}) -> m2({new_movie.start}, {new_movie.end})")

        return new_movie