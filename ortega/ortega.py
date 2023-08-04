from datetime import datetime as datetime
from .ellipses import Ellipse, EllipseList
from pandas.api.types import is_datetime64_dtype
from typing import List, Tuple
from .common import __timedifcheck
from .common import *
from .output import *


def __check_spatial_intersect(item: Ellipse, others: Ellipse) -> bool:
    """
    test
    :param item:
    :param others:
    :return:
    """
    return (
            item.el.intersects(others.el)
            or item.geom.within(others.geom)
            or others.geom.within(item.geom)
    )


# def get_time_difference(
#         ellipses_list_id1: List[Ellipse], ellipses_list_id2: List[Ellipse]):
#     time_diff = []
#     for count, item in enumerate(ellipses_list_id1, 1):
#         # spatial intersect
#         sub_ellipses_list = []
#         for item2 in ellipses_list_id2:
#             if __check_spatial_intersect(item, item2):
#                 time_diff.append(__timedifcheck(item.t1, item2.t1))
#     return time_diff


def get_spatial_intersect_pairs(
        ellipses_list_id1: List[Ellipse], ellipses_list_id2: List[Ellipse],
        ) -> List[Tuple[Ellipse, Ellipse]]:
    intersection_pairs = []
    for count, item in enumerate(ellipses_list_id1, 1):
        # spatial intersect
        for item2 in ellipses_list_id2:
            if __check_spatial_intersect(item, item2):
                intersection_pairs.append((item, item2))
    return intersection_pairs


def get_timedelay_pairs(intersection_df: List[Tuple[Ellipse, Ellipse]],
                        interaction_min_delay: float, interaction_max_delay: float):
    intersection_pair = []
    for pair in intersection_df:
        if (__timedifcheck(pair[0].t1, pair[1].t1) >= interaction_min_delay * 60) & (
                __timedifcheck(pair[0].t1, pair[1].t1) <= interaction_max_delay * 60):
            intersection_pair.append(pair)
    return intersection_pair


def intersect_ellipse_todataframe(intersection_df: List[Tuple[Ellipse, Ellipse]]):
    """

    :param intersection_df:
    :return:
    """

    def columns_names(e: Ellipse, num: int):
        as_dict = e.to_dict()

        return {
            f"p{num}": as_dict["pid"],
            f"p{num}_t_start": as_dict["t0"],
            f"p{num}_t_end": as_dict["t1"],
            f"p{num}_startlat": as_dict["last_lat"],
            f"p{num}_startlon": as_dict["last_lon"],
            f"p{num}_endlat": as_dict["lat"],
            f"p{num}_endlon": as_dict["lon"],
            f"p{num}_speed": as_dict["speed"],
            f"p{num}_direction": as_dict["direction"]
        }

    return pd.DataFrame(
        [
            {**columns_names(item, 1), **columns_names(item2, 2)}
            for item, item2 in intersection_df
        ]
    )


