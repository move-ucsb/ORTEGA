from datetime import datetime as datetime
from .ellipses import Ellipse, EllipseList
from pandas.api.types import is_datetime64_dtype
from typing import List, Tuple
from .common import __timedifcheck
from .common import *
from .output import *


def __check_spatial_intersect(item: Ellipse, others: Ellipse) -> bool:
    return (
            item.el[0].intersects(others.el[0])
            or item.geom.within(others.geom)
            or others.geom.within(item.geom)
    )


def __check_temporal_intersect(
        item: Ellipse, item2: Ellipse, interaction_min_delay: float
) -> bool:
    return __timedifcheck(item.t1, item2.t1) <= interaction_min_delay * 60


def get_spatiotemporal_intersect_pairs(
        ellipses_list_id1: List[Ellipse], ellipses_list_id2: List[Ellipse],
        interaction_min_delay: float, max_el_time_min: float
) -> List[Tuple[Ellipse, Ellipse]]:
    """
    Get spatially and temporally intersect PPA pairs
    :param ellipses_list_id2:
    :param ellipses_list_id1:
    :param max_el_time_min:
    :param interaction_min_delay:
    :return:
    """
    intersection_pairs = []
    for count, item in enumerate(ellipses_list_id1, 1):
        if __timedifcheck(item.t1, item.t2) > max_el_time_min * 60:
            continue  # May 15,2020: eliminate PPA if the time interval of PPA is too large:
        # if count % 500 == 0:
        # print(f"\r > On item {count} of {len(filtered_list)}", end="")

        # temporal intersect
        sub_ellipses_list = []
        for item2 in ellipses_list_id2:
            if __timedifcheck(item2.t1, item2.t2) > max_el_time_min * 60:
                continue  # eliminate PPA if the time interval of PPA of another individual is too large
            if __check_temporal_intersect(item, item2, interaction_min_delay):
                sub_ellipses_list.append(item2)

        if len(sub_ellipses_list) == 0:
            continue

        # spatial intersect
        intersection_pairs.extend(
            [
                (item, others)
                for others in sub_ellipses_list
                if __check_spatial_intersect(item, others)
            ]
        )

    return intersection_pairs


def intersect_ellipse_todataframe(intersection_df: List[Tuple[Ellipse, Ellipse]]):
    def columns_names(e: Ellipse, num: int):
        as_dict = e.to_dict()

        return {
            f"P{num}": as_dict["pid"],
            f"P{num}_t_start": as_dict["t2"],
            f"P{num}_t_end": as_dict["t1"],
            f"P{num}_startlat": as_dict["last_lat"],
            f"P{num}_startlon": as_dict["last_lon"],
            f"P{num}_endlat": as_dict["lat"],
            f"P{num}_endlon": as_dict["lon"]
        }

    return pd.DataFrame(
        [
            {**columns_names(item, 1), **columns_names(item2, 2)}
            for item, item2 in intersection_df
        ]
    )


def __remove_largePPA(df: pd.DataFrame, max_el_time_min: float):
    """

    :param df:
    :param max_el_time_min:
    :return:
    """
    df['p1diff'] = df['P1_t_end'] - df['P1_t_start']
    df['p1diff'] = df['p1diff'].dt.total_seconds().div(60)
    df['p2diff'] = df['P2_t_end'] - df['P2_t_start']
    df['p2diff'] = df['p2diff'].dt.total_seconds().div(60)
    df = df[(df['p1diff'] > 0) & (df['p1diff'] < max_el_time_min)]
    df = df[(df['p2diff'] > 0) & (df['p2diff'] < max_el_time_min)]
    df = df.sort_values(by=['P1_t_start', 'P2_t_start'])
    return df


