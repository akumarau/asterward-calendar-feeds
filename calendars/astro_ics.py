#!/usr/bin/env python3
"""ICS writing and link helpers shared by the astro calendar generators."""
import math
import os
from datetime import datetime, timezone
from urllib.parse import quote

NOW = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")

# Sony Alpha 1: 35.9 x 24.0 mm sensor, 8640 px wide (4.16 micron pixels).
SENSOR_W, SENSOR_H, PIXEL_UM = 35.9, 24.0, 4.16

SYD_VTZ = """BEGIN:VTIMEZONE
TZID:Australia/Sydney
BEGIN:STANDARD
DTSTART:19700405T030000
RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU
TZOFFSETFROM:+1100
TZOFFSETTO:+1000
TZNAME:AEST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19701004T020000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=1SU
TZOFFSETFROM:+1000
TZOFFSETTO:+1100
TZNAME:AEDT
END:DAYLIGHT
END:VTIMEZONE""".split("\n")


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    if len(line.encode("utf-8")) <= 75:
        return line
    out, cur, limit = [], b"", 75
    for ch in line:
        cb = ch.encode("utf-8")
        if len(cur) + len(cb) > limit:
            out.append(cur.decode("utf-8"))
            cur, limit = b"", 74
        cur += cb
    out.append(cur.decode("utf-8"))
    return "\r\n ".join(out)


def gmaps(lat, lon):
    return f"https://www.google.com/maps/search/?api=1&query={lat:.5f},{lon:.5f}"


def tpe(cam, subject, dt, fov=None, zoom=15):
    """The Photographer's Ephemeris web link: red pin = camera, grey pin = subject."""
    utc = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:00.000Z")
    url = (f"https://app.photoephemeris.com/?ll={cam[0]:.5f},{cam[1]:.5f}"
           f"&center={cam[0]:.5f},{cam[1]:.5f}&z={zoom}&dt={quote(utc, safe='')}")
    if subject:
        url += f"&sll={subject[0]:.5f},{subject[1]:.5f}"
    if fov:
        url += (f"&fovb={fov['bearing']:.1f}&fovhfov={fov['hfov']:.2f}&fovvfov={fov['vfov']:.2f}"
                f"&fovd={fov['dist']:.0f}&fovo=l&fovov=1")
    return url


def fov_deg(focal_mm):
    h = 2 * math.degrees(math.atan(SENSOR_W / (2 * focal_mm)))
    v = 2 * math.degrees(math.atan(SENSOR_H / (2 * focal_mm)))
    return h, v


def npf_seconds(focal_mm, aperture):
    """Simple NPF rule for sharp stars on the Alpha 1."""
    return (35 * aperture + 30 * PIXEL_UM) / focal_mm


def write_calendar(filename, prodid, calname, events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//akumarau//{prodid}//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{calname}",
             "X-WR-TIMEZONE:Australia/Sydney", "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
             "X-PUBLISHED-TTL:PT12H"] + SYD_VTZ
    for ev in events:
        lines += ["BEGIN:VEVENT", f"UID:{ev['uid']}", f"DTSTAMP:{NOW}",
                  f"DTSTART;TZID=Australia/Sydney:{ev['start'].strftime('%Y%m%dT%H%M00')}",
                  f"DTEND;TZID=Australia/Sydney:{ev['end'].strftime('%Y%m%dT%H%M00')}",
                  f"SUMMARY:{esc(ev['summary'])}", f"LOCATION:{esc(ev['location'])}",
                  f"GEO:{ev['geo'][0]:.5f};{ev['geo'][1]:.5f}", f"URL:{ev['url']}",
                  f"DESCRIPTION:{esc(ev['description'])}", f"CATEGORIES:{ev['category']}",
                  "TRANSP:TRANSPARENT", "X-MICROSOFT-CDO-BUSYSTATUS:FREE",
                  "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-P2D",
                  f"DESCRIPTION:{esc('Check cloud and weather: ' + ev['summary'])}", "END:VALARM",
                  "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT3H",
                  f"DESCRIPTION:{esc('Leave soon: ' + ev['summary'])}", "END:VALARM",
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    path = os.path.join(DOCS, filename)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(fold(l) for l in lines) + "\r\n")
    return path
