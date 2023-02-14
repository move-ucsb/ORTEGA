import statistics
from .ortega import ORTEGA
import math
from .common import __timedifcheck
from .common import __check_dist
import pandas as pd
import utm

from geographiclib.geodesic import Geodesic
Geo = Geodesic.WGS84

# from osgeo import ogr
# import seaborn
# import matplotlib.pyplot as plt


def compute_ppa_size(interation: ORTEGA):
    size_list1 = [e.el[0].length for e in interation.ellipses_list_id1]
    size_list2 = [e.el[0].length for e in interation.ellipses_list_id2]
    id1 = interation.id1
    id2 = interation.id2

    ellipse_size_collection = {"size_list1": size_list1, "size_list2": size_list2}
    print(f"Statistics of PPA ellipses length for id {id1}:")
    print(f"mean:", statistics.mean(ellipse_size_collection['size_list1']))
    print(f"min:", min(ellipse_size_collection['size_list1']))
    print(f"max:", max(ellipse_size_collection['size_list1']))
    print(f"median:", statistics.median(ellipse_size_collection['size_list1']))
    print(f"std:", statistics.stdev(ellipse_size_collection['size_list1']))
    print(f"Statistics of PPA ellipses length for id {id2}:")
    print(f"mean:", statistics.mean(ellipse_size_collection['size_list2']))
    print(f"min:", min(ellipse_size_collection['size_list2']))
    print(f"max:", max(ellipse_size_collection['size_list2']))
    print(f"median:", statistics.median(ellipse_size_collection['size_list2']))
    print(f"std:", statistics.stdev(ellipse_size_collection['size_list2']))
    # if plot:
    #     plt.rcParams.update({'font.size': 14})
    #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    #     seaborn.violinplot(data=ellipse_size_collection['size_list1'], ax=ax1)
    #     seaborn.violinplot(data=ellipse_size_collection['size_list2'], ax=ax2)
    #     ax1.set_xticklabels([str(id1)])
    #     ax2.set_xticklabels([str(id2)])
    #     plt.show()
    return ellipse_size_collection


def compute_ppa_interval(interation: ORTEGA):
    id1 = interation.id1
    id2 = interation.id2
    print(f"Statistics of PPA ellipses time interval (minutes) for id {id1}:")
    time_diff = [
        interation.df1[interation.time_field].diff().dt.total_seconds().div(60).dropna(),
        interation.df2[interation.time_field].diff().dt.total_seconds().div(60).dropna()
    ]
    print(f"mean:", time_diff[0].mean())
    print(f"min:", time_diff[0].min())
    print(f"max:", time_diff[0].max())
    print(f"median:", time_diff[0].median())
    print(f"std:", time_diff[0].std())

    print(f"Statistics of PPA ellipses time interval (minutes) for id {id2}:")
    print(f"mean:", time_diff[1].mean())
    print(f"min:", time_diff[1].min())
    print(f"max:", time_diff[1].max())
    print(f"median:", time_diff[1].median())
    print(f"std:", time_diff[1].std())
    # if plot:
    #     plt.rcParams.update({'font.size': 14})
    #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    #     seaborn.violinplot(data=time_diff[0].tolist(), ax=ax1)
    #     seaborn.violinplot(data=time_diff[1].tolist(), ax=ax2)
    #     ax1.set_xticklabels([str(id1)])
    #     ax2.set_xticklabels([str(id2)])
    #     ax1.set_ylabel('Interval (min)')
    #     ax2.set_ylabel('Interval (min)')
    #     plt.show()
    return time_diff


def compute_ppa_speed(df: pd.DataFrame):
    def compute_speed(x):
        d1 = __check_dist(x['P1_startlat'], x['P1_startlon'], x['P1_endlat'], x['P1_endlon'])
        delta_time1 = __timedifcheck(x['P1_t_start'], x['P1_t_end'])
        x['P1_speed'] = d1 / delta_time1
        d2 = __check_dist(x['P2_startlat'], x['P2_startlon'], x['P2_endlat'], x['P2_endlon'])
        delta_time2 = __timedifcheck(x['P2_t_start'], x['P2_t_end'])
        x['P2_speed'] = d2 / delta_time2 #m/s
        return x

    df = df.apply(lambda x: compute_speed(x), axis=1)
    df['diff_speed'] = (df['P2_speed'] - df['P1_speed']).abs() / (
                (df['P1_speed'] + df['P2_speed']) / 2)
    print("Statistics of percentage difference in movement speed between intersecting PPAs:")
    print(df['diff_speed'].describe())
    return df


