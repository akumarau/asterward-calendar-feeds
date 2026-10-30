#!/usr/bin/env python3
"""Build docs/full-moon-2027.ics: long lens full moon alignments near Sydney, 2027.

Run: python calendars/full_moon_2027.py   (needs: pip install -r calendars/requirements-astro.txt)

Each event picks the evening (night before, of, or after full moon) where moonrise
lands closest to sunset, then solves the exact camera pin where the rising moon
sits on the landmark. June is left out for the Europe trip.
"""
import math
from datetime import date, timedelta

import astro_engine as A
from astro_ics import fov_deg, gmaps, tpe, write_calendar
import astro_tides as TD

HOME = (-33.8366, 151.2190)  # Neutral Bay, for straight line distance only
FULL_MOONS = [dt.astimezone(A.SYD) for dt, n in A.moon_phases(2027) if n == "Full Moon"]

# Landmark: pin, top height above sea level (m, approx), base height (m), target wording.
LANDMARKS = {
    "Anzac Bridge": dict(pin=(-33.86899, 151.18533), top=120, base=0,
                         target="the centre of the span, level with the pylon tops"),
    "Nobbys Lighthouse": dict(pin=(-32.91857, 151.79840), top=35, base=17,
                              target="the lighthouse lantern on Nobbys Head"),
    "Barrenjoey Lighthouse": dict(pin=(-33.58019, 151.32983), top=115, base=97,
                                  target="the sandstone lighthouse on Barrenjoey Head"),
    "Kiama Lighthouse": dict(pin=(-34.67181, 150.86259), top=38, base=23,
                             target="the lighthouse lantern on Blowhole Point"),
    "Sydney Harbour Bridge": dict(pin=(-33.85212, 151.21078), top=134, base=0,
                                  target="the top of the arch"),
    "Norah Head Lighthouse": dict(pin=(-33.28165, 151.57635), top=48, base=21,
                                  target="the lighthouse lantern"),
    "Crookhaven Lighthouse": dict(pin=(-34.89912, 150.77017), top=28, base=17,
                                  target="the lighthouse on Crookhaven Heads"),
}

# Viewpoint: named pin, ground elevation (SRTM, m), place text.
VIEWPOINTS = {
    "Bicentennial Park, Glebe": dict(pin=(-33.87283, 151.17743), elev=2,
        place="Bicentennial Park foreshore, Glebe NSW 2037"),
    "Stockton foreshore": dict(pin=(-32.91974, 151.78250), elev=0,
        place="Stockton Ferry Wharf and foreshore, Mitchell Street, Stockton NSW 2295"),
    "West Head Lookout": dict(pin=(-33.57914, 151.30924), elev=101,
        place="West Head Lookout, West Head Road, Ku-ring-gai Chase National Park NSW 2105"),
    "Black Beach, Kiama": dict(pin=(-34.67023, 150.85601), elev=0,
        place="Black Beach, Shoalhaven Street, Kiama NSW 2533"),
    "Blues Point Reserve": dict(pin=(-33.84957, 151.20342), elev=0,
        place="Blues Point Reserve, Blues Point Road, McMahons Point NSW 2060"),
    "Norah Head Rock Pool": dict(pin=(-33.27893, 151.56964), elev=5,
        place="Norah Head Rock Pool, Bald Street, Norah Head NSW 2263"),
    "Orient Point": dict(pin=(-34.90907, 150.73993), elev=1,
        place="Orient Point foreshore, Orient Point NSW 2540"),
    "Kiama Surf Beach": dict(pin=(-34.67634, 150.85456), elev=4,
        place="Kiama Surf Beach, Manning Street, Kiama NSW 2533"),
}

