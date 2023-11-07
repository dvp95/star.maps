# import libraries
import argparse
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.collections import LineCollection
from matplotlib.patches import RegularPolygon
from star_works import collect_celestial_data


def create_hexstar_chart(location, when, chart_size, max_star_size):
    """
    Arguments: location, time, chart size, max star size
    Returns: Nonetype, plots a hexagonal star chart
    """
    # get stars info
    stars, edges_star1, edges_star2 = collect_celestial_data(location, when)

    # define the number of stars & brightness of stars to include
    limiting_magnitude = 13
    bright_stars = stars.magnitude <= limiting_magnitude
    magnitude = stars["magnitude"][bright_stars]
    marker_size = max_star_size * 10 ** (magnitude / -2.5)

    # calculate the constellation lines
    xy1 = stars[["x", "y"]].loc[edges_star1].values
    xy2 = stars[["x", "y"]].loc[edges_star2].values
    lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)

    # build the figure
    fig, ax = plt.subplots(figsize=(chart_size, chart_size))

    # draw the stars & constellation
    stars_scatter = ax.scatter(
        stars["x"][bright_stars],
        stars["y"][bright_stars],
        s=marker_size,
        color="yellow",
        marker="*",
        linewidths=0,
        zorder=2,
    )
    lines_scatter = ax.add_collection(
        LineCollection(lines_xy, colors="skyblue", linewidths=0.25)
    )

    # add hex patch
    hexa = RegularPolygon(
        (0, 0),
        numVertices=6,
        radius=4.0 / 4.0,
        orientation=np.radians(0),
        facecolor="darkcyan",
    )
    ax.add_patch(hexa)
    stars_scatter.set_clip_path(hexa)
    lines_scatter.set_clip_path(hexa)

    # other settings
    ax.set_aspect("equal")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    plt.axis("off")
    when_datetime = datetime.strptime(when, "%Y-%m-%d %H:%M")
    plt.title(
        f"Observation Location: {location}, Time: {when_datetime.strftime('%Y-%m-%d %H:%M')}",
        loc="right",
        color="darkorange",
        fontsize=10,
    )

    plt.show()
    plt.close()


def get_cl_args():
    """
    Arguments: None
    Returns: instance of argparse arguments
    """
    parser = argparse.ArgumentParser(
        description="Give location and time for map. Here is an example to run this script: python star_map.py -l 'Juneau, AK' -t '2023-11-01 15:00' -ms 250"
    )
    parser.add_argument(
        "-l",
        "--location",
        dest="LOC",
        required=True,
        type=str,
        help="Location for map in the format 'City, State' ",
    )
    parser.add_argument(
        "-t",
        "--time",
        dest="TIME",
        required=True,
        type=str,
        help="Time to initate map in the format 'YYYY-MM-DD 00:00' ",
    )
    parser.add_argument(
        "-ms",
        "--max_stars",
        dest="MS",
        required=True,
        type=int,
        help="Maximum number of stars to display",
    )

    return parser.parse_args()


def main():
    """Business logic"""

    args = get_cl_args()
    loc = args.LOC
    strttime = args.TIME
    maxstars = args.MS

    print(f"You've requested a star map for {loc} starting from {strttime}")

    # creating star chart
    create_hexstar_chart(loc, strttime, 13, maxstars)


if __name__ == "__main__":
    main()
