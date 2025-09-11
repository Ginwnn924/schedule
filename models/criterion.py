
class Criterion:
    # Đại diện cho một tiêu chí đánh giá lịch chiếu (giá trị, tên, trọng số, cấp độ)
    '''Criterion has 3 (principal) propteries
    value: value
    name: name
    weight: weight [5]
    level: level [None]
    '''

    def __init__(self, value, name='', weight=5, level=None):
        # Khởi tạo tiêu chí với các thuộc tính cơ bản
        self.value = value
        self.name = name
        self.weight = weight
        self.level = level

    def __repr__(self):
        return '%s: %.4f * %d'%(self.name, self.value, weight)

