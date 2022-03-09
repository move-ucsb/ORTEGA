from typing import List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import statistics

from ortega.ellipses import Ellipse, EllipseList

# make into Ellipse converters:
def __timedifcheck(t1: pd.Timestamp, t2: pd.Timestamp):
    return abs(pd.Timedelta(t2 - t1).total_seconds())


def __check_spatial_intersect(item: Ellipse, others: Ellipse) -> bool:
    return (
        item.el[0].intersects(others.el[0])
        or item.geom.within(others.geom)
        or others.geom.within(item.geom)
    )


def __check_temporal_intersect(
    item: Ellipse, item2: Ellipse, interaction_second_delay: float
) -> bool:
    return (
        item2.tig != item.tig
        and __timedifcheck(item.t1, item2.t1) <= interaction_second_delay
    )


def get_intersect_pairs(
    ellipses_list: List[Ellipse], personid: int, interaction_min_delay: float
) -> List[Tuple[Ellipse, Ellipse]]:
    interaction_second_delay = interaction_min_delay * 60

    intersection_pairs = []

    filtered_list = [i for i in ellipses_list if i.tig == personid]

    for count, item in enumerate(filtered_list, 1):

        # May 15,2020: ignore it if it's too big:
        if count % 500 == 0:
            print(f"\r > On item {count} of {len(filtered_list)}", end="")

        # if __timedifcheck(item.t1,item.t2)>max_el_timethres:
        #     continue

        # temporal intersect
        sub_ellipses_list = [
            item2
            for item2 in ellipses_list
            if __check_temporal_intersect(item, item2, interaction_second_delay)
        ]

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

    print()
    return intersection_pairs


def get_spatially_intersect_pairs(
    ellipses_list: List[Ellipse], personid: int, max_el_timethres: float
):
    intersection_pairs = []

    filtered_list = [i for i in ellipses_list if i.tig == personid]

    for count, item in enumerate(filtered_list, 1):
        # May 15,2020: ignore it if it's too big:
        if count % 500 == 0:
            print(f"\r > On item {count} of {len(filtered_list)}", end="")

        # if __timedifcheck(item.t1,item.t2)>max_el_timethres:
        #     continue

        sub_ellipses_list = [item2 for item2 in ellipses_list if item2.tig != item.tig]

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

    print()
    return intersection_pairs


def get_all_intersect_ellipse(intersection_df: List[Tuple[Ellipse, Ellipse]]):
    def columns_names(e: Ellipse, num: int):
        as_dict = e.to_dict()

        return {
            f"Person{num}": as_dict["tig"],
            f"Person{num}_t_start": as_dict["t2"],
            f"Person{num}_t_end": as_dict["t1"],
            f"Person{num}_endlat": as_dict["lat"],
            f"Person{num}_endlon": as_dict["lon"],
            f"Person{num}_startlat": as_dict["lastlat"],
            f"Person{num}_startlon": as_dict["lastlon"],
        }

    return pd.DataFrame(
        [
            {**columns_names(item, 1), **columns_names(item2, 2)}
            for item, item2 in intersection_df
        ]
    )


def compute_frequency_excludinglarge_ellipse(
    df1: pd.DataFrame, remove_large_ellipse: float = 180
) -> pd.DataFrame:
    df1["timediff1"] = df1["Person1_t_end"] - df1["Person1_t_start"]
    df1["timediff1"] = df1["timediff1"].dt.total_seconds() / 60
    df1["timediff2"] = df1["Person2_t_end"] - df1["Person2_t_start"]
    df1["timediff2"] = df1["timediff2"].dt.total_seconds() / 60

    return df1[
        (df1["timediff1"] <= remove_large_ellipse)
        & (df1["timediff2"] <= remove_large_ellipse)
    ]


def get_ellipses_in_date_range(
    animal1_ID: int,
    animal2_ID: int,
    start_time: str,
    end_time: str,
    ellipses_list: List[Ellipse],
    all_intersection_pairs: List[Tuple[Ellipse, Ellipse]],
) -> Tuple[List[Ellipse], List[Ellipse], List[Ellipse]]:

    ellipses_that_intersect = [
        item for items in all_intersection_pairs for item in items
    ]

    ellipses_within_time_range_animal1: List[Ellipse] = []
    ellipses_within_time_range_animal2: List[Ellipse] = []
    ellipses_that_intersect_within_time_range: List[Ellipse] = []

    start_time: pd.Timestamp = pd.to_datetime(start_time)
    end_time: pd.Timestamp = pd.to_datetime(end_time)
    time_diff_from_endtime = pd.Timedelta(start_time - end_time).total_seconds()

    for ellipse in ellipses_list:
        timediff1 = pd.Timedelta(ellipse.t2 - end_time).total_seconds()
        timediff2 = pd.Timedelta(ellipse.t1 - end_time).total_seconds()

        if (
            timediff1 > time_diff_from_endtime or timediff2 > time_diff_from_endtime
        ) and (timediff1 < 0 or timediff2 < 0):
            if ellipse.tig == animal1_ID:
                ellipses_within_time_range_animal1.append(ellipse)
            elif ellipse.tig == animal2_ID:
                ellipses_within_time_range_animal2.append(ellipse)

    for ellipse in ellipses_that_intersect:
        timediff1 = pd.Timedelta(ellipse.t2 - end_time).total_seconds()
        timediff2 = pd.Timedelta(ellipse.t1 - end_time).total_seconds()

        if (
            timediff1 > time_diff_from_endtime or timediff2 > time_diff_from_endtime
        ) and (timediff1 < 0 or timediff2 < 0):
            ellipses_that_intersect_within_time_range.append(ellipse)

    ellipses_that_intersect_within_time_range_set = list(
        set(ellipses_that_intersect_within_time_range)
    )

    return (
        ellipses_within_time_range_animal1,
        ellipses_within_time_range_animal2,
        ellipses_that_intersect_within_time_range_set,
    )


