import numpy as np
import pandas as pd


def subset_nets(df, cat_code):
    """Subset the NETS based on the prescence of a category"""
    return df[df["adr_net_{}_c_2014".format(cat_code.lower())] == 1]


def enter_exit(df, subset_cat="Total", interval_length=None):
    """Define the number of businesses that entered and exited all census tracts per time period"""

    if subset_cat != "Total":
        df = subset_nets(df, subset_cat)

    # Enter and exit year per business per tract
    business_rate = df.replace({"adr_net_lastyear_x_2014": 2014}, np.nan) \
        .replace({"adr_net_firstyear_x_2014": 1990}, np.nan) \
        .groupby(["adr_net_dunsnumber_x_2014", "t10_cen_uid_u_2010"]).agg({
        'adr_net_firstyear_x_2014': min,
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
        .rename("exit_year")
    # Change year index to int for datetime conversion
    idx_exit = exit_year.index
    exit_year.index.set_levels(idx_exit.levels[-1].astype(int), level="year", inplace=True)

    # Enter and exit count per tract per year
    df_tract_year_count = pd.concat([enter_year, exit_year], axis=1) \
        .reset_index() \
        .assign(year=lambda x: pd.to_datetime(x.year, format="%Y")) \
        .set_index(["t10_cen_uid_u_2010", "year"])

    if interval_length:
        df_tract_year_count = df_tract_year_count \
            .groupby(level=0) \
            .resample("{}Y".format(interval_length), level=1).sum() \
            .loc[(slice(None), slice("1/1/1990", "12/31/2014")), :]

    df_tract_year_count.index.set_levels(df_tract_year_count.index.levels[1].year, level=1, inplace=True)
    df_tract_year_count.columns = pd.MultiIndex.from_product([[subset_cat.upper()], df_tract_year_count.columns])

    return df_tract_year_count


def enter_exit_multicat(df, cat_list, interval_length=None):
    """Returns entry and exit rates for all categories with a given interval length"""

    df_list = [enter_exit(df, subset_cat=cat, interval_length=interval_length) for cat in cat_list]

    return pd.concat(df_list, axis=1).fillna(0)


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
            "m10_cen_uid_u_2010"]

    df_philly = pd.read_csv(root_path / "data" / "raw" / "nets_philly_ACT_FFA_WAL.csv", usecols=cols)

    intervals = [1, 3, 5, 10]
    for interval in intervals:
        df_interval = enter_exit_multicat(df_philly, cat_list=["Total", "acth", "walh", "ffah"], interval_length=interval)
        df_interval.to_csv(root_path / "data" / "final" / "nets_philly_entryExit_{}yrInterval.csv".format(interval))
