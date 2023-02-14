import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from .traj import *
from .ortega import ORTEGA
# from keplergl import KeplerGl
# from matplotlib.animation import FuncAnimation


def plot_original_tracks(interation: ORTEGA, throw_out_big_ellipses: bool = True, legend: bool = True,
                         save_plot: bool = False):
    color1 = "#ff0000"
    color2 = "#0000ff"
    colors = [color1, color2]
    fig = plt.figure(1, figsize=(8, 8), dpi=90)
    fig.set_tight_layout(True)

    for i, collection in enumerate([interation.ellipses_list_id1, interation.ellipses_list_id2]):
        color_picked = colors[i]
        for item in collection:
            if throw_out_big_ellipses and abs(
                    pd.Timedelta(item.t2 - item.t1).total_seconds()) >= interation.max_el_time_min * 60:
                continue
            # if throw_out_big_ellipses and item.el[0].length > max_val:
            #     continue
            x, y = item.el[0].xy
            plt.plot(y, x, color=color_picked, alpha=0.8, linewidth=1, solid_capstyle="round")
            # PLOT THE POINTS USED TO MAKE THE ELLIPSES, TOO
            plt.plot([item.lon, item.last_lon], [item.lat, item.last_lat], "o-", color="grey", linewidth=0.5,
                     markersize=1)

    # plt.title('')
    plt.xlabel("Longitude", fontsize=14)
    plt.ylabel("Latitude", fontsize=14)
    plt.grid(True)
    if legend:
        color1_patch = mpatches.Patch(color=color1, label=interation.id1)
        color2_patch = mpatches.Patch(color=color2, label=interation.id2)
        plt.legend(handles=[color1_patch, color2_patch])
    if save_plot:
        plt.savefig(f"{interation.id1}_{interation.id2}_original_tracks.pdf")
    plt.show()


def plot_interaction(interation: ORTEGA, throw_out_big_ellipses: bool = True,
                     legend: bool = True, save_plot: bool = False):
    color1 = "#ff0000"  # "#3ABA36" #green #
    color2 = "#0000ff"  # "#ff0000" #red %"#005EFF" #blue #"
    interaction_color = "#f2ff00"  # yellow
    colors = [color1, color2]
    fig = plt.figure(1, figsize=(8, 8), dpi=90)
    # fig.set_tight_layout(True)

    for i, collection in enumerate([interation.ellipses_list_id1, interation.ellipses_list_id2]):
        color_picked = colors[i]
        for item in collection:
            if throw_out_big_ellipses and abs(
                    pd.Timedelta(item.t2 - item.t1).total_seconds()) >= interation.max_el_time_min * 60:
                continue
            # if throw_out_big_ellipses and item.el[0].length > max_val:
            #     continue
            x, y = item.el[0].xy
            plt.plot(y, x, color=color_picked, alpha=0.8, linewidth=1, solid_capstyle="round")
            # PLOT THE POINTS USED TO MAKE THE ELLIPSES, TOO
            plt.plot([item.lon, item.last_lon], [item.lat, item.last_lat], "o-", color="grey", linewidth=0.5,
                     markersize=1)

    for two_item in interation.all_intersection_pairs:
        for item in two_item:
            if throw_out_big_ellipses and abs(
                    pd.Timedelta(item.t2 - item.t1).total_seconds()) >= interation.max_el_time_min * 60:
                continue
            x1, y1 = item.el[0].xy
            plt.plot(y1, x1, color=interaction_color, alpha=0.8, linewidth=1, solid_capstyle="round")
            plt.plot([item.lon, item.last_lon], [item.lat, item.last_lat], "o-", color="grey", linewidth=0.5,
                     markersize=1)
    # plt.title('')
    plt.xlabel("Longitude", fontsize=14)
    plt.ylabel("Latitude", fontsize=14)
    plt.grid(True)
    if legend:
        color1_patch = mpatches.Patch(color=color1, label=interation.id1)
        color2_patch = mpatches.Patch(color=color2, label=interation.id2)
        plt.legend(handles=[color1_patch, color2_patch])
    if save_plot:
        plt.savefig(f"{interation.id1}_{interation.id2}_interaction.pdf")
    plt.show()


