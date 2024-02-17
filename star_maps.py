# import libraries
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from matplotlib.collections import LineCollection
from matplotlib.patches import RegularPolygon
from matplotlib.animation import FuncAnimation
from star_works import *


def update(frame_num, location, start_time, max_star_size):
    """
    Arguments: frame_num
    Returns: data to feed through animation
    """
    # Calculate time for current frame
    dt = start_time + timedelta(hours=frame_num)

    # Collect celestial data for current frame
    stars, edges_star1, edges_star2 = collect_celestial_data(location, dt)

    # define the number of stars & brightness of stars to include
    limiting_magnitude = 13

    # Filter bright stars and calculate marker sizes
    bright_stars = stars.magnitude <= limiting_magnitude
    magnitude = stars["magnitude"][bright_stars]
    marker_size = max_star_size * 10 ** (magnitude / -2.5)

    # Update data for scatter plots and lines
    stars_scatter.set_offsets(stars[["x", "y"]][bright_stars].values)
    stars_scatter.set_sizes(marker_size)
    lines_scatter.set_segments(
        np.rollaxis(
            np.array(
                [
                    stars[["x", "y"]].loc[edges_star1].values,
                    stars[["x", "y"]].loc[edges_star2].values,
                ]
            ),
            1,
        )
    )

    # Update title with current time
    plt.title(
        f"Observation Location: {location}, Time: {dt}",
        loc="right",
        color="darkorange",
        fontsize=10,
    )

    return stars_scatter, lines_scatter, title_text


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
        help="Location for map in the format 'City, State/Country'",
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
    parser.add_argument(
        "-f",
        "--file_name",
        dest="FNAME",
        type=str,
        default=None,
        help="Name of the file to be created. Defaults to None.",
    )

    return parser.parse_args()


args = get_cl_args()
loc = args.LOC
strttime = args.TIME
maxstars = args.MS
fname = args.FNAME

print(f"You've requested a star map for {loc} starting from {strttime}")
# Convert time to datetime object
when_datetime = datetime.strptime(strttime, "%Y-%m-%d %H:%M")

# Create figure and axes
fig, ax = plt.subplots(figsize=(13, 13))

# Initial plot elements
stars_scatter = ax.scatter(
    [], [], s=[], color="yellow", marker="*", linewidths=0, zorder=2
)
lines_scatter = ax.add_collection(LineCollection([], colors="skyblue", linewidths=0.25))
title_text = plt.title(
    f"Observation Location: {loc}, Time: {when_datetime}",
    loc="right",
    color="darkorange",
    fontsize=10,
)

# Add hex patch
hexa = RegularPolygon(
    (0, 0),
    numVertices=6,
    radius=4.0 / 4.0,
    orientation=np.radians(0),
    facecolor="black",
)
ax.add_patch(hexa)
stars_scatter.set_clip_path(hexa)
lines_scatter.set_clip_path(hexa)

# Other settings
ax.set_aspect("equal")
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
plt.axis("off")

ani = animation.FuncAnimation(
    fig, update, frames=24, fargs=(loc, when_datetime, maxstars), interval=679
)

if fname:
    ani.save(filename=f"{fname}.gif", writer="pillow")
else:
    plt.show()
