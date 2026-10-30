#!/usr/bin/env python3
"""Rebuild calendars/data/bom_tides_2027.json from the BOM 2027 NSW tide table PDFs.

Run: pip install pdfplumber && python calendars/bom_tides.py
Only needed if BOM republishes the tables. The JSON is committed.
"""
import calendar
import json
import os
import re
import urllib.request

import pdfplumber

YEAR = 2027
HERE = os.path.dirname(os.path.abspath(__file__))
STATIONS = {"Newcastle": "TP004", "Port Kembla": "TP006", "Sydney (Fort Denison)": "TP007"}
URL = "https://www.bom.gov.au/ntc/IDO59001/IDO59001_{y}_NSW_{code}.pdf"
MONTHS = [m.upper() for m in calendar.month_name]


def parse(path):
    out = {}
    pdf = pdfplumber.open(path)
    for page in pdf.pages[:3]:  # page 4 is the conditions of use
        ws = page.extract_words()
        mnums = [MONTHS.index(w["text"].upper()) for w in
                 sorted((w for w in ws if w["text"].upper() in MONTHS[1:]), key=lambda w: w["x0"])]
        times = []
        for w in ws:
            # Weekday labels sometimes merge with a time, e.g. "WE1724". Align on the right edge.
            m = re.fullmatch(r"(?:[A-Z]{2})?(\d{4})", w["text"])
            if m and w["top"] > 105:
                times.append(dict(w, text=m.group(1), x0=w["x1"] - 19.5))
        heights = [w for w in ws if re.fullmatch(r"-?\d\.\d\d", w["text"])]
        cols = sorted({round(w["x0"] / 5) * 5 for w in times})
        cols = [c for c in cols if sum(1 for w in times if abs(w["x0"] - c) < 6) > 20]
        assert len(cols) == 8, (path, cols)
        for ci, cx in enumerate(cols):
            month, first = mnums[ci // 2], 1 if ci % 2 == 0 else 16
            ndays = 15 if first == 1 else calendar.monthrange(YEAR, month)[1] - 15
            rows = []
            for t in sorted((w for w in times if abs(w["x0"] - cx) < 6), key=lambda w: w["top"]):
                h = min((h for h in heights if 0 < h["x0"] - t["x0"] < 40 and abs(h["top"] - t["top"]) < 2),
                        key=lambda h: h["x0"] - t["x0"])
                rows.append((t["top"], t["text"], float(h["text"])))
            dn = sorted((w for w in ws if re.fullmatch(r"\d{1,2}", w["text"]) and -30 < w["x0"] - cx < -2
                         and w["top"] > 105), key=lambda w: w["top"])
            assert [int(w["text"]) for w in dn] == list(range(first, first + ndays)), (path, month, first)
            for k, w in enumerate(dn):
                lo = w["top"] - 6
                hi = dn[k + 1]["top"] - 6 if k + 1 < len(dn) else 1e9
                b = [r for r in rows if lo <= r[0] < hi]
                assert 2 <= len(b) <= 4, (path, month, first + k)
                out[f"{YEAR}-{month:02d}-{first + k:02d}"] = [(r[1][:2] + ":" + r[1][2:], r[2]) for r in b]
    seq = [(d, t, h) for d in sorted(out) for t, h in out[d]]
    lab = {}
    for i, (d, t, h) in enumerate(seq):
        nb = [seq[j][2] for j in (i - 1, i + 1) if 0 <= j < len(seq)]
        lab[(d, t)] = "High" if all(h > x for x in nb) else "Low" if all(h < x for x in nb) else "?"
    assert "?" not in lab.values(), path
    return {d: [[t, h, lab[(d, t)]] for t, h in out[d]] for d in sorted(out)}


def main():
    data = {"source": f"Bureau of Meteorology {YEAR} NSW tide predictions (IDO59001)",
            "copyright": "Copyright Commonwealth of Australia 2026, Bureau of Meteorology",
            "notes": "Local time: AEST (UTC+10) or AEDT (UTC+11) when in effect. "
                     "Heights in metres above Lowest Astronomical Tide.",
            "stations": {}}
    for name, code in STATIONS.items():
        url = URL.format(y=YEAR, code=code)
        path = os.path.join(HERE, f"{code}.pdf")
        # BOM rejects the default Python user agent.
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (astro calendar build)"})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
        data["stations"][name] = {"pdf": url, "days": parse(path)}
        os.remove(path)
        print(name, len(data["stations"][name]["days"]), "days")
    with open(os.path.join(HERE, "data", f"bom_tides_{YEAR}.json"), "w") as f:
        json.dump(data, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
