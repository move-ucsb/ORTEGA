from __future__ import annotations
import math
import pandas as pd
from typing import Any
import numpy as np
from shapely.geometry import Point
from .common import haversine


class STPoint:
    def __init__(self, x: float, y: float, time: pd.Timestamp, pid: int):
        self.x = x  # latitude
        self.y = y  # longitude
        self.time = time
        self.id = pid

    @classmethod
    def from_row(
            cls,
            row: Any,
            latitude_field: str,
            longitude_field: str,
            id_field: str,
            timefield: str,
    ):
        return cls(
            row[latitude_field],
            row[longitude_field],
            row[timefield],
            row[id_field],
        )

    def average_speed(
            self,
            stp2: STPoint,
            div_constant: float = 0.000000000000000000000000000000001,
    ):
        # return haversine(self.x, self.y, stp2.x, stp2.y) / (self.delta_time(stp2) + div_constant)  # m/s
        return self.euclidean_distance(stp2) / (self.delta_time(stp2) + div_constant)  # supposed to be in m/s

    def euclidean_distance(self, stp2: STPoint):
        return self.dx_dy_euclidean(stp2)[2]

    def dx_dy_euclidean(self, stp2: STPoint):
        dx = stp2.x - self.x
        dy = stp2.y - self.y
        dist = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        return dx, dy, dist

    def delta_time(self, stp2: STPoint):
        delta_time = self.time - stp2.time
        return math.fabs(delta_time.total_seconds())  # in seconds

    def ellipse(self, stp2: STPoint, speed: float):
        """
        Compute the four parameters center, major, minor, angle for further creating PPA
        :param stp2:
        :param speed:
        :return:
        """
        dt = self.delta_time(stp2)
        dx, dy, dist = self.dx_dy_euclidean(stp2)

        # the major axis of the PPA ellipse based on input speed (in time geography this speed is max speed)
        major = dt * speed
        minor: float = (major ** 2 - dist ** 2) ** 0.5  # calculate minor axis for the ellipse

        if dy == 0:
            dy = 0.1
        if dx == 0:
            dx = 0.1

        angle: float = np.rad2deg(math.atan(abs(dy / dx)))  # angle of the ellipse

        if dx * dy < 0:
            # the rotation angle of the PPA ellipse in 2nd and 4th quadrants
            angle = 180 - angle
        center = self.mid_point(stp2)
        return center, major, minor, angle

    def mid_point(self, stp2: STPoint):
        mx = (self.x + stp2.x) / 2
        my = (self.y + stp2.y) / 2

        return Point(mx, my)
