#!/usr/bin/env python3
"""Build docs/milky-way-2027.ics: Milky Way core shoots near Sydney, Feb to Oct 2027.

Run: python calendars/milky_way_2027.py   (needs: pip install -r calendars/requirements-astro.txt)

Sessions sit on the Saturday night closest to each new moon. June and early July
are left out for the Europe trip. Sky positions are computed at build time.
"""
from datetime import date, datetime, timedelta

import astro_engine as A
from astro_ics import fov_deg, gmaps, npf_seconds, tpe, write_calendar

HOME = (-33.8366, 151.2190)  # Neutral Bay, for straight line distance only
NEW_MOONS = [dt.astimezone(A.SYD) for dt, n in A.moon_phases(2027) if n == "New Moon"]

KIT_WIDE = ("FE 12-24mm F2.8 GM at 12 to 14 mm for single frames. "
            "FE 35mm F1.4 GM II for a sharper multi row panorama.")
KIT_TRACK = ("Dark site option: Esprit 80ED on the AM5N with the ASI2600MC Air for the "
             "Lagoon and Trifid region near the core. Antlia Triband for the emission nebulae.")

NIGHTS = [
    dict(evening=date(2027, 2, 6), priority="Optional", region="Central Coast",
         site="Norah Head Lighthouse", title="Core rising beside the lighthouse",
         cam=(-33.27893, 151.56964), cam_name="Norah Head Rock Pool, Bald Street, Norah Head NSW 2263",
         subject=(-33.28165, 151.57635), subject_name="Norah Head Lighthouse",
         what="The galactic core rising out of the Pacific beside Norah Head Lighthouse. "
              "Early season, so the core is low and short lived before dawn. "
              "Frame the lighthouse low and let the core climb beside it.",
         kit=KIT_WIDE,
         notes=["Work from the public rock platform and foreshore, not the lighthouse grounds.",
                "Rock platform: check swell and tide first. Wet rock is slippery in the dark.",
                "Light from the lighthouse beam sweeps the frame. Time exposures between passes or blend."]),
    dict(evening=date(2027, 3, 6), priority="High", region="Kiama Downs",
         site="Cathedral Rocks", title="Core over the coastal rock stacks",
         cam=(-34.64444, 150.85547), cam_name="Cliff Drive viewpoint above Cathedral Rocks, Kiama Downs NSW 2533",
         subject=(-34.64481, 150.85670), subject_name="Cathedral Rocks sea stacks",
         what="The core rising over the Cathedral Rocks sea stacks, with the Pacific below. "
              "By 03:00 the core is high enough to stack the band above the rocks.",
         kit=KIT_WIDE,
         notes=["Viewpoint is at the top of the cliff. Going down to the rocks means a rock platform at night: "
                "only at low tide and small swell.",
                "Check BOM tide times for Kiama before you go.",
                "Long exposure smooths the surf around the stacks. Shoot the foreground at blue hour if possible."]),
    dict(evening=date(2027, 4, 10), priority="Very high", region="Kiama",
         site="Bombo Headland Quarry", title="Core above the basalt columns",
         cam=(-34.65005, 150.86242), cam_name="Bombo Headland Quarry Geological Site viewpoint, Commissioners Lane, Bombo NSW 2533",
         subject=(-34.65037, 150.86344), subject_name="Bombo basalt columns",
         what="The core rising in the east above the hexagonal basalt columns of the old Bombo quarry, "
              "with the ocean behind. The best core position of the coastal set.",
         kit=KIT_WIDE,
         notes=["Confirm current track and car park access with Kiama Council before the trip.",
                "Old quarry: loose rock and drop offs. Scout in daylight and keep to marked paths.",
                "A low level light panel on the columns from the side adds texture. Keep it dim."]),
    dict(evening=date(2027, 5, 8), priority="Very high", region="Lithgow",
         site="Lake Lyell", title="Core rising above the water",
         cam=(-33.52379, 150.07734), cam_name="Lake Lyell Recreation Park shoreline, Magpie Hollow Road, Rydal NSW 2790",
         subject=None, subject_name=None,
         what="The core rising in the east south east above the eastern arm of Lake Lyell. "
              "From this shoreline the water runs 100 m to 600 m out toward the core. "
              "Calm nights give a reflection.",
         kit=KIT_WIDE + " " + KIT_TRACK,
         notes=["The park has powered and unpowered camp sites. Camping is the simplest way to be on the shore after dark.",
                "Expect cold, damp air in May at 790 m. Run the dew heater on lenses too.",
                "Low hills across the lake sit about 3 degrees high, so the core clears them early."]),
    dict(evening=date(2027, 7, 31), priority="High", region="Kangaroo Valley",
         site="Hampden Bridge", title="Core descending over the sandstone towers",
         cam=(-34.72736, 150.52311), cam_name="Riverside viewpoint east of Hampden Bridge, Cullen Crescent, Kangaroo Valley NSW 2577",
         subject=(-34.72755, 150.52093), subject_name="Hampden Bridge",
         what="Winter core, high and bright, sinking toward the west south west behind the castellated "
              "sandstone towers of Hampden Bridge. Rural valley skies, darker than the coast.",
         kit=KIT_WIDE + " " + KIT_TRACK,
         notes=["Valley fog often forms on cold still nights. Check the forecast dew point.",
                "The bridge carries traffic. Avoid headlights by timing exposures, or stack frames.",
                "Terrain to the west south west is only about 2 degrees high from here."]),
    dict(evening=date(2027, 8, 28), priority="High", region="Lithgow",
         site="Hassans Walls Lookout", title="Core setting over the Hartley Valley",
         cam=(-33.51491, 150.15092), cam_name="Hassans Walls Lookout, Sir Joseph Cook Boardwalk, Lithgow NSW 2790",
         subject=None, subject_name=None,
         what="The core sinking into the south west over the Hartley Valley from the highest lookout "
              "in the Blue Mountains region. Open horizon, no terrain above zero degrees to the south west.",
         kit=KIT_WIDE + " " + KIT_TRACK,
         notes=["Cliff top boardwalk. Stay behind the rails.",
                "Check road and reserve access after dark with Lithgow City Council.",
                "Late August at 1,100 m is near freezing. Pack layers and a flask."]),
    dict(evening=date(2027, 9, 25), priority="Medium", region="Northern Beaches",
         site="Pittwater, Palm Beach", title="Core over Pittwater and Ku-ring-gai Chase",
         cam=(-33.59640, 151.32002), cam_name="Pittwater Park foreshore, Palm Beach NSW 2108",
         subject=None, subject_name=None,
         what="The core over the dark bushland of Ku-ring-gai Chase across Pittwater, with water in the "
              "foreground. Closest site to home, but suburban glow sits low to the south west.",
         kit=KIT_WIDE,
         notes=["Calm water gives reflections. Moored boats make good foreground lights.",
                "Ridge line across Pittwater sits about 2 degrees high.",
                "Light pollution is moderate here. Stop shooting once the core drops below about 12 degrees."]),
    dict(evening=date(2027, 10, 30), priority="Medium", region="Blue Mountains",
         site="Mount Blackheath Lookout", title="Last core of the season over the Kanimbla Valley",
         cam=(-33.64173, 150.24531), cam_name="Mount Blackheath Lookout, Mount Blackheath Road, Blackheath NSW 2785",
         subject=None, subject_name=None,
         what="The final evening core of 2027, low in the west south west over the Kanimbla Valley. "
              "A short window right after dark, so be set up before astronomical dusk.",
         kit=KIT_WIDE,
         notes=["Hang gliding launch area on the cliff edge. Keep well back from the drop.",
                "Distant ranges sit about 0.5 degrees high, so the low core stays clear.",
                "Window is about two hours. Shoot the foreground at blue hour first."]),
]