PLAN = [
    dict(evening=date(2027, 1, 22), vp="Bicentennial Park, Glebe", lm="Anzac Bridge",
         title="Moon between the pylons",
         what="The full moon climbing between the two white pylons of Anzac Bridge, across Rozelle Bay. "
              "Moonrise is at sunset, and the moon reaches the pylon tops in blue hour.",
         notes=["Public foreshore park. Jubilee Park light rail stop is close.",
                "City light builds quickly after 21:00. Bracket for the moon and the sky separately.",
                "Calm water in Rozelle Bay gives a reflection of the bridge lights."]),
    dict(evening=date(2027, 2, 21), vp="Stockton foreshore", lm="Nobbys Lighthouse",
         title="Moonrise behind Nobbys Head",
         what="The full moon rising out of the Tasman Sea behind Nobbys Head Lighthouse, "
              "across the mouth of Newcastle Harbour. Big ships often pass in front.",
         notes=["Stockton is reached by the Newcastle ferry from Queens Wharf or by road over Stockton Bridge.",
                "Harbour traffic: check the Port of Newcastle shipping schedule for a ship in frame.",
                "The camera pin is on the foreshore south of the wharf. Walk the shoreline to fine tune.",
                "Stay off the breakwall when there is any surf."]),
    dict(evening=date(2027, 3, 22), vp="West Head Lookout", lm="Barrenjoey Lighthouse",
         title="Moonrise over Barrenjoey Head", use_named=True,
         what="The full moon lifting off the ocean right beside Barrenjoey Lighthouse, seen across Broken Bay "
              "from West Head. Moonrise comes just before sunset, so the headland is in warm light.",
         notes=["NPWS: West Head gates close at 8.30pm during daylight saving and 6pm the rest of the year. "
                "Leave before the gate closes.",
                "Park entry is a vehicle day fee, payable with the Park'nPay app.",
                "The lookout is about 100 m above the sea, so the moon rises from the sea horizon level with the lantern."]),
    dict(evening=date(2027, 4, 21), vp="Black Beach, Kiama", lm="Kiama Lighthouse",
         title="Moon on the lighthouse across Kiama Harbour",
         what="The full moon rising behind Kiama Lighthouse on Blowhole Point, framed across Kiama Harbour "
              "from Black Beach. Short distance, so the moon is small: a context frame rather than a giant moon.",
         notes=["Wednesday, about 2 hours south. Plan a half day. Kiama station is a short walk away.",
                "Low tide exposes the dark rocks at Black Beach for foreground.",
                "Blowhole Point floodlights switch on after dark. Shoot the alignment before they dominate."]),
    dict(evening=date(2027, 5, 20), vp="Blues Point Reserve", lm="Sydney Harbour Bridge",
         title="Moon on the arch of the Harbour Bridge",
         what="The full moon sitting on the top of the Harbour Bridge arch, seen from Blues Point. "
              "The exact pin is within metres of the reserve's usual photo spot.",
         notes=["About 1.5 km from the North Sydney office. Leave by 16:30 on the day.",
                "Popular spot on full moon nights. Arrive early to claim the line.",
                "Twilight bridge climbers may be on the arch. At 600 mm they make a strong silhouette against the moon."]),
    dict(evening=date(2027, 7, 18), vp="Norah Head Rock Pool", lm="Norah Head Lighthouse",
         title="Moonrise behind the lighthouse at sunset",
         what="The full moon rising behind Norah Head Lighthouse across Cabbage Tree Bay, a few minutes "
              "before sunset. Winter light on the tower and a pale moon.",
         notes=["Rock pool and platform: check swell before stepping onto the rocks.",
                "The alignment pin is within metres of the rock pool.",
                "A Sunday shoot. Allow about 1 h 30 min to drive up from Neutral Bay."]),
    dict(evening=date(2027, 8, 16), vp="Blues Point Reserve", lm="Sydney Harbour Bridge",
         title="Moon on the arch at sunset",
         what="The full moon reaching the top of the Harbour Bridge arch right at sunset, from the tip of "
              "Blues Point. Warm light on the steel and a bright sky.",
         notes=["About 1.5 km from the North Sydney office. Leave by 16:20 on the day.",
                "The exact pin is about 120 m south of the reserve pin, near the point itself.",
                "The moon is still faint against the sunset sky. Expose for the sky and bracket."]),
    dict(evening=date(2027, 9, 16), vp="Stockton foreshore", lm="Nobbys Lighthouse",
         title="Spring moonrise behind Nobbys",
         what="The full moon rising behind Nobbys Head Lighthouse about 20 minutes after sunset, "
              "with blue hour over Newcastle Harbour.",
         notes=["Thursday evening, about 2 hours north. Plan a half day or a Newcastle overnight.",
                "The exact pin is about 80 m along the foreshore from the wharf.",
                "Check the shipping schedule for an outbound ship."]),
    dict(evening=date(2027, 10, 16), vp="Orient Point", lm="Crookhaven Lighthouse",
         title="Moonrise behind Crookhaven Heads",
         what="The full moon rising behind the small Crookhaven Heads Lighthouse across the mouth of the "
              "Crookhaven River. Three kilometres out, so the moon looks big beside the tower.",
         notes=["Long drive: about 2 h 30 min south. Pair it with a Shoalhaven weekend.",
                "Check the exact pin falls on the public foreshore before you go, then fine tune along the shore.",
                "Moonrise is after sunset. The sky is dark blue, so expose for the moon and blend."]),
    dict(evening=date(2027, 11, 14), vp="Bicentennial Park, Glebe", lm="Anzac Bridge",
         title="Late spring moon between the pylons",
         what="The full moon rising between the pylons of Anzac Bridge across Rozelle Bay, in late twilight.",
         notes=["Public foreshore park. Jubilee Park light rail stop is close.",
                "The moon climbs further north than in January, closer to the left pylon.",
                "Sunday night. Easy return home."]),
    dict(evening=date(2027, 12, 13), vp="Kiama Surf Beach", lm="Kiama Lighthouse",
         title="Summer moonrise over Blowhole Point",
         what="The full moon rising out of the sea behind Kiama Lighthouse, seen across the water from "
              "Kiama Surf Beach, in the last light of a summer evening.",
         notes=["The exact pin is beside the Surf Life Saving Club, a few metres from the beach pin.",
                "Monday evening, about 2 hours south. Plan to leave work early.",
                "Summer swell can be large here. Stay above the wet sand."]),
]