def __merge_continuous_incident(df: pd.DataFrame, id1: int, id2: int):
    """
    after estimating duration merge some continuous interaction incidents
    :param df:
    :param id1:
    :param id2:
    :return:
    """
    pstart = df['Start'].tolist()
    pend = df['End'].tolist()
    finalstart, finalend = [], []
    tag = []
    for i in range(0, len(pstart) - 1):
        if pend[i] >= pstart[i + 1]:
            tag.append(1)
        else:
            tag.append(0)
    tag.append(0)
    df['tag'] = tag
    finalsub, subq = [], []
    j = 0
    while j < len(tag):
        if tag[j] == 1 and tag[j + 1] == 1:
            subq.extend([pstart[j], pend[j], pstart[j + 1], pend[j + 1]])
            j += 1
        elif tag[j] == 1 and tag[j + 1] == 0:
            subq.extend([pstart[j], pend[j], pstart[j + 1], pend[j + 1]])
        else:
            if len(subq) != 0:
                finalsub.append(subq)
            else:
                finalsub.append([pstart[j], pend[j]])
            subq = []
        j += 1
    for item in finalsub:
        finalstart.append(min(item))
        finalend.append(max(item))

    df_new = pd.DataFrame(list(zip(finalstart, finalend)), columns=['Start', 'End'])
    df_new['P1'] = id1
    df_new['P2'] = id2
    df_new['No'] = np.arange(df_new.shape[0]) + 1
    df_new['Duration'] = df_new['End'] - df_new['Start']
    df_new['Duration'] = df_new['Duration'].dt.total_seconds().div(60)
    return df_new[['No', 'P1', 'P2', 'Start', 'End', 'Duration']]


def durationEstimator(df: pd.DataFrame, max_el_time_min: float, id1: int, id2: int):
    """
    estimate duration of interation
    :param id2:
    :param id1:
    :param df:
    :param max_el_time_min: allowable maximum time interval of PPA in minute
    :return:
    """
    df = __remove_largePPA(df, max_el_time_min)
    p1start = df['P1_t_start'].tolist()
    p1end = df['P1_t_end'].tolist()
    p2start = df['P2_t_start'].tolist()
    p2end = df['P2_t_end'].tolist()
    final_start, final_end, subsequenceOfInteraction = [], [], []
    for i in range(0, len(p1start) - 1):  # identify subsequence of continuous interaction
        if datetime.strptime(str(p1start[i]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p1start[i + 1]),
                                                                                        '%Y-%m-%d %H:%M:%S'):
            subsequenceOfInteraction.extend([p1start[i], p1end[i], p1end[i + 1], p2start[i], p2end[i], p2start[i + 1],
                                             p2end[i + 1]])  # append all time in a candidate pool
        elif datetime.strptime(str(p1end[i]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p1start[i + 1]),
                                                                                        '%Y-%m-%d %H:%M:%S'):
            subsequenceOfInteraction.extend([p1start[i], p1end[i], p1end[i + 1], p2start[i], p2end[i], p2start[i + 1],
                                             p2end[i + 1]])  # append all time in a candidate pool
        else:
            if len(subsequenceOfInteraction) == 0:
                subsequenceOfInteraction.extend([p1start[i], p1end[i], p2start[i], p2end[i]])
            final_start.append(min(subsequenceOfInteraction))  # print(i,p1start[i],p1end[i],p1start[i+1],p1end[i+1])
            final_end.append(max(subsequenceOfInteraction))
            subsequenceOfInteraction = []
    if len(subsequenceOfInteraction) != 0:
        final_start.append(min(subsequenceOfInteraction))
        final_end.append(max(subsequenceOfInteraction))
    if len(p1start) == 1:
        i = 0
        subsequenceOfInteraction.extend(
            [p1start[i], p1end[i], p2start[i], p2end[i]])  # append all time in a candidate pool
        final_start.append(min(subsequenceOfInteraction))
        final_end.append(max(subsequenceOfInteraction))
    df_new = pd.DataFrame(list(zip(final_start, final_end)), columns=['Start', 'End'])
    df_new['P1'] = id1
    df_new['P2'] = id2
    df_new['No'] = np.arange(df_new.shape[0]) + 1
    df_new['Duration'] = df_new['End'] - df_new['Start']
    df_new['Duration'] = df_new['Duration'].dt.total_seconds().div(60)
    df_new = __merge_continuous_incident(df_new, id1, id2)
    return df_new[['No', 'P1', 'P2', 'Start', 'End', 'Duration']]


