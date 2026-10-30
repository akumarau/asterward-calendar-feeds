#!/usr/bin/env python3
"""Tide lookups for the astro calendars, from BOM 2027 predictions."""
import json
import math
import os
from datetime import datetime, timedelta

from astro_engine import SYD

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "data", "bom_tides_2027.json")) as f:
    _DATA = json.load(f)

BOM_NOTE = ("Tide predictions: Bureau of Meteorology 2027 tide tables, "
            "Copyright Commonwealth of Australia 2026. Based on Bureau of Meteorology information "
            "that has been modified. The Bureau does not necessarily support or endorse, or have any "
            "connection with, this product, and gives no warranty about the information. "
            "Full terms: page 4 of the source PDF.")


def _series(station):
    days = _DATA["stations"][station]["days"]
    return [(datetime.fromisoformat(f"{d}T{t}").replace(tzinfo=SYD), h, l)
            for d in sorted(days) for t, h, l in days[d]]


def pdf_url(station):
    return _DATA["stations"][station]["pdf"]


def between(station, a, b):
    return [x for x in _series(station) if a <= x[0] <= b]


def height_at(station, when):
    """Cosine interpolation between the bracketing high and low waters."""
    s = _series(station)
    for (t0, h0, _), (t1, h1, _) in zip(s, s[1:]):
        if t0 <= when <= t1:
            f = (when - t0) / (t1 - t0)
            h = h0 + (h1 - h0) * (1 - math.cos(math.pi * f)) / 2
            return h, ("rising" if h1 > h0 else "falling")
    raise ValueError(when)


def nearest_low(station, when):
    return min((x for x in _series(station) if x[2] == "Low"), key=lambda x: abs(x[0] - when))


def section(station, proxy_note, a, b, at=None, label="shoot", rock=False):
    """Text block for an event description."""
    lines = ["TIDES (BOM prediction, " + station + ")",
             proxy_note]
    for t, h, l in between(station, a - timedelta(hours=4), b + timedelta(hours=4)):
        lines.append(f"{l} water {t:%a %H:%M}  {h:.2f} m")
    if at is not None:
        h, trend = height_at(station, at)
        lines.append(f"At the {label} ({at:%H:%M}): about {h:.2f} m and {trend}.")
        if rock and h >= 1.1:
            lines.append("ROCK PLATFORM CAUTION: the water is mid to high and the tide is "
                         f"{trend} at this time. Stay on dry ground above the platform.")
    lines.append("Predictions exclude swell, wind setup and wave run up. Check BOM coastal waters "
                 "and swell forecasts on the day.")
    lines.append(f"Source table: {pdf_url(station)}")
    return lines
