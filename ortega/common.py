from geographiclib.geodesic import Geodesic
import pandas as pd
import numpy as np


def __check_dist(lat1: float, lon1: float, lat2: float, lon2: float):
    d = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
    return d['s12']


def __timedifcheck(t1: pd.Timestamp, t2: pd.Timestamp):
    return abs(pd.Timedelta(t2 - t1).total_seconds())