class ORTEGA:
    def __init__(
        self,
        data: pd.DataFrame,
        id1: int,
        id2: int,
        starttime: str,
        endtime: str,
        MAX_EL_TIMETHRESH: float = 1000000000000000,
        MINUTE_DELAY: float = 180,
        latitude_field: str = "Latitude",
        longitude_field: str = "Longitude",
        tiger_ID: str = "tid",
        timefield: str = "Time_LMT",
        position_identifier: str = "position",
        time_format: str = "%Y-%m-%d %H:%M:%S",
    ):
        self.data = data
        self.id1 = id1
        self.id2 = id2
        self.start_time = starttime
        self.end_time = endtime

        self.latitude_field = latitude_field
        self.longitude_field = longitude_field
        self.tiger_ID = tiger_ID
        self.timefield = timefield
        self.position_identifier = position_identifier
        self.time_format = time_format

        self.MINUTE_DELAY = MINUTE_DELAY
        self.MAX_EL_TIMETHRESH = MAX_EL_TIMETHRESH

        self.__start()

    def __start(self):
        df1 = self.data[self.data[self.tiger_ID] == self.id1]
        df2 = self.data[self.data[self.tiger_ID] == self.id2]

        self.ellipses_list = self.__get_ellipse_list(df1, df2)

        all_intersection_pairs1 = self.__get_intersect_pairs(df1, self.ellipses_list)
        # write to csv?:
        # df_allinter_ellipse = get_all_intersect_ellipse(all_intersection_pairs1)

        # all_intersection_pairs2 = self.__get_spatial_intersect_pairs(
        #     df1, self.ellipses_list
        # )
        # df_allinter_ellipse2 = get_all_intersect_ellipse(all_intersection_pairs2)
        # newdata1 = compute_frequency_excludinglarge_ellipse(df_allinter_ellipse2)

        (
            self.ellipses_within_time_range_animal1,
            self.ellipses_within_time_range_animal2,
            self.ellipses_that_intersect_within_time_range_set,
        ) = get_ellipses_in_date_range(
            self.id1,
            self.id2,
            self.start_time,
            self.end_time,
            self.ellipses_list,
            all_intersection_pairs1,
        )

    def __get_ellipse_list(self, df1: pd.DataFrame, df2: pd.DataFrame):
        ellipses_list_gen = EllipseList()
        ellipses_list_gen.generate(df1)
        return ellipses_list_gen.generate(df2)

    def __get_intersect_pairs(self, df: pd.DataFrame, ellipses_list: List[Ellipse]):
        print(f"Getting intersection pairs")
        return get_intersect_pairs(ellipses_list, self.id1, self.MINUTE_DELAY)

    def __get_spatial_intersect_pairs(
        self, df: pd.DataFrame, ellipses_list: List[Ellipse]
    ):
        print(f"Getting spatial intersection pairs")
        return get_spatially_intersect_pairs(
            ellipses_list, self.id1, self.MAX_EL_TIMETHRESH
        )

    def report(self):
        data = self.__report_gen()
        print(f"Mean polygon length in the ellipses list: {data['mean']}")
        print(f"Std Deviation polygon length in the ellipses list: {data['stdev']}")
        print(
            f"Max polygon length (mean + 3 sd) in the ellipses list: {data['max_val']}"
        )

    def __report_gen(self):
        size_list = [e.el[0].length for e in self.ellipses_list]

        return {
            "stdev": statistics.stdev(size_list),
            "mean": statistics.mean(size_list),
            "max_val": statistics.mean(size_list) + 3 * statistics.stdev(size_list),
        }

    def plot(self, throw_out_big_ellipses: bool = True):

        ellipsecollection = [
            self.ellipses_within_time_range_animal1,
            self.ellipses_within_time_range_animal2,
            self.ellipses_that_intersect_within_time_range_set,
        ]

        color1 = "#ff0000"  # "#3ABA36" #green #
        color2 = "#0000ff"  # "#ff0000" #red %"#005EFF" #blue #"
        interaction_color = "#f2ff00"  # yellow
        colors = [color1, color2, interaction_color]

        max_val: float = self.__report_gen()["max_val"]

        fig = plt.figure(1, figsize=(8, 8), dpi=90)
        # ax = fig.add_subplot(111)

        for i, collection in enumerate(ellipsecollection):
            colorpicked = colors[i]

            for item in collection:
                if throw_out_big_ellipses and item.el[0].length > max_val:
                    continue

                x, y = item.el[0].xy
                # ax = fig.add_subplot(111)
                plt.plot(
                    y,
                    x,
                    color=colorpicked,
                    alpha=0.8,
                    linewidth=1,
                    solid_capstyle="round",
                )

                # PLOT THE POINTS USED TO MAKE THE ELLIPSES, TOO
                plt.plot(
                    [item.lon, item.lastlon],
                    [item.lat, item.lastlat],
                    "o-",
                    color="grey",
                    linewidth=0.5,
                    markersize=1,
                )

        plt.axis("equal")
        plt.axis("on")
        # plt.title('')
        plt.xlabel("Longitude", fontsize=14)
        plt.ylabel("Latitude", fontsize=14)
        plt.grid(True)
        # plt.savefig("tiger20080_20083_interaction.pdf")
        plt.show()

        return fig
