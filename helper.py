import time
import numpy as np

def stamp2str(timeStamp):
    # Chuyển đổi timestamp sang chuỗi giờ:phút (HH:MM)
    timeArray = time.localtime(timeStamp)
    return time.strftime("%H:%M", timeArray)

# def mymin(x):
#     m = np.min(x)
#     return m + np.mean(x-m)/(m+1)

def mymin(x):
    # Tính giá trị tối thiểu có trọng số cho một dãy số
    x = np.sort(np.unique(x))
    return np.sum(a / 30**k for k, a in enumerate(x))
