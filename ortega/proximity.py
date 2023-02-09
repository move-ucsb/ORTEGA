from datetime import timedelta
from .common import __check_dist
from .common import *


def proximity_interaction(df1: pd.DataFrame, df2: pd.DataFrame, minute_delay: float, distance_size: float,
                          latitude_field: str, longitude_field: str, time_field: str, id1: int, id2: int):
    '''

    :param df1:
    :param df2:
    :param minute_delay:
    :param distance_size: define buffer size in meter
    :param latitude_field: 
    :param longitude_field:
    :param time_field:
    :param id1:
    :param id2:
    :return:
    '''
    intersection_list = []
    for a, row in df1.iterrows():
        lf_lat, lf_lon, lf_ts = float(row[latitude_field]), float(row[longitude_field]), row[time_field]
        min_time = lf_ts - timedelta(seconds=minute_delay * 60)
        max_time = lf_ts + timedelta(seconds=minute_delay * 60)
        sub_df2 = df2[(df2[time_field] >= min_time) & (df2[time_field] <= max_time)]
        for b, others in sub_df2.iterrows():
            if __check_dist(lf_lat, lf_lon, float(others[latitude_field]), float(others[longitude_field])) \
                    < distance_size and abs((others[time_field] - lf_ts).seconds) < minute_delay * 60:
                intersection_list.append(tuple((id1, lf_ts, lf_lat, lf_lon, id2,
                                                others[time_field], others[latitude_field],
                                                others[longitude_field])))
    return pd.DataFrame(intersection_list, columns=["Person1", "Person1_time", "Person1_lat", "Person1_lon",
                                                    "Person2", "Person2_time", "Person2_lat", "Person2_lon"])


def merge_continuous_incident_proximity(df: pd.DataFrame, id1: int, id2: int, threshold_continuous_min: float):
    p1time = df['Person1_time'].tolist()
    p2time = df['Person2_time'].tolist()
    final_start, final_end = [], []
    subq, final_sub = [], []
    i = 0
    while i < len(p1time) - 1:
        if (p1time[i + 1] - p1time[i]).total_seconds() / 60.0 <= threshold_continuous_min:
            subq.extend([p1time[i], p2time[i], p1time[i + 1], p2time[i + 1]])
        else:
            if len(subq) != 0:
                final_sub.append(subq)
            else:
                final_sub.append([p1time[i], p2time[i]])
            subq = []
        i += 1
    if len(subq) != 0:
        final_sub.append(subq)
    if len(p1time) == 1:
        final_sub.append([p1time[0], p2time[0]])
    if p1time[-1] not in final_sub[-1]:
        final_sub.append([p1time[-1], p2time[-1]])
    for item in final_sub:
        final_start.append(min(item))
        final_end.append(max(item))

    df_new = pd.DataFrame(list(zip(final_start, final_end)), columns=['Start', 'End'])
    df_new['Person1'] = id1
    df_new['Person2'] = id2
    df_new['No'] = np.arange(df_new.shape[0]) + 1
    df_new['Duration_proxi'] = df_new['End'] - df_new['Start']
    df_new['Duration_proxi'] = df_new['Duration_proxi'].dt.total_seconds().div(60)
    return df_new[['No', 'Person1', 'Person2', 'Start', 'End', 'Duration_proxi']]


# def proximity(self, minute_delay: float = None, distance_size: float = 100.0):
#     """
#
#         :param minute_delay: allowable time difference between two GPS points of two individuals
#         :param distance_size: define buffer size in meter
#         :return:
#         """
#     if minute_delay is None:
#         minute_delay = self.minute_delay
#     return proximity_interaction(self.df1, self.df2, minute_delay, distance_size, self.latitude_field,
#                                  self.longitude_field, self.time_field, self.id1, self.id2)


# def proximity_duration(self, df1: pd.DataFrame, threshold_continuous_min: float = 2):
#     """
#         :param df1:
#         :param threshold_continuous_min: merge the subsequent interaction incidents if the time gap
#         between them is less than threshold_continuous_min
#         :return:
#         """
#     if df1.empty:
#         raise ValueError("The input dataframe is empty!")
#     return merge_continuous_incident_proximity(df1, self.id1, self.id2, threshold_continuous_min)