def check_continuous(df: pd.DataFrame, id1: int, id2: int):
    p1start = df['p1_t_start'].tolist()
    p1end = df['p1_t_end'].tolist()
    p2start = df['p2_t_start'].tolist()
    p2end = df['p2_t_end'].tolist()
    p1_start_time, p1_end_time, p2_start_time, p2_end_time = [], [], [], []
    p1_start_index, p1_end_index = [], []
    p1_start_time.append(p1start[0])
    p1_start_index.append(0)
    for i in range(1, len(p1start)):
        if datetime.strptime(str(p1start[i]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p1start[i - 1]),
                                                                                        '%Y-%m-%d %H:%M:%S'):
            if datetime.strptime(str(p2start[i]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p2start[i - 1]),
                                                                                            '%Y-%m-%d %H:%M:%S'):
                continue
            elif datetime.strptime(str(p2end[i - 1]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(
                    str(p2start[i]),'%Y-%m-%d %H:%M:%S') or datetime.strptime(
                    str(p2start[i - 1]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p2end[i]), '%Y-%m-%d %H:%M:%S'):
                continue
            else:
                p1_end_time.append(p1end[i - 1])
                p1_end_index.append(i - 1)
                p1_start_time.append(p1start[i])
                p1_start_index.append(i)
        elif datetime.strptime(str(p1end[i - 1]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p1start[i]),
                                                                                        '%Y-%m-%d %H:%M:%S'):
            if datetime.strptime(str(p2start[i]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p2start[i - 1]),
                                                                                            '%Y-%m-%d %H:%M:%S'):
                continue
            elif datetime.strptime(str(p2end[i - 1]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(
                    str(p2start[i]), '%Y-%m-%d %H:%M:%S') or datetime.strptime(
                    str(p2start[i - 1]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p2end[i]), '%Y-%m-%d %H:%M:%S'):
                continue
            else:
                p1_end_time.append(p1end[i - 1])
                p1_end_index.append(i - 1)
                p1_start_time.append(p1start[i])
                p1_start_index.append(i)
        else:
            p1_end_time.append(p1end[i - 1])
            p1_end_index.append(i - 1)
            p1_start_time.append(p1start[i])
            p1_start_index.append(i)
    p1_end_time.append(p1end[len(p1end) - 1])
    p1_end_index.append(len(p1end) - 1)
    
    p2_start_pool, p2_end_pool = [], []
    p2_start_pool_list, p2_end_pool_list = [], []
    
    i = 0
    for j in p1_end_index:
        while i <= j:
            p2_start_pool.append(p2start[i])
            p2_end_pool.append(p2end[i])
            i += 1
        p2_start_pool.sort()
        p2_end_pool.sort()
        p2_start_pool_list.append(p2_start_pool)
        p2_end_pool_list.append(p2_end_pool)
        p2_start_pool, p2_end_pool = [], []

    p2_start_time_list, p2_end_time_list = [], []
    for k in range(0, len(p2_start_pool_list)):
        p2_start_time.append((p2_start_pool_list[k])[0])
        for m in range(1, len(p2_start_pool_list[k])):
            if datetime.strptime(str((p2_start_pool_list[k])[m]), '%Y-%m-%d %H:%M:%S') \
                    == datetime.strptime(str((p2_start_pool_list[k])[m - 1]), '%Y-%m-%d %H:%M:%S'):
                continue
            elif datetime.strptime(str((p2_end_pool_list[k])[m - 1]), '%Y-%m-%d %H:%M:%S') \
                    == datetime.strptime(str((p2_start_pool_list[k])[m]), '%Y-%m-%d %H:%M:%S'):
                continue
            else:
                p2_end_time.append((p2_end_pool_list[k])[m - 1])
                p2_start_time.append((p2_start_pool_list[k])[m])
        p2_end_time.append((p2_end_pool_list[k])[len((p2_end_pool_list[k])) - 1])
        p2_start_time_list.append(p2_start_time)
        p2_end_time_list.append(p2_end_time)
        p2_start_time = []
        p2_end_time = []

    p1_start_column, p1_end_column, p2_start_column, p2_end_column = [], [], [], []
    for i in range(0, len(p2_start_time_list)):
        for j in range(0, len(p2_start_time_list[i])):
            p1_start_column.append(p1_start_time[i])
            p1_end_column.append(p1_end_time[i])
            p2_start_column.append((p2_start_time_list[i])[j])
            p2_end_column.append((p2_end_time_list[i])[j])

    d = {'p1_start': p1_start_column, 'p1_end': p1_end_column,
         'p2_start': p2_start_column, 'p2_end': p2_end_column}
    df_new = pd.DataFrame(d)
    diff_list = []
    for i in range(0, len(p1_start_column)):
        diff = pd.Timedelta(p2_start_column[i] - p1_start_column[i]).total_seconds()/60
        diff_list.append(diff)
    df_new['difference'] = diff_list
    df_new['p1'] = id1
    df_new['p2'] = id2
    return df_new[['p1', 'p2', 'p1_start', 'p1_end', 'p2_start', 'p2_end', 'difference']]


def __merge_continuous_incident(df: pd.DataFrame, id1: int, id2: int):
    """
    Merge continuous interaction incidents after estimating duration
    :param df:
    :param id1:
    :param id2:
    :return:
    """
    pstart = df['start'].tolist()
    pend = df['end'].tolist()
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

    df_new = pd.DataFrame(list(zip(finalstart, finalend)), columns=['start', 'end'])
    df_new['p1'] = id1
    df_new['p2'] = id2
    df_new['no'] = np.arange(df_new.shape[0]) + 1
    df_new['duration'] = df_new['ed'] - df_new['start']
    df_new['duration'] = df_new['duration'].dt.total_seconds().div(60)
    return df_new[['no', 'p1', 'p2', 'start', 'end', 'duration']]


def durationEstimator(df: pd.DataFrame, id1: int, id2: int):
    """
    estimate duration of interation
    :param id2:
    :param id1:
    :param df:
    :return:
    """
    p1start = df['p1_t_start'].tolist()
    p1end = df['p1_t_end'].tolist()
    p2start = df['p2_t_start'].tolist()
    p2end = df['p2_t_end'].tolist()
    final_start, final_end, subsequenceOfInteraction = [], [], []
    time_difference = [(df['p2_t_start'] - df['p1_t_start']) / pd.Timedelta(hours=1)]
    time_group, diff_mean = [], []
    for i in range(0, len(p1start) - 1):  # identify subsequence of continuous interaction
        if datetime.strptime(str(p1start[i]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p1start[i + 1]),
                                                                                        '%Y-%m-%d %H:%M:%S'):
            subsequenceOfInteraction.extend([p1start[i], p1end[i], p1end[i + 1], p2start[i], p2end[i], p2start[i + 1],
                                             p2end[i + 1]])  # append all time in a candidate pool
            time_group.append(time_difference[0][i])

        elif datetime.strptime(str(p1end[i]), '%Y-%m-%d %H:%M:%S') == datetime.strptime(str(p1start[i + 1]),
                                                                                        '%Y-%m-%d %H:%M:%S'):
            subsequenceOfInteraction.extend([p1start[i], p1end[i], p1end[i + 1], p2start[i], p2end[i], p2start[i + 1],
                                             p2end[i + 1]])  # append all time in a candidate pool
            time_group.append(time_difference[0][i])
        else:
            if len(subsequenceOfInteraction) == 0:
                subsequenceOfInteraction.extend([p1start[i], p1end[i], p2start[i], p2end[i]])
            final_start.append(min(subsequenceOfInteraction))  # print(i,p1start[i],p1end[i],p1start[i+1],p1end[i+1])
            final_end.append(max(subsequenceOfInteraction))
            subsequenceOfInteraction = []
            time_group.append(time_difference[0][i])
            diff_mean.append(sum(time_group) / len(time_group))
            time_group = []
        if i == (len(p1start) - 2):
            time_group.append(time_difference[0][i + 1])
            diff_mean.append(sum(time_group) / len(time_group))
            time_group = []

    if len(subsequenceOfInteraction) != 0:
        final_start.append(min(subsequenceOfInteraction))
        final_end.append(max(subsequenceOfInteraction))
    if len(p1start) == 1:
        i = 0
        subsequenceOfInteraction.extend(
            [p1start[i], p1end[i], p2start[i], p2end[i]])  # append all time in a candidate pool
        final_start.append(min(subsequenceOfInteraction))
        final_end.append(max(subsequenceOfInteraction))
    df_new = pd.DataFrame(list(zip(final_start, final_end)), columns=['start', 'end'])
    df_new['p1'] = id1
    df_new['p2'] = id2
    df_new['no'] = np.arange(df_new.shape[0]) + 1
    df_new['duration'] = df_new['end'] - df_new['start']
    df_new['duration'] = df_new['duration'].dt.total_seconds().div(60)
    df_new = __merge_continuous_incident(df_new, id1, id2)
    #df_new['Mean_delay'] = diff_mean
    return df_new[['no', 'p1', 'p2', 'start', 'end', 'duration']]


def interaction_compute_speed_diff(df: pd.DataFrame):
    """
    compute the percentage difference in speed between two moving entities
    this speed is based on the instant speed between two points not the average speed over a kernel
    :param df:
    :return:
    """
    df['diff_speed'] = (df['p2_speed'] - df['p1_speed']).abs() / (
            (df['p1_speed'] + df['p2_speed']) / 2)
    # a higher value of percentage difference in speed indicates that two interacting entities move at
    # more different speeds
    return df


def interaction_compute_direction_diff(df: pd.DataFrame):
    """
    compute difference in moving direction between two moving entities
    :param df:
    :return:
    """

    # def between_angles(x, a):
    #     # The difference in movement direction of two interacting entities is between 0 and 180 degrees, with 0
    #     # degrees indicating an identical movement direction and 180 degrees indicating a completely opposite
    #     # movement direction.
    #     if x[a] >= 180:
    #         x[a] -= 360
    #     if x[a] < -180:
    #         x[a] += 360
    #     x[a] = abs(x[a])
    #     return x

    df['diff_direction'] = df['p2_direction'] - df['p1_direction']
    df['diff_direction'] = df['diff_direction'].apply(math.cos)
    return df


def interaction_compute_time_diff(df: pd.DataFrame):
    df['diff_time'] = (df['p2_t_start'] - df['p1_t_start'])/ pd.Timedelta(minutes=1)
    return df


class ORTEGA:
    # ORTEGA is the main class for interaction analysis, users need to initialize this object at the very beginning
    def __init__(
            self,
            data: pd.DataFrame,  # movement data of two entities
            minute_min_delay: float = 0,  # allowable minimum delay for intersecting PPAs, in minute
            minute_max_delay: float = 0,  # allowable maximum delay for intersecting PPAs, in minute
            start_time: str = None,  # use this when users want to select a segment of movement data
            end_time: str = None,  # use this when users want to select a segment of movement data
            max_el_time_min: float = 10000,  # PPA's interval greater than this value will be eliminated, in minute
            latitude_field: str = "latitude",  # specify the latitude field name
            longitude_field: str = "longitude",  # specify the longitude field name
            id_field: str = "pid",  # specify the id field name
            time_field: str = "time_local",  # time_field must include month, day, year, hour, minute, second
            speed_average: bool = False
            # kernel: List[int] = None,  # define a kernel for averaging speed when creating PPA (e.g., [1, 1, 2, 5])
    ):
        self.data = data
        self.start_time = start_time
        self.end_time = end_time
        self.latitude_field = latitude_field
        self.longitude_field = longitude_field
        self.id_field = id_field
        self.time_field = time_field
        self.minute_min_delay = minute_min_delay
        self.minute_max_delay = minute_max_delay
        self.max_el_time_min = max_el_time_min
        self.speed_average = speed_average
        # self.kernel = kernel
        self.__validate()
        self.__start()

    @property
    def minute_min_delay(self):
        return self._minute_min_delay

    @minute_min_delay.setter
    def minute_min_delay(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Parameter 'minute_min_delay' must be numeric!")
        if value < 0:
            raise ValueError("Parameter 'minute_min_delay' must be greater than zero!")
        self._minute_min_delay = value

    @property
    def minute_max_delay(self):
        return self._minute_max_delay

    @minute_max_delay.setter
    def minute_max_delay(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Parameter 'minute_max_delay' must be numeric!")
        if value <= 0:
            raise ValueError("Parameter 'minute_max_delay' must be greater than zero!")
        self._minute_max_delay = value

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
                raise ValueError("Incorrect 'start_time' format! Please use YYYY-MM-DD HH:MM:SS.")
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
                raise ValueError("Incorrect 'end_time' format! Please use YYYY-MM-DD HH:MM:SS.")
        self._end_time = value

    def __validate(self):
        """
        private function, only can be called in side the class
        """
        print(datetime.now(), 'Initializing ORTEGA object...')
        if not is_datetime64_dtype(self.data[self.time_field]):
            raise TypeError("Column 'time_field' is not datetime type! Please use "
                            "pd.to_datetime() to convert it to datetime.")

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

            # Check time overlap and lag, stop initialization if conditions are not met
            if not self.__check_time_lag_and_overlap():
                raise ValueError(f"Skipping pair {self.id1} and {self.id2} due to time lag greater than {self.minute_max_delay}!")

    def __start(self):
        """
        create PPAs for two moving objects (private method, only can be called inside the class)
        ellipses_list: all PPAs for two objects
        ellipses_list_id1: PPAs for object 1
        ellipses_list_id2: PPAs for object 2
        """
        self.ellipses_list = self.__get_ellipse_list(self.df1, self.df2)  # all ellipses for two objects
        self.ellipses_list_id1 = [i for i in self.ellipses_list if i.pid == self.id1]
        self.ellipses_list_id2 = [i for i in self.ellipses_list if i.pid == self.id2]
        # these do not exclude large PPAs! Only after __get_spatiotemporal_intersect_pairs() we exclude large PPAs
        print(datetime.now(), 'Initialization success!')

    def interaction_analysis(self):
        spatial_pairs = self.__get_spatial_intersect_pairs()
        all_intersection_pairs = get_timedelay_pairs(spatial_pairs, self.minute_min_delay, self.minute_max_delay)

        if not all_intersection_pairs:
            print(datetime.now(), 'Complete! No interaction found!')
            return None
        else:
            results = ORTEGAResults()
            results.set_intersection_ellipse_pair(all_intersection_pairs)
            print(datetime.now(), f'Complete! {len(all_intersection_pairs)} pairs of intersecting PPAs found!')

            # convert the list of intersecting ellipses to dataframe format - df_all_intersection_pairs
            df_all_intersection_pairs = intersect_ellipse_todataframe(all_intersection_pairs)
            df_all_intersection_pairs = interaction_compute_speed_diff(df_all_intersection_pairs)
            df_all_intersection_pairs = interaction_compute_direction_diff(df_all_intersection_pairs)
            df_all_intersection_pairs = interaction_compute_time_diff(df_all_intersection_pairs)
            results.set_df_all_intersection_pairs(df_all_intersection_pairs)

            # compute duration of interaction and output as a dataframe - df_duration
            print(datetime.now(), 'Compute continuous interaction events...')
            df_continues = check_continuous(df_all_intersection_pairs, self.id1, self.id2)
            print(datetime.now(), f'Complete! {df_continues.shape[0]} continuous interaction events identified!')
            if df_continues.shape[0] != 0:
                results.set_df_interaction_events(df_continues)
                return results
            else:
                return None

    def interaction_analysis2(self):
        # old method， voided but just keep it for reference
        print(datetime.now(), 'Implement interaction analysis...')
        spatial_pairs = self.__get_spatial_intersect_pairs()
        all_intersection_pairs = get_timedelay_pairs(spatial_pairs, self.minute_min_delay, self.minute_max_delay)
        if not all_intersection_pairs:
            print(datetime.now(), 'Complete! No interaction found!')
            return None
        else:
            print(datetime.now(), f'Complete! {len(all_intersection_pairs)} pairs of intersecting PPAs found!')
            results = ORTEGAResults()
            results.set_intersection_ellipse_pair(all_intersection_pairs)

            # convert the list of intersecting ellipses to dataframe format - df_all_intersection_pairs
            df_all_intersection_pairs = intersect_ellipse_todataframe(all_intersection_pairs)
            df_all_intersection_pairs = interaction_compute_speed_diff(df_all_intersection_pairs)
            df_all_intersection_pairs = interaction_compute_direction_diff(df_all_intersection_pairs)
            df_all_intersection_pairs = interaction_compute_time_diff(df_all_intersection_pairs)
            results.set_df_all_intersection_pairs(df_all_intersection_pairs)

            # compute duration of interaction and output as a dataframe - df_duration
            print(datetime.now(), 'Compute duration of interaction...')
            df_duration = durationEstimator(df_all_intersection_pairs, self.id1, self.id2)
            print(datetime.now(), f'Complete! {df_duration.shape[0]} interaction events identified!')
            if df_duration.shape[0] != 0:
                results.set_df_interaction_events(df_duration)
                return results
            else:
                return None

    def __check_time_lag_and_overlap(self):
        """
        Check time overlap and time lag between the movements of two individuals (private method, only can be called inside the class).
        Returns a boolean value indicating whether the time lag is less than or equal to the allowable maximum delay (True) or not (False).
        """
        # Extract the start and end times for each individual
        start1, end1 = self.df1[self.time_field].min(), self.df1[self.time_field].max()
        start2, end2 = self.df2[self.time_field].min(), self.df2[self.time_field].max()

        # Calculate the time overlap
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        overlap_duration = (overlap_end - overlap_start).total_seconds() / 60

        # Check if there is no overlap
        if overlap_duration <= 0:
            # Calculate the time lag
            time_lag = abs((start2 - end1).total_seconds() / 60) if end1 < start2 else abs((start1 - end2).total_seconds() / 60)
            # Check if time lag is greater than the max delay
            if time_lag > self.minute_max_delay:
                return False
        return True

    def __get_ellipse_list(self, df1: pd.DataFrame, df2: pd.DataFrame):
        """
        Create PPA ellipses using as input the two dataframes of GPS tracks of two moving objects
        :param df1: a pandas dataframe of GPS points of individual id1
        :param df2: a pandas dataframe of GPS points of individual id2
        :return:
        """
        print(datetime.now(), "Generate PPA list for the two moving entities...")
        ellipses_list_gen = EllipseList(self.latitude_field, self.longitude_field, self.id_field, self.time_field)

        # create PPA for df1, skip PPAs with large time interval
        ellipses_list_gen.generate(df1, max_el_time_min=self.max_el_time_min, speed_average=self.speed_average)
        # append PPA based on df2 to the above ellipses_list_gen object
        allPPAlist = ellipses_list_gen.generate(df2, max_el_time_min=self.max_el_time_min,
                                                speed_average=self.speed_average)
        print(datetime.now(), "Generating PPA list completed!")

        return allPPAlist  # return the whole list of PPAs
    '''
    def __get_spatiotemporal_intersect_pairs(self):
        print(datetime.now(), "Getting spatial and temporal intersection pairs...")
        intersection_pairs = get_spatiotemporal_intersect_pairs(self.ellipses_list_id1, self.ellipses_list_id2,
                                                                self.minute_delay)
        print(datetime.now(), "Getting spatial and temporal intersection pairs completed!")
        return intersection_pairs
    '''
    def __get_spatial_intersect_pairs(self):
        intersection_pairs = get_spatial_intersect_pairs(self.ellipses_list_id1, self.ellipses_list_id2)
        return intersection_pairs

    def compute_ppa_speed(self):
        speed_list = [
            [e.speed for e in self.ellipses_list_id1],
            [e.speed for e in self.ellipses_list_id2]
        ]
        print(f"Descriptive statistics of PPA ellipses length for id {self.id1}:")
        print(pd.Series(speed_list[0]).describe())
        print(f"Descriptive statistics of PPA ellipses length for id {self.id2}:")
        print(pd.Series(speed_list[1]).describe())
        return speed_list

    def compute_ppa_size(self):
        size_list = [
            [e.el.length for e in self.ellipses_list_id1],
            [e.el.length for e in self.ellipses_list_id2]
        ]
        print(f"Descriptive statistics of PPA ellipses length for id {self.id1}:")
        print(pd.Series(size_list[0]).describe())
        print(f"Descriptive statistics of PPA ellipses length for id {self.id2}:")
        print(pd.Series(size_list[1]).describe())
        return size_list

    def compute_ppa_interval(self):
        time_diff = [
            self.df1[self.time_field].diff().dt.total_seconds().div(60).dropna().loc[
                lambda x: x <= self.max_el_time_min],
            self.df2[self.time_field].diff().dt.total_seconds().div(60).dropna().loc[
                lambda x: x <= self.max_el_time_min]
        ]
        print(f"Descriptive statistics of PPA ellipses time interval (minutes) for id {self.id1}:")
        print(time_diff[0].describe())
        print(f"Descriptive statistics of PPA ellipses time interval (minutes) for id {self.id2}:")
        print(time_diff[1].describe())
        return time_diff