CAM_HEIGHT = 1.5

# Tide station per viewpoint, with how well it represents the spot.
TIDE = {
    "Bicentennial Park, Glebe": ("Sydney (Fort Denison)", "Fort Denison is in the same harbour, so times are close for this spot."),
    "Blues Point Reserve": ("Sydney (Fort Denison)", "Fort Denison is about 1.5 km away in the same harbour, so times are close."),
    "Stockton foreshore": ("Newcastle", "The Newcastle gauge is in the same harbour mouth, so times are close."),
    "West Head Lookout": ("Sydney (Fort Denison)", "Nearest BOM standard port. Broken Bay tides are similar in timing. "
                          "The lookout is high above the water, so tide only changes the foreground."),
    "Black Beach, Kiama": ("Port Kembla", "Port Kembla is the nearest BOM standard port. Treat times as approximate."),
    "Kiama Surf Beach": ("Port Kembla", "Port Kembla is the nearest BOM standard port. Treat times as approximate."),
    "Norah Head Rock Pool": ("Newcastle", "Newcastle is the nearest BOM standard port. Treat times as approximate."),
    "Orient Point": ("Port Kembla", "Port Kembla is the nearest BOM standard port. The Crookhaven River mouth "
                     "can lag the open coast, so treat times as approximate."),
}


def solve(vp, lm, evening):
    v, l = VIEWPOINTS[vp], LANDMARKS[lm]
    cam_h = v["elev"] + CAM_HEIGHT
    topo = A.site(*v["pin"], v["elev"])
    n = A.night_summary(topo, evening)
    mr = n["moonrise"]
    best, t = None, mr - timedelta(minutes=10)
    while t < mr + timedelta(minutes=120):
        alt, az, _ = A.altaz(topo, A.MOON, t)
        f = lambda D: A.apparent_top_angle(D, cam_h, l["top"]) - alt
        lo, hi = 50.0, 40000.0
        if f(lo) > 0 > f(hi):
            for _ in range(60):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
            D = (lo + hi) / 2
            P = A.destination(*l["pin"], (az + 180) % 360, D)
            off, _ = A.distance_bearing(*v["pin"], *P)
            if best is None or off < best["off"]:
                best = dict(off=off, t=t, alt=alt, az=az, D=D, P=P)
        t += timedelta(minutes=1)
    return topo, n, best


