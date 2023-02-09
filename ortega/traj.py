import geopandas as gpd


def points_to_traj(traj_points, col=['Lng', 'Lat', 'ID'], timecol=None):
    '''
    Input trajectory, generate GeoDataFrame
    Parameters
    -------
    traj_points : DataFrame
        trajectory data
    col : List
        The column name, in the sequence of [lng, lat,trajectoryid]
    timecol : str(Optional)
        Optional, the column name of the time column. If given, the geojson
        with [longitude, latitude, altitude, time] in returns can be put into
        the Kepler to visualize the trajectory
    Returns
    -------
    traj : GeoDataFrame
        Generated trajectory
    '''
    [Lng, Lat, ID] = col
    if timecol:
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID] == i][[Lng, Lat, timecol]]
            coords[timecol] = coords[timecol].apply(
                lambda r: int(r.value / 1000000000))
            coords['altitude'] = 0
            coords = coords[[Lng, Lat, 'altitude', timecol]].values.tolist()
            traj_id.append(i)
            if len(coords) >= 2:
                geometry.append({
                    "type": "Feature",
                    "properties": {"ID": i},
                    "geometry": {"type": "LineString",
                                 "coordinates": coords}})
        traj = {"type": "FeatureCollection",
                "features": geometry}
    else:
        traj = gpd.GeoDataFrame()
        from shapely.geometry import LineString
        geometry = []
        traj_id = []
        for i in traj_points[ID].drop_duplicates():
            coords = traj_points[traj_points[ID] == i][[Lng, Lat]].values
            traj_id.append(i)
            if len(coords) >= 2:
                geometry.append(LineString(coords))
            else:
                geometry.append(None)  # pragma: no cover
        traj[ID] = traj_id
        traj['geometry'] = geometry
        traj = gpd.GeoDataFrame(traj)
    return traj
