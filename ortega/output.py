from .ellipses import Ellipse
from typing import List, Tuple
from .common import *


def _extract_attributes(df: pd.DataFrame, col: str, method: str):
    VALID_METHODS = {'mean', 'difference'}
    if method not in VALID_METHODS:
        raise ValueError("results: method must be one of %r." % VALID_METHODS)

    def mean(row):
        row['p1_attrs_' + col] = (row['p1_start_attrs'][col] + row['p1_end_attrs'][col]) / 2
        row['p2_attrs_' + col] = (row['p2_start_attrs'][col] + row['p2_end_attrs'][col]) / 2
        row['attrs_mean_' + col] = (row['p1_attrs_' + col] + row['p2_attrs_' + col])/2
        return row

    def difference(row):
        row['p1_attrs_' + col] = (row['p1_start_attrs'][col] + row['p1_end_attrs'][col]) / 2
        row['p2_attrs_' + col] = (row['p2_start_attrs'][col] + row['p2_end_attrs'][col]) / 2
        row['attrs_diff_' + col] = row['p1_attrs_' + col] - row['p2_attrs_' + col]
        return row

    if method == 'mean':
        df = df.apply(lambda row: mean(row), axis=1)
    if method == 'difference':
        df = df.apply(lambda row: difference(row), axis=1)
    return df


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

    def extract_attributes(self, col: str, method: str):
        self.df_all_intersection_pairs = _extract_attributes(self.df_all_intersection_pairs, col, method)
