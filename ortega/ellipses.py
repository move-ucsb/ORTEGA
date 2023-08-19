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
    create polyline (a set of sequential points) for ellipse
    :param ptc:
    :param major:
    :param minor:
    :param angle:
    :param n:
    :return:
    """

    t = np.linspace(0, 2 * np.pi, n, endpoint=False)  # Return evenly spaced numbers over a specified interval

    st = np.sin(t)
    ct = np.cos(t)

    angle = np.deg2rad(angle)  # rotation angle of ellipse in radius unit
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
    :param avg_speed: floating average of speed over an exponential kernel
    :param stp1:
    :param stp2:
    :param est_speed: instant speed based on a pair of consecutive points
    :return:
    """
    speed = max(est_speed, avg_speed)  # avg_speed can be negative value so this step can prevent a negative speed
    center, major, minor, angle = stp1.ellipse(stp2, speed)
    # print(center, major, minor, angle)
    ply = ellipse_polyline(center, major, minor, angle)
    ell = LinearRing(ply)  # creates the PPA ellipse
    return ell, angle  # returns a shapely LinearRing and angle of the object


class SpeedMemory:
    # this class is for averaging speeds of several consecutive PPAs in order to mitigate GPS drift effects and
    # prevent PPA being a beeline between two points
    def __init__(self, kernel: List[int] = [1, 1, 2, 5, 10]):
        self.speed: List[float] = []
        self.kernel = np.asarray(kernel)

    def append(self, speed: float):
        self.speed.append(speed)

    def get_average(self):
        #  average speed over a given kernel
        memory_length = len(self.kernel)  # = 5
        if len(self.speed) < memory_length:
            return self.speed[-1]

        speed_memory_subset_np = np.asarray(self.speed[-memory_length:])  # previous 5 speeds
        avg_speed_kern = sum(self.kernel * speed_memory_subset_np) / self.kernel.sum()
        return avg_speed_kern


class EllipseDictionary(TypedDict):
    #  this is a TypedDict class for creating dataframe of intersecting PPA later
    t1: datetime
    t0: Union[datetime, None]
    pid: int
    lon: float
    lat: float
    last_lon: Union[float, None]
    last_lat: Union[float, None]
    speed: float
    direction: float
    attrs: Union[Any, None]
    last_attrs: Union[Any, None]


@define(frozen=True)
class Ellipse:
    #  this is an Ellipse class for PPAs
    el: LinearRing  # a shapeley LinearRing object to delimit the PPA boundary
    lat: float
    lon: float
    last_lat: Union[float, None]
    last_lon: Union[float, None]
    pid: int  # current point person id
    last_pid: Union[int, None]  # last point's person id
    t1: pd.Timestamp  # current timestamp
    t0: Union[pd.Timestamp, None] = field()  # last point's timestamp
    speed: float  # PPA speed between two consecutive points not the average speed over a few points
    direction: float  # PPA direction
    geom: Polygon  # a shapeley Polygon object for PPA (so that we can use geom.within to determine if two PPAs overlap)
    attrs: Union[Any, None] = None
    last_attrs: Union[Any, None] = None

    def to_dict(self) -> EllipseDictionary:
        #  return a dict for creating dataframe of intersecting PPA later
        return {
            "t1": self.t1,
            "t0": self.t0,
            "pid": self.pid,
            "lon": self.lon,
            "lat": self.lat,
            "last_lon": self.last_lon,
            "last_lat": self.last_lat,
            "speed": self.speed,
            "direction": self.direction,
            "attrs": self.attrs,
            "last_attrs": self.last_attrs
        }