def visualization_trip(interaction, zoom='auto', height=500):
    '''
    The input is the trajectory data and the column name. The output is the
    visualization result based on kepler
    Parameters
    -------
    interaction :

    zoom : number
        Map zoom level
    height : number
        The height of the map frame
    Returns
    -------
    vmap : keplergl.keplergl.KeplerGl
        Visualizations provided by keplergl
    '''
    print('Processing movement data...')
    Lng, Lat, ID, timecol = interaction.longitude_field, interaction.latitude_field, interaction.id_field, interaction.time_field

    if interaction.start_time is not None or interaction.end_time is not None:
        trajdata = interaction.subset
    else:
        trajdata = interaction.data

    # clean data
    trajdata = trajdata[-((trajdata[Lng].isnull()) | (trajdata[Lat].isnull()))]
    trajdata = trajdata[
        (trajdata[Lng] >= -180) & (trajdata[Lng] <= 180) & (trajdata[Lat] >= -90) & (trajdata[Lat] <= 90)]

    trajdata[timecol] = pd.to_datetime(trajdata[timecol])

    trajdata = trajdata.sort_values(by=[ID, timecol])
    traj = points_to_traj(trajdata, col=[Lng, Lat, ID], timecol=timecol)
    ls = []
    for i in range(len(traj['features'])):
        ls.append(traj['features'][i]['geometry']['coordinates'][0])
        ls.append(traj['features'][i]['geometry']['coordinates'][-1])
    ls = pd.DataFrame(ls)
    lon_center, lat_center, starttime = ls[0].mean(), ls[1].mean(), ls[3].min()
    if zoom == 'auto':
        lon_min, lon_max = ls[0].quantile(0.05), ls[0].quantile(0.95)
        zoom = 8.5 - np.log(lon_max - lon_min) / np.log(2)
    print('Generate visualization...')
    vmap = KeplerGl(config={
        "version": "v1",
        "config":
            {"visState":
                {
                    "filters": [],
                    "layers": [
                        {
                            "id": "hizm36i",
                            "type": "trip",
                            "config":
                                {
                                    "dataId": "trajectory",
                                    "label": "trajectory",
                                    # "color": [255, 255, 255],
                                    # "highlightColor": [255, 255, 0, 255],
                                    "columns":
                                        {
                                            "geojson": "_geojson"
                                        },
                                    "isVisible": True,
                                    "visConfig": {
                                        "opacity": 0.8,
                                        "thickness": 5,
                                        "colorRange": {
                                            "name": "ColorBrewer Set1-6",
                                            "type": "qualitative",
                                            "category": "ColorBrewer",
                                            "colors": [
                                                "#e41a1c",
                                                "#377eb8",
                                                "#4daf4a",
                                                "#984ea3",
                                                "#ff7f00",
                                                "#ffff33",
                                            ],
                                        },
                                        "trailLength": 1000,
                                        "sizeRange": [0, 10],
                                    },
                                },
                            "visualChannels": {
                                "colorField": {"name": "ID", "type": "integer"},
                                "colorScale": "quantile",
                                "sizeField": None,
                                "sizeScale": "linear",
                            },
                        }],
                    "layerBlending": "additive",
                    "animationConfig":
                        {
                            "currentTime": starttime,
                            "speed": 0.1
                        }
                },
                "mapState":
                    {
                        "bearing": 0,
                        "latitude": lat_center,
                        "longitude": lon_center,
                        "pitch": 0,
                        "zoom": zoom,
                    },
                "mapStyle": {
                    "styleType": "satellite"  # outdoors, streets
                }
            }},
        data={'trajectory': traj}, height=height)
    return vmap

# def plot_interaction_animated(all_intersection_pairs: List[Tuple[Ellipse, Ellipse]], ellipses_list_id1: List[Ellipse],
#                               ellipses_list_id2: List[Ellipse], boundary: [[float, float], [float, float]],
#                               id1: int, id2: int, max_el_time_min: float,
#                               throw_out_big_ellipses: bool = True, legend: bool = True, save_plot: bool = False):
#     color1 = "#ff0000"
#     color2 = "#0000ff"
#     colors = [color1, color2]
#     # fig = plt.figure(1, figsize=(8, 8), dpi=90)
#     fig, ax = plt.subplots(figsize=(8, 8))
#     fig.set_tight_layout(True)
#     plt.xlabel("Longitude", fontsize=14)
#     plt.ylabel("Latitude", fontsize=14)
#     plt.grid(True)
#     plt.xlim(boundary[0])
#     plt.ylim(boundary[1])
#     if legend:
#         color1_patch = mpatches.Patch(color=color1, label=id1)
#         color2_patch = mpatches.Patch(color=color2, label=id2)
#         plt.legend(handles=[color1_patch, color2_patch])
#
#     # print(len(ellipses_list_id1), len(ellipses_list_id2))
#     # boundary = [[min_lon - 0.01, max_lon + 0.01], [min_lat - 0.01, max_lat + 0.01]]
#
#     # G = ox.graph_from_bbox(boundary[1][1], boundary[1][0], boundary[0][1], boundary[0][0], network_type='all')
#     # ox.plot_graph(G, ax=ax, dpi=300, show=False, close=False, node_size=0, bgcolor='white', edge_color='gray',
#     #               edge_linewidth=0.5)
#
#     def animate(i, x=[], y=[]):
#         # if i % 5 == 0:
#         #     plt.cla()
#         # concerns: length of the two lists, temporal order of two lists needs to be consistent?
#         # based on days
#         min_len = min(len(ellipses_list_id1), len(ellipses_list_id2))
#         max_len = max(len(ellipses_list_id1), len(ellipses_list_id2))
#
#         if i < min_len:
#             for j, item in enumerate([ellipses_list_id1[i], ellipses_list_id2[i]]):
#                 if throw_out_big_ellipses and abs(
#                         pd.Timedelta(item.t2 - item.t1).total_seconds()) >= max_el_time_min * 60:
#                     pass
#                 else:
#                     x, y = item.el[0].xy
#                     plt.plot(y, x, color=colors[j], alpha=0.8, linewidth=1, solid_capstyle="round")
#                     plt.plot([item.lon, item.last_lon], [item.lat, item.last_lat], "o-", color="grey", linewidth=0.5,
#                              markersize=1)
#         elif i < max_len:
#             if len(ellipses_list_id1) > len(ellipses_list_id2):
#                 item = ellipses_list_id1[i]
#                 k = 0
#             else:
#                 item = ellipses_list_id2[i]
#                 k = 1
#
#             if throw_out_big_ellipses and abs(
#                     pd.Timedelta(item.t2 - item.t1).total_seconds()) >= max_el_time_min * 60:
#                 pass
#             else:
#                 x, y = item.el[0].xy
#                 plt.plot(y, x, color=colors[k], alpha=0.8, linewidth=1, solid_capstyle="round")
#                 plt.plot([item.lon, item.last_lon], [item.lat, item.last_lat], "o-", color="grey", linewidth=0.5,
#                          markersize=1)
#
#     ani = FuncAnimation(fig, animate, interval=300)
#     plt.show()
#     if save_plot:
#         ani.to_html5_video()
