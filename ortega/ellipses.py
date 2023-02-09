from datetime import datetime
import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from typing import Any, List, Tuple, Union

import numpy as np
import pandas as pd
from shapely.geometry.polygon import LinearRing
from shapely.geometry import Point, Polygon
from attrs import define, field

from .STPoint import STPoint


def ellipse_polyline(ptc: Point, major: float, minor: float, angle: float, n: int = 100):
    """

    :param ptc:
    :param major:
    :param minor:
    :param angle:
    :param n:
    :return:
    """
    # Return evenly spaced numbers over a specified interval.
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)

    st = np.sin(t)
    ct = np.cos(t)

    angle = np.deg2rad(angle)  # rotation angle of ellipse
    sa = np.sin(angle)
    ca = np.cos(angle)

    p = np.empty((n, 2))
    # divide the major and minor axis by 2.0
    p[:, 0] = ptc.x + major / 2.0 * ca * ct - minor / 2.0 * sa * st
    p[:, 1] = ptc.y + major / 2.0 * sa * ct + minor / 2.0 * ca * st

    return p


def ppa_ellipse(stp1: STPoint, stp2: STPoint, est_speed: float, avg_speed: float):
    """
    Instantiate shapely LinearRing object for PPA
    :param stp1:
    :param stp2:
    :param est_speed:
    :param avg_speed:
    :return:
    """
    speed = max(est_speed, avg_speed)

    center, major, minor, angle = stp1.ellipse(stp2, speed)
    ply = ellipse_polyline(center, major, minor, angle)

    ell = LinearRing(ply)  # creates the PPA ellipse
    return ell, major  # returns a shapely LinearRing


class SpeedMemory:
    def __init__(self, kernel: List[int] = [1, 1, 2, 5, 10]):
        self.speed: List[float] = []
        self.kernel = np.asarray(kernel)
        self.memory_length = len(kernel)

    def append(self, speed: float):
        self.speed.append(speed)

    def get_average(self):
        if len(self.speed) < self.memory_length:
            return self.speed[-1]

        subset = self.speed[-self.memory_length:]
        speed_memory_subset_np = np.asarray(subset)
        avg_speed_kern_list = self.kernel * speed_memory_subset_np
        avg_speed_kern = sum(avg_speed_kern_list) / self.kernel.sum()

        return avg_speed_kern


class EllipseDictionary(TypedDict):
    t1: datetime
    t2: Union[datetime, None]
    pid: int
    lon: float
    lat: float
    last_lon: Union[float, None]
    last_lat: Union[float, None]


@define(frozen=True)
class Ellipse:
    el: Tuple[LinearRing, float]
    lat: float
    lon: float
    last_lat: Union[float, None]
    last_lon: Union[float, None]
    pid: int  # current point person id
    last_pid: Union[int, None]  # last point's person id
    t1: pd.Timestamp  # current timestamp
    t2: Union[pd.Timestamp, None] = field()  # last point's timestamp
    speed: float
    geom: Polygon

    def to_dict(self) -> EllipseDictionary:
        return {
            "t1": self.t1,
            "t2": self.t2,
            "pid": self.pid,
            "lon": self.lon,
            "lat": self.lat,
            "last_lon": self.last_lon,
            "last_lat": self.last_lat,
        }


class EllipseList:
    def __init__(
            self,
            latitude_field: str,
            longitude_field: str,
            id_field: str,
            time_field: str,
    ):
        self.list: List[Ellipse] = []
        self.last_lat: Union[float, None] = None
        self.last_lon: Union[float, None] = None
        self.last_id: Union[int, None] = None
        self.last_ts: Union[pd.Timestamp, None] = None
        self.latitude_field = latitude_field
        self.longitude_field = longitude_field
        self.id_field = id_field
        self.time_field = time_field

    def add_ellipse(
            self,
            ppa_ellipse: Tuple[LinearRing, float],
            row: Any,
            est_speed: float,
            geom: Polygon,
    ):
        new_ellipse = Ellipse(
            ppa_ellipse,
            row[self.latitude_field],
            row[self.longitude_field],
            self.last_lat,
            self.last_lon,
            row[self.id_field],
            self.last_id,
            row[self.time_field],
            self.last_ts,
            est_speed,
            geom,
        )

        self.list.append(new_ellipse)

    def set_last(self, row: Any):
        self.last_lat = row[self.latitude_field]
        self.last_lon = row[self.longitude_field]
        self.last_id = row[self.id_field]
        self.last_ts = row[self.time_field]

    def get_last_to_point(self) -> STPoint:
        return STPoint(self.last_lat, self.last_lon, self.last_ts, self.last_id)

    def generate(self, gen_ellipses_for1: pd.DataFrame, multi_el: float = 1.25):
        speed_memory = SpeedMemory()

        sorted_iter = gen_ellipses_for1.sort_values(self.time_field)
        for _, row in sorted_iter.iterrows():
            if row[self.id_field] == self.last_id:  # make sure still looping the same pid
                p1: STPoint = STPoint.from_row(row, self.latitude_field, self.longitude_field, self.id_field,
                                               self.time_field)
                p2: STPoint = self.get_last_to_point()
                est_speed = p1.average_speed(p2) * multi_el * 3600
                speed_memory.append(est_speed)  # speed averaging to minimize uncertainty and noise effects of
                # movement data
                avg_speed_kern = speed_memory.get_average()
                el = ppa_ellipse(p1, p2, est_speed, avg_speed_kern)
                geom = Polygon(el[0])
                try:
                    self.add_ellipse(el, row, est_speed, geom)
                except Exception as e:
                    print(e)
                    print("Can't make ellipse class instance")
            self.set_last(row)
        return self.list
