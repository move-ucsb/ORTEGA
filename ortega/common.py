import pandas as pd
import numpy as np
import math
from datetime import datetime as datetime
from math import radians, cos, sin, asin, sqrt


def haversine(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r * 1000  # in meters


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

