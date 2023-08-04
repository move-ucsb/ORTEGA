import pandas as pd
import numpy as np
import math
from datetime import datetime as datetime

def __check_dist(lat1: float, lon1: float, lat2: float, lon2: float):
    """

    :param lat1:
    :param lon1:
    :param lat2:
    :param lon2:
    :return:
    """
    dx = lon1 - lon2
    dy = lat1 - lat2
    dist = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
    return dist


def __timedifcheck(t1: pd.Timestamp, t2: pd.Timestamp):
    """

    :param t1:
    :param t2:
    :return:
    """
    return abs(pd.Timedelta(t2 - t1).total_seconds())