class ORTEGA:
    def __init__(
            self,
            data: pd.DataFrame,
            minute_delay: float,  # in minute
            start_time: str = None,  # only select a segment of tracking points for the two moving entities
            end_time: str = None,
            max_el_time_min: float = 10000,  # in minute
            latitude_field: str = "latitude",
            longitude_field: str = "longitude",
            id_field: str = "pid",
            time_field: str = "time_local",  # must include month, day, year, hour, minute, second
    ):
        self.data = data
        self.start_time = start_time
        self.end_time = end_time
        self.latitude_field = latitude_field
        self.longitude_field = longitude_field
        self.id_field = id_field
        self.time_field = time_field
        self.minute_delay = minute_delay
        self.max_el_time_min = max_el_time_min
        self.__validate()
        self.__start()

    @property
    def minute_delay(self):
        return self._minute_delay

    @minute_delay.setter
    def minute_delay(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Parameter 'minute_delay' must be numeric!")
        if value <= 0:
            raise ValueError("Parameter 'minute_delay' must be greater than zero!")
        self._minute_delay = value

    @property
    def max_el_time_min(self):
        return self._max_el_time_min

    @max_el_time_min.setter
    def max_el_time_min(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Parameter 'max_el_time_min' must be numeric!")
        if value <= 0:
            raise ValueError("Parameter 'max_el_time_min' must be greater than zero!")
        self._max_el_time_min = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, pd.DataFrame):
            raise TypeError("Parameter 'data' must be a dataframe!")
        if value.shape[0] == 0:
            raise ValueError("The input dataframe is empty")
        self._data = value

    @property
    def latitude_field(self):
        return self._latitude_field

    @latitude_field.setter
    def latitude_field(self, value):
        if not isinstance(value, str):
            raise TypeError("Parameter 'latitude_field' must be a string!")
        if value not in self.data.columns:
            raise KeyError("Column 'latitude_field' does not exist!")
        self._latitude_field = value

    @property
    def longitude_field(self):
        return self._longitude_field

    @longitude_field.setter
    def longitude_field(self, value):
        if not isinstance(value, str):
            raise TypeError("Parameter 'longitude_field' must be a string!")
        if value not in self.data.columns:
            raise KeyError("Column 'longitude_field' does not exist!")
        self._longitude_field = value

    @property
    def id_field(self):
        return self._id_field

    @id_field.setter
    def id_field(self, value):
        if not isinstance(value, str):
            raise TypeError("Parameter 'id_field' must be a string!")
        if value not in self.data.columns:
            raise KeyError("Column 'id_field' does not exist!")
        self._id_field = value

    @property
    def time_field(self):
        return self._time_field

    @time_field.setter
    def time_field(self, value):
        if not isinstance(value, str):
            raise TypeError("Parameter 'time_field' must be a string!")
        if value not in self.data.columns:
            raise KeyError("Column 'time_field' does not exist!")
        self._time_field = value

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if value is not None:
            try:
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError("Incorrect 'start_time' format, should be YYYY-MM-DD HH:MM:SS")
        self._start_time = value

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        if value is not None:
            try:
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError("Incorrect 'end_time' format, should be YYYY-MM-DD HH:MM:SS")
        self._end_time = value

    def __validate(self):
        """
        private function, only can be called in side the class
        """
        if not is_datetime64_dtype(self.data[self.time_field]):
            raise TypeError("Column 'time_field' is not datetime type! Use pd.to_datetime() to convert to datetime.")

        id_list = self.data[self.id_field].unique().tolist()
        if len(id_list) != 2:
            raise ValueError(f'Only two unique id is allowed but {len(id_list)} id are found in the given dataframe!')
        else:
            self.id1, self.id2 = id_list[0], id_list[1]
            # split the dataframe according to id and filter by the time window if given
            if self.start_time is not None and self.end_time is None:
                start_time = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
                self.subset = self.data[[self.data[self.time_field] >= start_time]]
                self.df1 = self.subset[self.subset[self.id_field] == self.id1]
                self.df2 = self.subset[self.subset[self.id_field] == self.id2]
            elif self.start_time is None and self.end_time is not None:
                end_time = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')
                self.subset = self.data[[self.data[self.time_field] <= end_time]]
                self.df1 = self.subset[self.subset[self.id_field] == self.id1]
                self.df2 = self.subset[self.subset[self.id_field] == self.id2]
            elif self.start_time is not None and self.end_time is not None:
                start_time = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')
                self.subset = self.data[
                    (self.data[self.time_field] >= start_time) & (self.data[self.time_field] <= end_time)]
                self.df1 = self.subset[self.subset[self.id_field] == self.id1]
                self.df2 = self.subset[self.subset[self.id_field] == self.id2]
            else:
                self.df1 = self.data[self.data[self.id_field] == self.id1]
                self.df2 = self.data[self.data[self.id_field] == self.id2]

    def __start(self):
        """
        private method, only can be called inside the class
        """

        self.ellipses_list = self.__get_ellipse_list(self.df1, self.df2)  # all ellipses for two objects
        self.ellipses_list_id1 = [i for i in self.ellipses_list if i.pid == self.id1]
        self.ellipses_list_id2 = [i for i in self.ellipses_list if i.pid == self.id2]

        #  list of intersecting ellipses
        self.all_intersection_pairs = self.__get_spatiotemporal_intersect_pairs()

        if not self.all_intersection_pairs:
            print(datetime.now(), 'Complete! No interaction found!')
        else:
            print(datetime.now(), f'Complete! {len(self.all_intersection_pairs)} pairs of interaction found!')

            # convert the list of intersecting ellipses to dataframe format
            self.df_all_intersection_pairs = intersect_ellipse_todataframe(self.all_intersection_pairs)

            # compute duration of interaction and output as a df
            self.df_duration = durationEstimator(self.df_all_intersection_pairs, self.max_el_time_min, self.id1,
                                                 self.id2)


    def __get_ellipse_list(self, df1: pd.DataFrame, df2: pd.DataFrame):
        """
        Construct PPA ellipse using as input the two dataframes of GPS tracks of two individuals
        :param df1: a pandas dataframe of GPS points of individual id1
        :param df2: a pandas dataframe of GPS points of individual id2
        :return:
        """
        print(datetime.now(), "Generate PPA list for the two moving entities")
        ellipses_list_gen = EllipseList(self.latitude_field, self.longitude_field, self.id_field, self.time_field)
        ellipses_list_gen.generate(df1)  # create PPA for df1
        return ellipses_list_gen.generate(df2)  # append PPA based on df2 to the above ellipses_list_gen object

    def __get_spatiotemporal_intersect_pairs(self):
        print(datetime.now(), "Getting spatial and temporal intersection pairs")
        return get_spatiotemporal_intersect_pairs(self.ellipses_list_id1, self.ellipses_list_id2,
                                                  self.minute_delay, self.max_el_time_min)

    def save_shapefile(self):
        output_shapefile(self.ellipses_list, self.max_el_time_min, self.id1, self.id2)

    def compute_ppa_size(self):
        compute_ppa_size(self.ellipses_list_id1, self.ellipses_list_id2, self.id1, self.id2)

    def compute_ppa_interval(self):
        compute_ppa_interval(self.df1, self.df2, self.time_field, self.id1, self.id2)