class EllipseList:
    # save all PPAs of two moving objects as a EllipseList
    def __init__(
            self,
            latitude_field: str,
            longitude_field: str,
            id_field: str,
            time_field: str,
            attr_fields: Union[List[str], None] = None
    ):
        self.list: List[Ellipse] = []
        self.last_lat: Union[
            float, None] = None  # having last_lat, last_lon, last_id, last_ts here just for initializing Ellipse()
        self.last_lon: Union[
            float, None] = None  # these attributes are not useful anywhere besides initializing Ellipse()
        self.last_id: Union[int, None] = None  # they only save the attributes of the last point of the tracking data
        self.last_ts: Union[pd.Timestamp, None] = None
        self.last_attrs: Any = None
        self.latitude_field = latitude_field
        self.longitude_field = longitude_field
        self.id_field = id_field
        self.time_field = time_field
        self.attr_fields = attr_fields

    def add_ellipse(
            self,
            el: LinearRing,
            row: Any,
            est_speed: float,
            direction: float,
            geom: Polygon,
    ):
        if self.attr_fields is not None:
            new_ellipse = Ellipse(
                el,
                row[self.latitude_field],
                row[self.longitude_field],
                self.last_lat,
                self.last_lon,
                row[self.id_field],
                self.last_id,
                row[self.time_field],
                self.last_ts,
                est_speed,
                direction,
                geom,
                row[self.attr_fields].to_dict(),
                self.last_attrs
            )
        else:
            new_ellipse = Ellipse(
                el,
                row[self.latitude_field],
                row[self.longitude_field],
                self.last_lat,
                self.last_lon,
                row[self.id_field],
                self.last_id,
                row[self.time_field],
                self.last_ts,
                est_speed,
                direction,
                geom,
            )
        self.list.append(new_ellipse)

    def set_last(self, row: Any):
        self.last_lat = row[self.latitude_field]
        self.last_lon = row[self.longitude_field]
        self.last_id = row[self.id_field]
        self.last_ts = row[self.time_field]
        if self.attr_fields is not None:
            self.last_attrs = row[self.attr_fields].to_dict()

    def get_last_to_point(self) -> STPoint:
        return STPoint(self.last_lat, self.last_lon, self.last_ts, self.last_id)

    def generate(self, gen_ellipses_for1: pd.DataFrame, max_el_time_min: float = 100000,
                 multi_el: float = 1.25, speed_average: bool = False):
        """
        Create PPAs based on the following parameters
        :param speed_average: if True, apply speed average to compute max speed for PPA
        :param gen_ellipses_for1: a pd.DataFrame of list of GPS tracking points of a moving object
        :param max_el_time_min: remove large PPA if time interval greater than this value
        :param multi_el: default value is 1.25 to avoid the resulted PPA being a beeline between two points
        :return:
        """

        speed_memory = SpeedMemory()
        avg_speed_kern = -1
        sorted_iter = gen_ellipses_for1.sort_values(self.time_field)
        for _, row in sorted_iter.iterrows():
            if row[self.id_field] == self.last_id:  # make sure still looping the same pid
                if abs(pd.Timedelta(row[self.time_field] - self.last_ts).total_seconds()) > max_el_time_min * 60:
                    # remove large PPAs
                    self.set_last(row)
                    speed_memory = SpeedMemory()  # clear speed_memory if ever skip a PPA
                    continue
                p1: STPoint = STPoint.from_row(row, self.latitude_field, self.longitude_field, self.id_field,
                                               self.time_field)
                p2: STPoint = self.get_last_to_point()
                inst_speed = p1.average_speed(p2)
                est_speed = inst_speed * multi_el
                # if do not apply multi_el for max speed, the resulted PPA will be a beeline between two points
                if est_speed <= 0:  # if not moving, skip the step of creating PPA
                    self.set_last(row)
                    speed_memory = SpeedMemory()  # clear speed_memory if ever skip a PPA
                    continue
                if speed_average:
                    # speed averaging to minimize uncertainty and noise effects of movement data
                    speed_memory.append(est_speed)
                    avg_speed_kern = speed_memory.get_average()

                if avg_speed_kern > 0:
                    el, angle = ppa_ellipse(p1, p2, est_speed, avg_speed_kern)
                else:
                    el, angle = ppa_ellipse(p1, p2, est_speed, est_speed)
                geom = Polygon(el)
                try:
                    self.add_ellipse(el, row, inst_speed, angle, geom)
                except Exception as e:
                    print(e)
                    print("Can't make ellipse class instance")
            self.set_last(row)
        return self.list
