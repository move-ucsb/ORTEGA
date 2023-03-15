import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .ortega import ORTEGA
from .ellipses import Ellipse
from typing import List, Tuple
import matplotlib.patches as mpatches


def plot_original_tracks(interation: ORTEGA, save_plot: bool = False):
    """
    Visualize the original movement data with PPAs
    :param interation:
    :param save_plot:
    :return:
    """
    colors = ["#ff0000", "#0000ff"]
    fig = plt.figure(1, figsize=(8, 8), dpi=90)
    for i, collection in enumerate([interation.ellipses_list_id1, interation.ellipses_list_id2]):
        for item in collection:
            # if throw_out_big_ellipses and item.el[0].length > max_val:
            #     continue
            x, y = item.el.xy
            plt.plot(y, x, color=colors[i], alpha=0.5, linewidth=1, solid_capstyle="round")
            # PLOT THE POINTS USED TO MAKE THE ELLIPSES, TOO
            plt.plot([item.lon, item.last_lon], [item.lat, item.last_lat], "o-", color="grey", linewidth=0.5,
                     alpha=0.5, markersize=1)
    plt.xlabel("X", fontsize=14)
    plt.ylabel("Y", fontsize=14)
    plt.grid(True)
    plt.legend(handles=[mpatches.Patch(color=colors[0], label=interation.id1), mpatches.Patch(color=colors[1], label=interation.id2)])
    if save_plot:
        plt.savefig(f"{interation.id1}_{interation.id2}_original_tracks.pdf")
    plt.show()


def plot_interaction(interation: ORTEGA, all_intersection_pairs: List[Tuple[Ellipse, Ellipse]], save_plot: bool = False):
    """
    Visualize interaction. The PPAs of two moving individuals are shown using red and blue ellipses, respectively.
    PPA intersections marking potential interactions are highlighted using yellow ellipses.
    :param interation:
    :param all_intersection_pairs:
    :param save_plot:
    :return:
    """
    colors = ["#ff0000", "#0000ff"]
    interaction_color = "#f2ff00"  # yellow
    fig = plt.figure(1, figsize=(8, 8), dpi=90)
    for i, collection in enumerate([interation.ellipses_list_id1, interation.ellipses_list_id2]):
        for item in collection:
            # if throw_out_big_ellipses and item.el[0].length > max_val:
            #     continue
            x, y = item.el.xy
            plt.plot(y, x, color=colors[i], alpha=0.5, linewidth=1, solid_capstyle="round")
            # PLOT THE POINTS USED TO MAKE THE ELLIPSES, TOO
            plt.plot([item.lon, item.last_lon], [item.lat, item.last_lat], "o-", color="grey", linewidth=0.5,
                     alpha=0.5, markersize=1)
    for two_item in all_intersection_pairs:
        for item in two_item:
            x1, y1 = item.el.xy
            plt.plot(y1, x1, color=interaction_color, alpha=0.5, linewidth=1, solid_capstyle="round")
    plt.xlabel("X", fontsize=14)
    plt.ylabel("Y", fontsize=14)
    plt.grid(True)
    plt.legend(handles=[mpatches.Patch(color=colors[0], label=interation.id1),
                        mpatches.Patch(color=colors[1], label=interation.id2)])
    if save_plot:
        plt.savefig(f"{interation.id1}_{interation.id2}_interaction.pdf")
    plt.show()
