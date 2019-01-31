import numpy as np
import pandas as pd


def subset_nets(df, cat_code):
    """Subset the NETS based on the prescence of a category"""
    return df[df["adr_net_{}_c_2014".format(cat_code.lower())] == 1]


def num_business_1990(df):
    """'Finds the number of businesses present in 1990 to establish a baseline"""
    total = df.loc[df["adr_net_firstyear_x_2014"] == 1990] \
        .groupby("t10_cen_uid_u_2010") \
        .size()

    # reformat to long for easier aggregation
    id_vars = ["adr_net_behid_u_2014", "adr_net_firstyear_x_2014", "t10_cen_uid_u_2010"]
    value_vars = ["adr_net_acth_c_2014", "adr_net_walh_c_2014", "adr_net_ffah_c_2014"]
    melted = df.melt(id_vars=id_vars, value_vars=value_vars,
                     var_name="business_class", value_name="num_businesses") \
        .sort_values(["adr_net_behid_u_2014", "adr_net_firstyear_x_2014"]) \
        .loc[lambda df: df["adr_net_firstyear_x_2014"] == 1990] \
        .reset_index(drop=True)

    cols = ["t10_cen_uid_u_2010", "business_class", "num_businesses"]
    tract_sums = melted.loc[:, cols] \
        .groupby(["t10_cen_uid_u_2010", "business_class"]) \
        .sum() \
        .unstack()

    # Reformat columns to strip away RECVD formatting
    tract_sums.columns = [x.split("_")[2].upper() for x in tract_sums.columns.droplevel(0).tolist()]

    tract_sums["TOTAL"] = total

    return tract_sums


def enter_exit(df, subset_cat="Total", interval_length=None):
    """Define the number of businesses that entered and exited all census tracts per time period"""

    if subset_cat != "Total":
        df = subset_nets(df, subset_cat)

    # Enter and exit year per business per tract
    business_rate = df.replace({"adr_net_lastyear_x_2014": 2014}, np.nan) \
        .replace({"adr_net_firstyear_x_2014": 1990}, np.nan) \
        .groupby(["adr_net_dunsnumber_x_2014", "t10_cen_uid_u_2010"]).agg({
        'adr_net_firstyear_x_2014': lambda x: min(x) - 1,  # interval consistency correction
        'adr_net_lastyear_x_2014': max
    }) \
        .set_axis(["enter_year", "exit_year"], axis="columns", inplace=False)

    enter_year = business_rate.reset_index(drop=False).groupby(["t10_cen_uid_u_2010", "enter_year"]) \
        .size() \
        .rename_axis(["t10_cen_uid_u_2010", "year"], axis="index") \
        .rename("enter_year")
    idx_enter = enter_year.index
    enter_year.index.set_levels(idx_enter.levels[-1].astype(int), level="year", inplace=True)

    exit_year = business_rate.reset_index(drop=False).groupby(["t10_cen_uid_u_2010", "exit_year"]) \
        .size() \
        .rename_axis(["t10_cen_uid_u_2010", "year"], axis="index") \
        .rename("exit_year") \

    # Change year index to int for datetime conversion
    idx_exit = exit_year.index
    exit_year.index.set_levels(idx_exit.levels[-1].astype(int), level="year", inplace=True)

    # Enter and exit count per tract per year
    df_tract_year_count = pd.concat([enter_year, exit_year], axis=1) \
        .reset_index() \
        .assign(year=lambda x: pd.to_datetime(x.year, format="%Y")) \
        .set_index(["t10_cen_uid_u_2010", "year"])

    if interval_length:
        # new index with all tract/year combos
        all_tracts = df_tract_year_count.index.levels[0]
        idx_full = pd.MultiIndex.from_product([all_tracts,
                                              pd.to_datetime(range(1990, 2105), format="%Y")],
                                              names=["t10_cen_uid_u_2010", "year"])

        df_tract_year_count = df_tract_year_count \
            .reindex(idx_full) \
            .groupby(level=0) \
            .resample("{}Y".format(interval_length), level=1)\
            .sum() \
            .loc[(slice(None), slice("1/1/1990", "12/31/2014")), :]

    df_tract_year_count.index.set_levels(df_tract_year_count.index.levels[1].year, level=1, inplace=True)
    df_tract_year_count.columns = pd.MultiIndex.from_product([[subset_cat.upper()], df_tract_year_count.columns])

    return df_tract_year_count


def enter_exit_multicat(df, cat_list, interval_length=None):
    """Returns entry and exit rates for all categories with a given interval length"""

    df_list = [enter_exit(df, subset_cat=cat, interval_length=interval_length) for cat in cat_list]
    enter_exit_all = pd.concat(df_list, axis=1).fillna(0)

    # set data we can't know to NA
    enter_exit_all.loc[(slice(None), 1990), (slice(None), "enter_year")] = np.nan
    try:
        enter_exit_all.loc[(slice(None), 2014), (slice(None), "exit_year")] = np.nan
    except KeyError:  # this interval doesn't include 2014
        pass

    return enter_exit_all


if __name__ == "__main__":
    from pathlib import Path
    import os

    root_path = Path(os.getcwd()).parent

    cols = ["adr_net_dunsnumber_x_2014",
            "adr_net_behid_u_2014",
            "adr_net_firstyear_x_2014",
            "adr_net_lastyear_x_2014",
            "adr_net_acth_c_2014",
            "adr_net_walh_c_2014",
            "adr_net_ffah_c_2014",
            "t10_cen_uid_u_2010",
            "m10_cen_uid_u_2010"    ]

    df_philly = pd.read_csv(root_path / "data" / "raw" / "nets_philly_ACT_FFA_WAL.csv", usecols=cols)

    num_business_1990(df_philly).to_csv(root_path / "data" / "final" / "nets_philly_1990Baseline.csv")

    intervals = [1, 3, 5, 10]
    for interval in intervals:
        df_interval = enter_exit_multicat(df_philly, cat_list=["Total", "acth", "walh", "ffah"],
                                          interval_length=interval)
        df_interval.to_csv(root_path / "data" / "final" / "nets_philly_entryExit_{}yrInterval.csv".format(interval))

        print(".")
