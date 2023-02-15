from .ortega import ORTEGA
import math
from .common import __timedifcheck
from .common import __check_dist
import pandas as pd


def compute_ppa_size(interation: ORTEGA):
    size_list1 = [e.el[0].length for e in interation.ellipses_list_id1]
    size_list2 = [e.el[0].length for e in interation.ellipses_list_id2]
    print(f"Descriptive statistics of PPA ellipses length for id {interation.id1}:")
    print(pd.Series(size_list1).describe())
    print(f"Descriptive statistics of PPA ellipses length for id {interation.id2}:")
    print(pd.Series(size_list2).describe())
    return [size_list1, size_list2]


def compute_ppa_interval(interaction: ORTEGA):
    time_diff = [
        interaction.df1[interaction.time_field].diff().dt.total_seconds().div(60).dropna().loc[
            lambda x: x <= interaction.max_el_time_min],
        interaction.df2[interaction.time_field].diff().dt.total_seconds().div(60).dropna().loc[
            lambda x: x <= interaction.max_el_time_min]
    ]
    print(f"Descriptive statistics of PPA ellipses time interval (minutes) for id {interaction.id1}:")
    print(time_diff[0].describe())
    print(f"Descriptive statistics of PPA ellipses time interval (minutes) for id {interaction.id2}:")
    print(time_diff[1].describe())
    return time_diff


def compute_ppa_speed(df: pd.DataFrame):
    def compute_speed(x):
        d1 = __check_dist(x['P1_startlat'], x['P1_startlon'], x['P1_endlat'], x['P1_endlon'])
        delta_time1 = __timedifcheck(x['P1_t_start'], x['P1_t_end'])
        x['P1_speed'] = d1 / delta_time1  # speed in m/s
        d2 = __check_dist(x['P2_startlat'], x['P2_startlon'], x['P2_endlat'], x['P2_endlon'])
        delta_time2 = __timedifcheck(x['P2_t_start'], x['P2_t_end'])
        x['P2_speed'] = d2 / delta_time2  # speed in m/s
        return x

    df = df.apply(lambda x: compute_speed(x), axis=1)
    df['diff_speed'] = (df['P2_speed'] - df['P1_speed']).abs() / (
            (df['P1_speed'] + df['P2_speed']) / 2)
    print("Descriptive statistics of percentage difference in movement speed between intersecting PPAs:")
    print(df['diff_speed'].describe())
    return df


def compute_ppa_direction(df: pd.DataFrame):
    def compute_direction(x):
        # Angle between p1 and p2 in degree, Difference in x coordinates, Difference in y coordinates
        x['P1_direction'] = math.degrees(
            math.atan2(x['P1_endlon'] - x['P1_startlon'], x['P1_endlat'] - x['P1_startlat']))
        x['P2_direction'] = math.degrees(
            math.atan2(x['P2_endlon'] - x['P2_startlon'], x['P2_endlat'] - x['P2_startlat']))
        return x

    def between_angles(x, a):
        if x[a] >= 180:
            x[a] -= 360
        if x[a] < -180:
            x[a] += 360
        x[a] = abs(x[a])
        return x

    df = df.apply(lambda x: compute_direction(x), axis=1)
    df['diff_direction'] = df['P2_direction'] - df['P1_direction']
    df = df.apply(lambda x: between_angles(x, 'diff_direction'), axis=1)
    print("Descriptive statistics of difference in movement direction between intersecting PPAs:")
    print(df['diff_direction'].describe())
    return df

# from osgeo import ogr

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
