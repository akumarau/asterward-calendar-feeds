#!/usr/bin/env python3
"""Build docs/milky-way-2027.ics: Milky Way core shoots near Sydney, Feb to Oct 2027.

Run: python calendars/milky_way_2027.py   (needs: pip install -r calendars/requirements-astro.txt)

Sessions sit on the Saturday night closest to each new moon. June and early July
are left out for the Europe trip. Sky positions are computed at build time.
"""
from datetime import date, datetime, timedelta

import astro_engine as A
from astro_ics import fov_deg, gmaps, npf_seconds, tpe, write_calendar
import astro_tides as TD

HOME = (-33.8366, 151.2190)  # Neutral Bay, for straight line distance only
NEW_MOONS = [dt.astimezone(A.SYD) for dt, n in A.moon_phases(2027) if n == "New Moon"]

KIT_WIDE = ("FE 12-24mm F2.8 GM at 12 to 14 mm for single frames. "
            "FE 35mm F1.4 GM II for a sharper multi row panorama.")
PROXY = {
    "Port Kembla": "Port Kembla is the nearest BOM standard port. Treat times as approximate for this site.",
    "Newcastle": "Newcastle is the nearest BOM standard port. Treat times as approximate for this site.",
    "Sydney (Fort Denison)": "Fort Denison is the nearest BOM standard port. Treat times as approximate for this site.",
}
CAVE_SAFETY = [
    "SEA CAVE SAFETY: scout the cave, the approach and your exit in daylight on an earlier visit.",
    "Only go in on a falling or low tide with small swell. Leave the cave by the time shown, whatever the shot.",
    "Never go alone. Carry a phone in a dry bag and a spare head torch. Watch every set of waves.",
]

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
                "Light from the lighthouse beam sweeps the frame. Time exposures between passes or blend."],
         tide="Newcastle"),
    dict(evening=date(2027, 3, 5), priority="Optional", region="Kiama",
         site="Little Blowhole", title="Core rising over the Little Blowhole rock platform",
         cam=(-34.68671, 150.85915), cam_name="Little Blowhole, off Tingira Crescent, Kiama NSW 2533",
         subject=None, subject_name=None,
         what="The core rising out of the Pacific above the dark volcanic rock platform and the Little Blowhole. "
              "Pairs with Cathedral Rocks the next night for one Kiama weekend.",
         kit=KIT_WIDE,
         notes=["Access: car park and lookout off Tingira Crescent, about 2 km south of Kiama town. "
                "The site is a little hard to find, so check it in daylight.",
                "Official listing: free entry, car park, lookouts. Not suitable for people with access needs.",
                "The blowhole fires best with a north east swell. That same swell makes the platform dangerous. "
                "Shoot from the lookout if waves reach the rocks.",
                "Clear ocean horizon to the ESE. No terrain above 1 degree."],
         tide="Port Kembla",
         tide_limit_min=90),
    dict(evening=date(2027, 3, 6), priority="High", region="Kiama Downs",
         site="Cathedral Rocks", title="Core over the rock stacks and through the sea cave",
         cam=(-34.64444, 150.85547), cam_name="Cliff Drive viewpoint above Cathedral Rocks, Kiama Downs NSW 2533",
         subject=(-34.64481, 150.85670), subject_name="Cathedral Rocks sea stacks",
         what="Two compositions. First, the core framed by the sea cave in the cliff, looking out to the main "
              "sea stack, while the tide is low. Second, the core rising over the Cathedral Rocks sea stacks from "
              "the cliff top, which works all night.",
         kit=KIT_WIDE,
         notes=["Access: park opposite Moona Avenue on North Kiama Drive, take a path down to Jones Beach, "
                "turn right and walk to the headland.",
                "The cave sits in the cliff with a framed view of a main sea stack. Its exact spot and mouth "
                "direction are not mapped, so drop your own pin on the daylight scout and check the core line "
                "with PhotoPills Night AR.",
                "The cliff top viewpoint needs no tide. Move up there once the cave window closes.",
                "Long exposure smooths the surf around the stacks. Shoot the foreground at blue hour if possible."],
         tide="Port Kembla",
         cave=dict(name="Cathedral Rocks sea cave", access=(-34.63931, 150.85258),
                   access_name="Parking opposite Moona Avenue, North Kiama Drive, Kiama Downs NSW 2533",
                   tide_limit_min=90)),
    dict(evening=date(2027, 4, 2), priority="Optional", region="Newcastle",
         site="Bogey Hole", title="Core over the convict cut ocean pool",
         cam=(-32.93522, 151.78164), cam_name="The Bogey Hole, below King Edward Park, York Drive, Newcastle NSW 2300",
         subject=None, subject_name=None,
         what="The core rising over the Tasman Sea above the Bogey Hole, the ocean pool cut into the rock "
              "platform by convicts in about 1820. Pairs with the Caves Beach sea caves the next night.",
         kit=KIT_WIDE,
         notes=["Access: steps lead down from King Edward Park to the pool platform. Park on York Drive or at "
                "the top of The Terrace and walk down through the park.",
                "Official listing: free entry. Not suitable for people with access needs.",
                "Waves break over the pool in any real swell, and people have been washed off these rocks. "
                "Shoot from the steps or the cliff top if sets reach the platform.",
                "Open ocean to the ESE. Newcastle city glow sits behind you to the west."],
         tide="Newcastle",
         tide_limit_min=90),
    dict(evening=date(2027, 4, 3), priority="Optional", region="Lake Macquarie",
         site="Caves Beach sea caves", title="Core rising through the sea caves",
         cam=(-33.11041, 151.64770), cam_name="Caves Beach, south end sea caves, below Caves Beach Road, Caves Beach NSW 2281",
         subject=None, subject_name=None,
         what="The core rising over the Pacific, framed by the sea cave openings at the south end of Caves Beach. "
              "The shoot window is set by the low tide, not just the sky.",
         kit=KIT_WIDE,
         notes=["Access: free parking above the Surf Life Saving Club. Walk down to the beach and turn right to the "
                "southern end. A track over the rocks leads to the caves.",
                "The camera pin is the beach. The cave openings are not mapped, so drop your own pin on the daylight "
                "scout and check which opening faces the ESE core with PhotoPills Night AR.",
                "Rocks outside the caves are mossy and slippery. Some openings need crawling. Wear grippy shoes.",
                "Backup night: Fri 2 Apr (low tide 00:30, 0.80 m). That is also the Bogey Hole night, 30 minutes "
                "north, so swap the two if Friday looks clearer.",
                "About 1 h 45 min north of Neutral Bay.",
                "Daylight saving ends at 03:00 this night and clocks go back to 02:00. "
                "Every time in this event is before the change, in AEDT."],
         tide="Newcastle",
         tide_limit_min=90),
    dict(evening=date(2027, 4, 10), priority="Very high", region="Kiama",
         site="Bombo Headland Quarry", title="Core above the basalt columns",
         cam=(-34.65005, 150.86242), cam_name="Bombo Headland Quarry Geological Site viewpoint, Commissioners Lane, Bombo NSW 2533",
         subject=(-34.65037, 150.86344), subject_name="Bombo basalt columns",
         what="The core rising in the east above the hexagonal basalt columns of the old Bombo quarry, "
              "with the ocean behind. The best core position of the coastal set.",
         kit=KIT_WIDE,
         notes=["Confirm current track and car park access with Kiama Council before the trip.",
                "Old quarry: loose rock and drop offs. Scout in daylight and keep to marked paths.",
                "The columns can block the lowest part of the core. Shoot from the upper terrace.",
                "A low level light panel on the columns from the side adds texture. Keep it dim."],
         tide="Port Kembla"),
    dict(evening=date(2027, 5, 1), priority="Optional", region="Central Coast",
         site="The Skillion, Terrigal", title="Core rising over the Skillion headland",
         cam=(-33.45104, 151.45173), cam_name="The Skillion, Terrigal Haven, Terrigal NSW 2260",
         subject=None, subject_name=None,
         what="The core rising over the open Pacific from the grassy Skillion headland, with the steep slope "
              "dropping to the sea in the foreground. No tide limit, so it is the easiest night of the set.",
         kit=KIT_WIDE,
         notes=["Access: free car park at Terrigal Haven by the boat ramp. Cross the oval, then take the short "
                "steep path to the summit lookout above the pin.",
                "The headland ends in sheer cliffs with no fence on parts of the top. Stay well back from the edge.",
                "Clear ocean horizon to the ESE. Terrigal town lights sit behind you.",
                "About 1 h 15 min north of Neutral Bay."],
         tide="Sydney (Fort Denison)"),
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
                "The bridge carries traffic. Avoid headlights by timing exposures, or stack frames. "
                "Never set up or stop on the carriageway.",
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
                "Light pollution is moderate here. Stop shooting once the core drops below about 12 degrees.",
                "Stay on the public foreshore. Keep off private jetties and moorings."],
         tide="Sydney (Fort Denison)"),
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
        low = None
        if nt.get("tide_limit_min"):
            low = TD.nearest_low(nt["tide"], pts[len(pts) // 2][0])
            lim = timedelta(minutes=nt["tide_limit_min"])
            pts = [p for p in pts if abs(p[0] - low[0]) <= lim]
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

        cave_lines = []
        if nt.get("cave"):
            cv = nt["cave"]
            clow = TD.nearest_low(nt["tide"], bt)
            lim = timedelta(minutes=cv["tide_limit_min"])
            cpts = [p for p in pts if abs(p[0] - clow[0]) <= lim]
            cs, ce = cpts[0], cpts[-1]
            cave_lines = [
                "",
                f"SEA CAVE WINDOW ({cv['name']})",
                f"{A.fmt(cs[0])} to {A.fmt(ce[0])}: low tide {A.fmt(clow[0])} ({clow[1]:.2f} m) plus or minus "
                f"{cv['tide_limit_min']} minutes, inside the dark sky window.",
                f"Core {cs[1]:.0f}° high at {cs[2]:.0f}° {A.compass(cs[2])} at the start, "
                f"{ce[1]:.0f}° at {ce[2]:.0f}° at the end.",
                f"Be out of the cave by {A.fmt(ce[0])}. Then shoot the stacks from the cliff top until {A.fmt(end_t)}.",
                f"Access pin: {gmaps(*cv['access'])} ({cv['access_name']})",
                *CAVE_SAFETY,
            ]
        tide_lines = []
        if nt.get("tide"):
            tide_lines = [""] + TD.section(nt["tide"], PROXY[nt["tide"]], start_t, end_t, at=bt,
                                           label="best composition",
                                           rock=nt["site"] in ("Norah Head Lighthouse", "Cathedral Rocks",
                                                               "Caves Beach sea caves", "Little Blowhole",
                                                               "Bogey Hole"))
        if nt.get("tide_limit_min"):
            tide_lines.insert(3, f"The window above is cut to low tide {A.fmt(low[0])} ({low[1]:.2f} m) plus or "
                                 f"minus {nt['tide_limit_min']} minutes.")
        desc = "\n".join([
            f"WHAT: {nt['what']}",
            f"Priority: {nt['priority']}",
            "",
            "WHEN (Sydney time)",
            f"Night of {nt['evening']:%a %d %b} into {day2:%a %d %b} 2027.",
            f"Shoot window: {A.fmt(start_t)} to {A.fmt(end_t)} (core between 8° and 60° high, sky fully dark, moon down"
            + (", low tide" if nt.get("tide_limit_min") else "") + ").",
            *([f"Rock platform shoot: the window is cut to low tide plus or minus {nt['tide_limit_min']} minutes."]
              if nt.get("tide_limit_min") and "cave" not in nt["site"].lower() else []),
            f"Best composition: about {A.fmt(bt)}, core {balt:.0f}° high in the {A.compass(baz)}.",
            f"Arrive by {A.fmt(start_t - timedelta(minutes=45))} to set up and focus.",
            f"Sunset {A.fmt(n['sunset'])} · astronomical dusk {A.fmt(n['astro_dusk'])} · "
            f"astronomical dawn {A.fmt(n['astro_dawn'])} · sunrise {A.fmt(n['sunrise'])}",
            f"Moon: new moon {nm:%a %d %b %H:%M}. {illum:.0f}% lit and below the horizon during the window. "
            + (" · ".join(moon_bits) if moon_bits else ""),
            "",
            "CORE POSITION",
            *rows,
            *cave_lines,
            *tide_lines,
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
            *([f"- {x}" for x in CAVE_SAFETY] if "cave" in nt["site"].lower() else []),
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
            *([TD.BOM_NOTE] if nt.get("tide") else []),
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