def window(topo, n, rising, alt_min, alt_max=60):
    """Longest run of dark, moonless times with the core between alt_min and alt_max,
    on the eastern (rising) or western (setting) side of the sky."""
    spans = A.dark_moonless_windows(topo, n["astro_dusk"], n["astro_dawn"], 5)
    runs, cur = [], []
    for a, b in spans:
        for t, alt, az in A.track(topo, A.GC, a, b, 5):
            ok = alt_min <= alt <= alt_max and ((az < 180) == rising)
            if ok and cur and (t - cur[-1][0]) > timedelta(minutes=5):
                runs.append(cur); cur = []
            if ok:
                cur.append((t, alt, az))
            elif cur:
                runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    return max(runs, key=len)


def side(offset):
    if abs(offset) < 2:
        return "almost directly behind"
    return f"{abs(offset):.0f} degrees {'left' if offset < 0 else 'right'} of"


def build():
    events = []
    for nt in NIGHTS:
        cam = nt["cam"]
        topo = A.site(*cam)
        n = A.night_summary(topo, nt["evening"])
        pts = window(topo, n, nt["evening"].month <= 5, alt_min=8)
        start_t, end_t = pts[0][0], pts[-1][0]
        best = min(pts, key=lambda p: abs(p[1] - 30))
        bt, balt, baz = best
        day2 = nt["evening"] + timedelta(days=1)
        nm = min(NEW_MOONS, key=lambda d: abs((d.date() - nt["evening"]).days))
        illum = A.moon_illumination(bt)
        dist_home, _ = A.distance_bearing(*HOME, *cam)

        rows = []
        t = start_t.replace(minute=(start_t.minute // 30) * 30)
        while t <= end_t + timedelta(minutes=1):
            if t >= start_t:
                alt, az, _ = A.altaz(topo, A.GC, t)
                rows.append(f"{A.fmt(t)}  altitude {alt:.0f}°, azimuth {az:.0f}° {A.compass(az)}")
            t += timedelta(minutes=30)

        moon_bits = []
        for k in ("moonrise", "moonset"):
            if k in n:
                moon_bits.append(f"{k.replace('moon', 'Moon')} {n[k]:%a %H:%M}")

        comp = f"Face {A.compass(baz)} (azimuth {baz:.0f}°) at {A.fmt(bt)}."
        fov = None
        if nt["subject"]:
            d, b = A.distance_bearing(*cam, *nt["subject"])
            off = baz - b
            move = 2 * d * abs(__import__("math").sin(__import__("math").radians(off) / 2))
            comp = (f"{nt['subject_name']} is {d:.0f} m away on bearing {b:.0f}° ({A.compass(b)}). "
                    f"At {A.fmt(bt)} the core is {side(off)} it, {balt:.0f}° up.")
            if abs(off) >= 2:
                comp += (f" To stack the core straight above it, move about {move:.0f} m to your "
                         f"{'right' if off < 0 else 'left'}, keeping the same distance.")
            h, v = fov_deg(14)
            fov = dict(bearing=b, hfov=h, vfov=v, dist=d)

        desc = "\n".join([
            f"WHAT: {nt['what']}",
            f"Priority: {nt['priority']}",
            "",
            "WHEN (Sydney time)",
            f"Night of {nt['evening']:%a %d %b} into {day2:%a %d %b} 2027.",
            f"Shoot window: {A.fmt(start_t)} to {A.fmt(end_t)} (core between 8° and 60° high, sky fully dark, moon down).",
            f"Best composition: about {A.fmt(bt)}, core {balt:.0f}° high in the {A.compass(baz)}.",
            f"Arrive by {A.fmt(start_t - timedelta(minutes=45))} to set up and focus.",
            f"Sunset {A.fmt(n['sunset'])} · astronomical dusk {A.fmt(n['astro_dusk'])} · "
            f"astronomical dawn {A.fmt(n['astro_dawn'])} · sunrise {A.fmt(n['sunrise'])}",
            f"Moon: new moon {nm:%a %d %b %H:%M}. {illum:.0f}% lit and below the horizon during the window. "
            + (" · ".join(moon_bits) if moon_bits else ""),
            "",
            "CORE POSITION",
            *rows,
            "",
            "CAMERA POSITION",
            nt["cam_name"],
            f"Camera pin: {gmaps(*cam)}",
            *( [f"Subject pin ({nt['subject_name']}): {gmaps(*nt['subject'])}"] if nt["subject"] else [] ),
            comp,
            f"Straight line from Neutral Bay: about {dist_home/1000:.0f} km.",
            "",
            "KIT AND STARTING SETTINGS (Sony A1)",
            nt["kit"],
            f"12 mm f/2.8: ISO 3200, up to {npf_seconds(12, 2.8):.0f} s. 14 mm: up to {npf_seconds(14, 2.8):.0f} s. "
            f"24 mm: up to {npf_seconds(24, 2.8):.0f} s. 35 mm f/1.4: up to {npf_seconds(35, 1.4):.0f} s (NPF rule).",
            "Foreground: separate longer frames at ISO 800 to 1600, or blue hour frames from the same tripod position.",
            "Peak Design travel tripod, red head torch, dew heater strap on the lens.",
            "",
            "FIELD NOTES",
            *[f"- {x}" for x in nt["notes"]],
            "",
            "VERIFY BEFORE YOU GO",
            f"TPE Web (camera pin, subject pin and time set): {tpe(cam, nt['subject'], bt, fov)}",
            "PhotoPills: Planner > drop the pin at the camera coordinates > set the date and time above > "
            "Milky Way layer. Use Night AR on site to confirm the core path.",
            "Check cloud (BOM and Windy) and light pollution (lightpollutionmap.info) two days out.",
            "",
            "SOURCES",
            "Moon phases: US Naval Observatory 2027 table (aa.usno.navy.mil).",
            "Sun, moon and core positions: computed with Skyfield and JPL DE421 for the camera pin.",
            "Coordinates: OpenStreetMap. Terrain horizons: SRTM 30 m via OpenTopoData.",
        ])
        events.append(dict(
            uid=f"milkyway2027-{nt['evening']:%Y%m%d}@akumarau",
            start=start_t - timedelta(minutes=45), end=end_t,
            summary=f"Milky Way · {nt['site']} · {nt['title']}",
            location=nt["cam_name"], geo=cam, url=gmaps(*cam),
            description=desc, category="Astrophotography"))
        print(f"{nt['evening']}  {nt['site']:28s} window {A.fmt(start_t)}-{A.fmt(end_t)} best {A.fmt(bt)} alt {balt:.0f} az {baz:.0f}")
    path = write_calendar("milky-way-2027.ics", "Milky Way 2027", "Astro · Milky Way 2027", events)
    print(f"wrote {path} ({len(events)} events)")


if __name__ == "__main__":
    build()
