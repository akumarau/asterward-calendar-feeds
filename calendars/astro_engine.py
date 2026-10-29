#!/usr/bin/env python3
"""Shared sky calculations for the 2027 astro calendars.

Uses Skyfield with the JPL DE421 ephemeris. The first run downloads
de421.bsp (about 17 MB) into the calendars folder. It is git ignored.

All public functions take and return timezone aware datetimes.
"""
import math
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from skyfield import almanac
from skyfield.api import Loader, Star, wgs84

SYD = ZoneInfo("Australia/Sydney")
_HERE = os.path.dirname(os.path.abspath(__file__))
_load = Loader(_HERE, verbose=False)
ts = _load.timescale(builtin=True)
eph = _load("de421.bsp")
EARTH, SUN, MOON = eph["earth"], eph["sun"], eph["moon"]

# Galactic centre (Sagittarius A*), J2000.
GC = Star(ra_hours=(17, 45, 40.04), dec_degrees=(-29, 0, 28.1))

MOON_DIAMETER_DEG = 0.52
EARTH_RADIUS_M = 6_371_000


def site(lat, lon, elev_m=0):
    return wgs84.latlon(lat, lon, elevation_m=elev_m)


def t_of(dt):
    return ts.from_datetime(dt)


def local(t):
    return t.utc_datetime().astimezone(SYD)


def altaz(topo, body, dt):
    """Apparent altitude and azimuth in degrees, with standard refraction."""
    obs = (EARTH + topo).at(t_of(dt)).observe(body).apparent()
    alt, az, dist = obs.altaz(temperature_C=15.0, pressure_mbar=1013.25)
    return alt.degrees, az.degrees, dist.km


def moon_illumination(dt):
    t = t_of(dt)
    return almanac.fraction_illuminated(eph, "moon", t) * 100


def moon_phases(year):
    t0 = ts.from_datetime(datetime(year, 1, 1, tzinfo=timezone.utc))
    t1 = ts.from_datetime(datetime(year + 1, 1, 1, tzinfo=timezone.utc))
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    names = ["New Moon", "First Quarter", "Full Moon", "Last Quarter"]
    return [(ti.utc_datetime(), names[yi]) for ti, yi in zip(t, y)]


def _events(topo, body, start, end, horizon=None):
    t0, t1 = t_of(start), t_of(end)
    if horizon is None:
        f = almanac.risings_and_settings(eph, body, topo)
    else:
        f = almanac.risings_and_settings(eph, body, topo, horizon_degrees=horizon)
    t, y = almanac.find_discrete(t0, t1, f)
    return [(local(ti), "rise" if yi else "set") for ti, yi in zip(t, y)]


def sun_moon_events(topo, start, end):
    """Rise and set events for the sun and moon between two datetimes."""
    out = [("sun" + e, dt) for dt, e in _events(topo, SUN, start, end)]
    out += [("moon" + e, dt) for dt, e in _events(topo, MOON, start, end)]
    return sorted(out, key=lambda x: x[1])


def twilight(topo, start, end):
    """Twilight transitions. Returns list of (local dt, label)."""
    f = almanac.dark_twilight_day(eph, topo)
    t, y = almanac.find_discrete(t_of(start), t_of(end), f)
    labels = {0: "Night", 1: "Astronomical twilight", 2: "Nautical twilight",
              3: "Civil twilight", 4: "Day"}
    out, prev = [], f(t_of(start)).item()
    for ti, yi in zip(t, y):
        out.append((local(ti), labels[prev], labels[int(yi)]))
        prev = int(yi)
    return out


def night_summary(topo, evening_date):
    """Key times for the night that starts on evening_date (local)."""
    start = datetime(evening_date.year, evening_date.month, evening_date.day, 12, tzinfo=SYD)
    end = start + timedelta(hours=24)
    tw = twilight(topo, start, end)
    res = {}
    for dt, frm, to in tw:
        if frm == "Day" and to == "Civil twilight":
            res["sunset"] = dt
        elif frm == "Nautical twilight" and to == "Astronomical twilight":
            res["nautical_dusk"] = dt
        elif frm == "Astronomical twilight" and to == "Night":
            res["astro_dusk"] = dt
        elif frm == "Night" and to == "Astronomical twilight":
            res["astro_dawn"] = dt
        elif frm == "Civil twilight" and to == "Day":
            res["sunrise"] = dt
    for name, dt in sun_moon_events(topo, start, end):
        if name.startswith("moon"):
            res.setdefault(name, dt)
    return res


def track(topo, body, start, end, step_min=5):
    out, dt = [], start
    while dt <= end:
        alt, az, _ = altaz(topo, body, dt)
        out.append((dt, alt, az))
        dt += timedelta(minutes=step_min)
    return out


def dark_moonless_windows(topo, start, end, step_min=5):
    """Times in [start, end] with sun below -18 deg and moon below 0 deg."""
    out, dt = [], start
    while dt <= end:
        s_alt = altaz(topo, SUN, dt)[0]
        m_alt = altaz(topo, MOON, dt)[0]
        out.append((dt, s_alt < -18 and m_alt < -0.5))
        dt += timedelta(minutes=step_min)
    spans, cur = [], None
    for dt, ok in out:
        if ok and cur is None:
            cur = dt
        if not ok and cur is not None:
            spans.append((cur, dt - timedelta(minutes=step_min)))
            cur = None
    if cur is not None:
        spans.append((cur, out[-1][0]))
    return spans


# ---------- Geodesy ----------
def destination(lat, lon, bearing_deg, dist_m):
    """Point reached from lat, lon travelling dist_m on bearing (spherical)."""
    r = dist_m / EARTH_RADIUS_M
    b = math.radians(bearing_deg)
    p1, l1 = math.radians(lat), math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(r) + math.cos(p1) * math.sin(r) * math.cos(b))
    l2 = l1 + math.atan2(math.sin(b) * math.sin(r) * math.cos(p1),
                         math.cos(r) - math.sin(p1) * math.sin(p2))
    return math.degrees(p2), (math.degrees(l2) + 540) % 360 - 180


def distance_bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    d = 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return d, (math.degrees(math.atan2(y, x)) + 360) % 360


def apparent_top_angle(dist_m, cam_elev_m, top_elev_m):
    """Angle above the camera's horizontal to a target top, with curvature."""
    drop = dist_m ** 2 / (2 * EARTH_RADIUS_M) * 0.87  # curvature less refraction
    return math.degrees(math.atan2(top_elev_m - cam_elev_m - drop, dist_m))


def moon_width_m(dist_m):
    return dist_m * math.tan(math.radians(MOON_DIAMETER_DEG))


def fmt(dt):
    return dt.strftime("%H:%M")


def compass(az):
    pts = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return pts[int((az % 360) / 22.5 + 0.5) % 16]