def lens_advice(h_deg):
    """Focal length that makes the landmark about 60% of frame height, and the moon at 600 mm."""
    f = 24.0 / (2 * math.tan(math.radians(h_deg / 0.6) / 2))
    if f <= 70:
        pick = f"FE 24-70mm F2.8 GM II at about {max(24, round(f / 5) * 5)} mm"
    elif f <= 200:
        pick = f"FE 70-200mm F2.8 GM OSS II at about {round(f / 5) * 5} mm"
    elif f <= 600:
        pick = f"FE 200-600mm at about {round(f / 10) * 10} mm"
    else:
        pick = "FE 200-600mm at 600 mm, or 900 mm equivalent in APS-C crop mode"
    return f, pick


def build():
    events = []
    for p in PLAN:
        v, l = VIEWPOINTS[p["vp"]], LANDMARKS[p["lm"]]
        topo, n, b = solve(p["vp"], p["lm"], p["evening"])
        # When the moon rises straight off the sea horizon, distance does not matter:
        # stay on the named lookout and report the sideways offset instead.
        cam = v["pin"] if p.get("use_named") else b["P"]
        cam_h = v["elev"] + CAM_HEIGHT
        fm = min(FULL_MOONS, key=lambda d: abs((d.date() - p["evening"]).days))
        mr = n["moonrise"]
        mr_alt, mr_az, _ = A.altaz(topo, A.MOON, mr)
        illum = A.moon_illumination(b["t"])
        civil_end = [x for x in A.twilight(topo, n["sunset"], n["sunset"] + timedelta(hours=2))
                     if x[1] == "Civil twilight"]
        civil_txt = f" · civil twilight ends {A.fmt(civil_end[0][0])}" if civil_end else ""

        # From the named viewpoint pin.
        dv, bv = A.distance_bearing(*v["pin"], *l["pin"])
        diff = b["az"] - bv
        lr = "left" if diff < 0 else "right"
        # Exact pin geometry.
        d_cam, b_cam = A.distance_bearing(*cam, *l["pin"])
        top_ang = A.apparent_top_angle(d_cam, cam_h, l["top"])
        base_ang = A.apparent_top_angle(d_cam, cam_h, l["base"])
        h_ang = max(top_ang - base_ang, 0.05)
        f_fit, pick = lens_advice(h_ang)
        moon_w = A.moon_width_m(d_cam)
        hf, vf = fov_deg(min(max(f_fit, 24), 600))
        dist_home, _ = A.distance_bearing(*HOME, *cam)

        rows, t = [], max(mr - timedelta(minutes=5), b["t"] - timedelta(minutes=30))
        while t <= b["t"] + timedelta(minutes=15):
            alt, az, _ = A.altaz(topo, A.MOON, t)
            mark = "  << alignment" if abs((t - b["t"]).total_seconds()) < 150 else ""
            if alt > -1:
                rows.append(f"{A.fmt(t)}  altitude {alt:4.1f}°, azimuth {az:5.1f}°{mark}")
            t += timedelta(minutes=5)

        start = b["t"] - timedelta(minutes=45)
        end = b["t"] + timedelta(minutes=30)
        weekday = p["evening"].weekday() < 5

        st, st_note = TIDE[p["vp"]]
        tide_lines = [""] + TD.section(st, st_note, b["t"] - timedelta(minutes=45), b["t"] + timedelta(minutes=30),
                                       at=b["t"], label="alignment",
                                       rock=p["vp"] in ("Norah Head Rock Pool", "Black Beach, Kiama"))
        desc = "\n".join([
            f"WHAT: {p['what']}",
            f"Target: moon centred on {l['target']}.",
            "",
            "WHEN (Sydney time)",
            f"{p['evening']:%A %d %B %Y}" + ("  (work day)" if weekday else ""),
            f"Full moon: {fm:%a %d %b %H:%M}. Moon {illum:.0f}% lit at the alignment.",
            f"Sunset {A.fmt(n['sunset'])}{civil_txt}",
            f"Moonrise {A.fmt(mr)} at azimuth {mr_az:.0f}° {A.compass(mr_az)} (sea level horizon).",
            f"ALIGNMENT {A.fmt(b['t'])}: moon altitude {b['alt']:.1f}°, azimuth {b['az']:.1f}°.",
            f"Arrive by {A.fmt(start)}. The moon moves about one diameter every 2 to 3 minutes, "
            "so shoot from 10 minutes before to 10 minutes after.",
            "",
            "MOON TRACK",
            *rows,
            "",
            "CAMERA POSITION",
            *( [f"Camera pin (the lookout itself): {gmaps(*cam)}", v["place"]] if p.get("use_named") else
               [f"Exact alignment pin: {gmaps(*cam)}",
                f"Named spot: {v['place']} ({b['off']:.0f} m from the exact pin). {gmaps(*v['pin'])}"] ),
            f"Subject pin ({p['lm']}): {gmaps(*l['pin'])}",
            f"From the {'lookout' if p.get('use_named') else 'exact pin'}, {p['lm']} is {d_cam:.0f} m away on bearing {b_cam:.1f}°.",
            (f"The moon rises {abs(diff):.1f}° {lr} of the target, roughly {'one moon width' if abs(diff) < 0.8 else f'{abs(diff) / 0.52:.0f} moon widths'}. "
             "Shift a few metres along the rail to fine tune." if p.get("use_named") else
             f"From the named spot it is on bearing {bv:.1f}°, so there the moon passes {abs(diff):.1f}° {lr} of the target. "
             "Walk toward the exact pin to close the gap."),
            f"Straight line from Neutral Bay: about {dist_home/1000:.0f} km.",
            *tide_lines,
            "",
            "FRAMING (Sony A1)",
            f"{p['lm']} spans about {h_ang:.1f}° tall from here. The moon is 0.52° wide, about {moon_w:.0f} m across at this distance.",
            f"Landmark filling 60% of the frame height: {pick}.",
            f"Moon dominant: FE 200-600mm at 600 mm puts the moon at {0.52 / fov_deg(600)[1] * 100:.0f}% of frame height "
            "(34% in APS-C crop mode).",
            "Tripod, OSS off on the tripod, 2 s timer or remote, shutter 1/125 s or faster at 600 mm.",
            "Start: ISO 200 to 400, f/8, expose for the moon. Bracket 3 frames at 2 EV after sunset and blend.",
            "",
            "FIELD NOTES",
            *[f"- {x}" for x in p["notes"]],
            "",
            "VERIFY BEFORE YOU GO",
            f"TPE Web (camera pin, subject pin, alignment time): "
            f"{tpe(cam, l['pin'], b['t'], dict(bearing=b_cam, hfov=hf, vfov=vf, dist=d_cam), zoom=16)}",
            f"In TPE, set the secondary height to about {l['top'] - l['base']} m above ground to check the geodetics line.",
            "PhotoPills: Planner > red pin on the camera pin, black pin on the subject > Find > "
            f"Moon, elevation {b['alt']:.1f}° > confirm the date. Use the AR view on site.",
            "Heights are approximate. Fine tune by a few metres on the day.",
            "",
            "SOURCES",
            "Moon phases: US Naval Observatory 2027 table (aa.usno.navy.mil).",
            "Moon and sun positions: computed with Skyfield and JPL DE421, with standard refraction.",
            "Coordinates: OpenStreetMap. Ground heights: SRTM 30 m via OpenTopoData.",
            TD.BOM_NOTE,
        ])
        events.append(dict(
            uid=f"fullmoon2027-{p['evening']:%Y%m%d}@akumarau",
            start=start, end=end,
            summary=f"Full Moon · {p['lm']} from {p['vp']} · {p['title']}",
            location=v["place"], geo=cam, url=gmaps(*cam),
            description=desc, category="Astrophotography"))
        print(f"{p['evening']}  {p['lm']:22s} from {p['vp']:26s} align {A.fmt(b['t'])} alt {b['alt']:.1f} "
              f"az {b['az']:.1f} pin {cam[0]:.5f},{cam[1]:.5f} ({b['off']:.0f} m) D {d_cam:.0f} m")
    path = write_calendar("full-moon-2027.ics", "Full Moon 2027", "Astro · Full Moon 2027", events)
    print(f"wrote {path} ({len(events)} events)")


if __name__ == "__main__":
    build()
