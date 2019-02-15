import os
import time
import pandas as pd

from pathlib import Path

def get_filename(search_term, dir):
    """Gets filenames containing search_term within dir"""
    all_matches = [x for x in os.listdir(dir) if search_term in x]
    first_match = all_matches[0]
    return first_match


def main():
    county = "c10_cen_uid_u_2010"
    ny_counties = [36005, 36047, 36061, 36081, 36085]
    today = time.strftime("%Y%m%d")

    dir_path_in = Path.cwd().parent.parent / "data"
    data_path_in = dir_path_in / get_filename("uhc", dir_path_in)
    data_path_out = data_path_in.parent / "recvd_nets_uhcid_{}.csv".format(today)
    df = pd.read_csv(data_path_in, chunksize=10**6)

    for i, chunk in enumerate(df):
        ny_mask = chunk[county].isin(ny_counties)
        ny_chunk = chunk[ny_mask]

        if not i:
            with open(data_path_out, "w", newline="\n") as f:
                ny_chunk.to_csv(f, index=False)

        else:
            with open(data_path_out, "a", newline="\n") as f:
                ny_chunk.to_csv(f, index=False, header=False)


if __name__ == "__main__":
    main()
