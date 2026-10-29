# Asterward calendar feeds for Outlook

This repository publishes subscribable `.ics` calendars through GitHub Pages.
Each calendar shows up in Outlook as its own calendar, and Outlook refreshes it automatically.

This repository is public. Never put booking references, account numbers or other private details in a feed.

## Feeds

| Calendar | File | Subscription URL | How it updates |
|---|---|---|---|
| Sydney Motorsport Park | `docs/calendar.ics` | `https://akumarau.github.io/asterward-calendar-feeds/calendar.ics` | GitHub Actions scraper, daily |
| Japan Trip 2026 | `docs/japan-2026.ics` | `https://akumarau.github.io/asterward-calendar-feeds/japan-2026.ics` | Hand built from `calendars/japan_2026.py` |

## Add a feed to Outlook

In Outlook choose **Calendar**, then **Add calendar**, then **Subscribe from web**.
Paste the subscription URL and give the calendar a name.

Subscribed calendars are read only in Outlook. Make changes here, and Outlook picks them up within a few hours.

## Hand built calendars

Each hand built calendar has a Python generator in `calendars/` that writes its feed into `docs/`.

To change one:

1. Edit the events in the generator, for example `calendars/japan_2026.py`.
2. Run `python calendars/japan_2026.py`.
3. Commit the generator and the updated file in `docs/`.

Keep event UIDs stable so Outlook updates events instead of duplicating them.

To add a new calendar, copy an existing generator, change the output file name and the events, then add a row to the table above.

## Sydney Motorsport Park scraper

The SMSP feed is generated from the public Sydney Motorsport Park event calendar:

https://events.sydneymotorsportpark.com.au/eventcalendar/s/

### How it works

1. GitHub Actions runs the scraper daily.
2. Playwright opens the dynamically rendered SMSP calendar.
3. The scraper extracts event data from structured data and rendered event links.
4. It writes:
   * `docs/calendar.ics`
   * `docs/events.json`
   * `docs/debug.json`

The workflow only commits those three files. It never touches the hand built calendars.

### Run manually

Open **Actions → Update Sydney Motorsport Park calendar → Run workflow**.

### Diagnostics

If the scraper fails to discover events, inspect `docs/debug.json`.
It records a preview of the rendered page, candidate event links, and a limited sample of JSON responses captured while the page loads.

### Notes

* Timed SMSP events use `Australia/Sydney`.
* Stable event UIDs are generated from event URLs, so normal updates do not create duplicates.
* All day events use date values.

## GitHub Pages setup

**Settings → Pages**, under **Build and deployment**:

* **Source:** Deploy from a branch
* **Branch:** `main`
* **Folder:** `/docs`
