"""
Purpose: Module for the following fxns by Summer He, modified based on my errors: load_data, collect_celestial_data 
"""
# import libaries
from datetime import datetime
from geopy import Photon
from timezonefinder import TimezoneFinder
from pytz import timezone, utc

from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import hipparcos, stellarium


def _load_data():
    """
    Arguments: None
    Returns: loaded datasets
    """
    # de421 ds shows position of earth and sun in space
    eph = load("de421.bsp")

    # hipparcos ds
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)

    # constellation ds
    url = (
        "https://raw.githubusercontent.com/Stellarium/stellarium/master"
        "/skycultures/modern_st/constellationship.fab"
    )

    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)

    return eph, stars, constellations


def collect_celestial_data(location, when):
    """
    Arguments: user provided location and time data
    Returns: position of stars and edges for constellations based on location and time
    """
    # loading required datasets
    eph, stars, constellations = _load_data()

    # get latitude coordinates
    locator = Photon(user_agent="myGeocoder", timeout=10)
    location = locator.geocode(location)
    lat, long = location.latitude, location.longitude

    # convert date string into datetime object
    dt = datetime.strptime(when, "%Y-%m-%d %H:%M")

    # define datetime & convert to UTC based on location coordinates
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=long, lat=lat)
    local = timezone(timezone_str)
    utc_dt = local.localize(dt, is_dst=None).astimezone(utc)

    # define observer using location coordinates & current UTC time
    t = load.timescale().from_datetime(utc_dt)
    observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=long).at(t)

    # an ephemeris on Sun and Earth positions.
    sun = eph["sun"]
    earth = eph["earth"]

    # the constellation outlines list.
    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]

    # define the angle & center the observation location by the angle
    position = observer.from_altaz(alt_degrees=90, az_degrees=0)
    ra, dec, distance = observer.radec()
    center_object = Star(ra=ra, dec=dec)

    # build the stereographic projection
    center = earth.at(t).observe(center_object)
    projection = build_stereographic_projection(center)
    field_of_view_degrees = 180.0

    # compute the x & y coordinates based on the projection
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars["x"], stars["y"] = projection(star_positions)

    return stars, edges_star1, edges_star2