def compute_ppa_direction(df: pd.DataFrame):
    def compute_direction(x):
        p1_start = utm.from_latlon(x['P1_startlat'], x['P1_startlon'])
        p1_end = utm.from_latlon(x['P1_endlat'], x['P1_endlon'])
        # Angle between p1 and p2 in degree, Difference in x coordinates, Difference in y coordinates
        x['P1_direction'] = math.degrees(math.atan2(p1_end[0] - p1_start[0], p1_end[1] - p1_start[1]))
        p2_start = utm.from_latlon(x['P2_startlat'], x['P2_startlon'])
        p2_end = utm.from_latlon(x['P2_endlat'], x['P2_endlon'])
        x['P2_direction'] = math.degrees(math.atan2(p2_end[0] - p2_start[0], p2_end[1] - p2_start[1]))
        return x

    def between_angles(x, a):
        if x[a] >= 180:
            x[a] -= 360
        if x[a] < -180:
            x[a] += 360
        x[a] = abs(x[a])
        return x

    df = df.apply(lambda x: compute_direction(x), axis=1)
    df['diff_angle'] = df['P2_direction'] - df['P1_direction']
    df = df.apply(lambda x: between_angles(x, 'diff_angle'), axis=1)
    print("Statistics of difference in movement direction between intersecting PPAs:")
    print(df['diff_angle'].describe())
    return df

# def output_shapefile(interation: ORTEGA):
#     # Now convert it to a shapefile with OGR
#     driver = ogr.GetDriverByName('Esri Shapefile')
#     id1 = interation.id1
#     id2 = interation.id2
#     ds = driver.CreateDataSource(f"{id1}_{id2}.shp")
#     layer = ds.CreateLayer('', None, ogr.wkbPolygon)
#     # Add one attribute
#     layer.CreateField(ogr.FieldDefn('pid', ogr.OFTInteger))
#     layer.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
#     layer.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
#     layer.CreateField(ogr.FieldDefn('time', ogr.OFTString))
#     layer.CreateField(ogr.FieldDefn('last_lat', ogr.OFTReal))
#     layer.CreateField(ogr.FieldDefn('last_lon', ogr.OFTReal))
#     layer.CreateField(ogr.FieldDefn('last_time', ogr.OFTString))
#     layer.CreateField(ogr.FieldDefn('ppa_id', ogr.OFTInteger))
#     defn = layer.GetLayerDefn()
#
#     i = 0
#     for item in interation.ellipses_list:
#         if abs(pd.Timedelta(item.t2 - item.t1).total_seconds()) > interation.max_el_time_min * 60:
#             continue
#         # Create a new feature (attribute and geometry)
#         feat = ogr.Feature(defn)
#         i += 1
#         feat.SetField('pid', item.pid)
#         feat.SetField('lat', item.lat)
#         feat.SetField('lon', item.lon)
#         feat.SetField('last_lat', item.last_lat)
#         feat.SetField('last_lon', item.last_lon)
#         feat.SetField('time', str(item.t1))
#         feat.SetField('last_time', str(item.t2))
#         # feat.SetField('time', item.t1.year, item.t1.month, item.t1.day, item.t1.hour, item.t1.minute, item.t1.second, 0)
#         # feat.SetField('last_time', item.t2.year, item.t2.month, item.t2.day, item.t2.hour, item.t2.minute, item.t2.second, 0)
#         feat.SetField('ppa_id', i)
#
#         # Make a geometry, from Shapely object
#         geom = ogr.CreateGeometryFromWkb(item.geom.wkb)
#         feat.SetGeometry(geom)
#         layer.CreateFeature(feat)
#         feat = geom = None  # destroy these
#     # Save and close everything
#     ds = layer = feat = geom = None