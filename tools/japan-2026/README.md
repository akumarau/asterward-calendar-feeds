# Japan 2026 feed tools

`docs/japan-2026.ics` is built from Anupam's private itinerary page (kept in iCloud, not in this repo).

- `wx.py` adds a daily weather row to each upcoming day of that page (Open-Meteo forecast).
- `html_to_cal.py` turns the page into the subscribed calendar feed.
- `foldbake.py` folds the page around today (past days closed, today open, coming days closed), written into the HTML so it works in the iPhone Files preview, which runs no scripts.

Daily refresh, run by a scheduled task until 30 Nov 2026:

```
python3 -I wx.py itinerary.html forecast.json itinerary.html YYYY-MM-DD "19 Nov, 05:40"
python3 -I foldbake.py itinerary.html itinerary.html YYYY-MM-DD
python3 -I html_to_cal.py itinerary.html ../../docs/japan-2026.ics /tmp/unused.csv "Japan Trip 2026" japan2026 auto feed
```
