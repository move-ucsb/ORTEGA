from .ellipses import Ellipse
from typing import List, Tuple
from .common import *


class ORTEGAResults:
    def __init__(
            self,
            intersection_ellipse_pair: List[Tuple[Ellipse, Ellipse]] = None,
            df_all_intersection_pairs: pd.DataFrame = None,
            df_interaction_events: pd.DataFrame = None

    ):
        self.df_all_intersection_pairs = df_all_intersection_pairs
        self.intersection_ellipse_pair = intersection_ellipse_pair
        self.df_interaction_events = df_interaction_events

    def set_intersection_ellipse_pair(self, row: List[Tuple[Ellipse, Ellipse]]):
        self.intersection_ellipse_pair = row

    def set_df_all_intersection_pairs(self, row: pd.DataFrame):
        self.df_all_intersection_pairs = row

    def set_df_interaction_events(self, row: pd.DataFrame):
        self.df_interaction_events = row

    def compute_interaction_duration(self):
        self.df_interaction_events['duration'] = self.df_interaction_events[["p1_end", "p2_end"]].max(axis=1) - self.df_interaction_events[["p1_start", "p2_start"]].min(axis=1)
        self.df_interaction_events['duration'] = self.df_interaction_events['duration'].dt.total_seconds().div(60)
        print(datetime.now(), f'Computing interaction duration complete!')

