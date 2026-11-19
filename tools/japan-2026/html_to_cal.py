"""Turn an itinerary HTML file into an importable .ics and a Google Calendar .csv.
Events come from each day section's timeline, so the calendar always matches the page.
Usage: html_to_cal.py itinerary.html out.ics out.csv "Calendar name" uid_prefix sequence|auto [feed]
"""
import re, sys, html, csv, hashlib
from datetime import datetime, timezone, date, timedelta

src, ics_out, csv_out, calname, prefix, seq = sys.argv[1:7]
if seq == 'auto':  # minutes since 1 Nov 2026, always increases between builds
    import time
    seq = str(int((time.time() - 1793458800) // 60))
FEED = len(sys.argv) > 7 and sys.argv[7] == "feed"
TZ = {"Sydney": "Australia/Sydney", "Tokyo": "Asia/Tokyo", None: "Asia/Tokyo"}
s = open(src, encoding='utf-8').read()
NOW = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def text(x):
    x = re.sub(r'<br\s*/?>', '\n', x)
    x = re.sub(r'<[^>]+>', '', x)
    return html.unescape(x).strip()

def slug(x):
    return re.sub(r'[^a-z0-9]+', '-', x.lower()).strip('-')[:40]

events, alldays = [], []
for m in re.finditer(r"<section id='(d\d+)' class='card day' data-date='(\d{4})-(\d{2})-(\d{2})'>(.*?)</section>", s, re.S):
    dn, y, mo, d, sec = m.groups()
    ymd = y + mo + d
    h2 = text(re.search(r'<h2>(.*?)</h2>', sec, re.S).group(1))
    facts = [(text(a), text(b)) for a, b in re.findall(r'<dt>(.*?)</dt><dd[^>]*>(.*?)</dd>', sec, re.S)]
    wxs = re.search(r"data-wxshort='([^']+)'", sec)
    hotel = re.search(r"<div class='hotel'>.*?<h4>(.*?)</h4><p>(.*?)<br>", sec, re.S)
    lines = ['%s: %s' % (a, b) for a, b in facts]
    hotel_name = ''
    if hotel:
        hotel_name = text(hotel.group(1))
        lines.append('Hotel tonight: %s, %s' % (hotel_name, text(hotel.group(2))))
    photo = re.search(r"<div class='photo'>(.*?)<div class='hk' style", sec, re.S)
    if photo:
        lines += ['Camera ' + text(p) for p in re.findall(r'<p><b>.*?</p>', photo.group(1), re.S)]
    notes = re.search(r"<ul class='notes'>(.*?)</ul>", sec, re.S)
    if notes:
        lines += [text(li) for li in re.findall(r'<li>(.*?)</li>', notes.group(1), re.S)]
    alldays.append(dict(date=ymd, title='%s | %s%s' % (dn.upper(), h2, (' | ' + html.unescape(wxs.group(1))) if wxs else ''), desc='\n'.join(lines), loc=hotel_name))
    for li in re.findall(r"<li class='ev ([a-z ]+)'>(.*?)</div></div></li>", sec, re.S):
        kind, body = li
        tt = re.search(r"<div class='t'>(\d\d):(\d\d)(?:<small>(Sydney|Tokyo)</small>)?<small>to (\d\d):(\d\d)(?: (Sydney|Tokyo))?( \+1)?</small></div>", body)
        if not tt:
            continue
        h1, m1, stz, h2_, m2, etz, plus = tt.groups()
        stz = TZ[stz]; etz = TZ[etz] if etz else stz
        title = text(re.sub(r"<span class='tag'>.*?</span>", '', re.search(r'<h4>(.*?)</h4>', body, re.S).group(1)))
        loc = text(re.search(r"<p class='loc'>(.*?)</p>", body, re.S).group(1))
        paras = [text(p) for p in re.findall(r'<p>(.*?)</p>', body, re.S)]
        extra = re.search(r"<details>.*?</details>", body, re.S)
        if extra:
            paras += [text(li) for li in re.findall(r'<li>(.*?)</li>', extra.group(0), re.S)]
        maplink = re.search(r"<a class='btn' href='([^']+)'[^>]*>Map</a>", body)
        url = html.unescape(maplink.group(1)) if maplink else ''
        if url:
            paras.insert(0, 'Google Maps: ' + url)
        start = h1 + m1
        end = h2_ + m2
        edate = ymd
        if plus:
            edate = (date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:])) + timedelta(days=1)).strftime('%Y%m%d')
        elif stz == etz and end <= start:  # zero length: give it 15 minutes
            e = datetime(2000, 1, 1, int(h1), int(m1)) + timedelta(minutes=15)
            end = e.strftime('%H%M')
        if kind.strip() == 'opt' and 'optional' not in title.lower():
            title += ' (optional)'
        events.append(dict(date=ymd, edate=edate, stz=stz, etz=etz, start=start, end=end, title=title, loc=loc, url=url, desc='\n'.join(p for p in paras if p)))

# ---- ICS
def esc(x):
    return x.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

def fold(line):
    out, cur, limit = [], b'', 75
    for ch in line:
        cb = ch.encode('utf-8')
        if len(cur) + len(cb) > limit:
            out.append(cur.decode('utf-8')); cur = b''; limit = 74
        cur += cb
    out.append(cur.decode('utf-8'))
    return '\r\n '.join(out)

def nextday(ymd):
    return (date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:])) + timedelta(days=1)).strftime('%Y%m%d')

L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//akumarau//%s//EN' % calname, 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
     'X-WR-CALNAME:%s' % calname, 'X-WR-TIMEZONE:Asia/Tokyo',
     'BEGIN:VTIMEZONE', 'TZID:Asia/Tokyo', 'BEGIN:STANDARD', 'DTSTART:19700101T000000', 'TZOFFSETFROM:+0900', 'TZOFFSETTO:+0900', 'TZNAME:JST', 'END:STANDARD', 'END:VTIMEZONE',
     'BEGIN:VTIMEZONE', 'TZID:Australia/Sydney', 'BEGIN:STANDARD', 'DTSTART:19700405T030000', 'RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU', 'TZOFFSETFROM:+1100', 'TZOFFSETTO:+1000', 'TZNAME:AEST', 'END:STANDARD',
     'BEGIN:DAYLIGHT', 'DTSTART:19701004T020000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=1SU', 'TZOFFSETFROM:+1000', 'TZOFFSETTO:+1100', 'TZNAME:AEDT', 'END:DAYLIGHT', 'END:VTIMEZONE']
if FEED:
    L[7:7] = ['REFRESH-INTERVAL;VALUE=DURATION:PT1H', 'X-PUBLISHED-TTL:PT1H']
for a in alldays:
    L += ['BEGIN:VEVENT', 'UID:%s-day-%s@akumarau' % (prefix, a['date']), 'DTSTAMP:' + NOW, 'SEQUENCE:' + seq,
          'DTSTART;VALUE=DATE:' + a['date'], 'DTEND;VALUE=DATE:' + nextday(a['date']),
          'SUMMARY:' + esc(a['title']), 'LOCATION:' + esc(a['loc']), 'DESCRIPTION:' + esc(a['desc']),
          'TRANSP:TRANSPARENT', 'END:VEVENT']
seen = {}
for e in events:
    key = '%s-%s' % (e['date'], slug(e['title']))
    seen[key] = seen.get(key, 0) + 1
    uid = '%s-%s%s@akumarau' % (prefix, key, '' if seen[key] == 1 else '-%d' % seen[key])
    L += ['BEGIN:VEVENT', 'UID:' + uid, 'DTSTAMP:' + NOW, 'SEQUENCE:' + seq,
          'DTSTART;TZID=%s:%sT%s00' % (e['stz'], e['date'], e['start']), 'DTEND;TZID=%s:%sT%s00' % (e['etz'], e['edate'], e['end']),
          'SUMMARY:' + esc(e['title']), 'LOCATION:' + esc(e['loc']), 'DESCRIPTION:' + esc(e['desc'])]
    if e.get('url'):
        L.append('URL:' + e['url'])
    L += ['TRANSP:OPAQUE', 'END:VEVENT']
L.append('END:VCALENDAR')
with open(ics_out, 'w', encoding='utf-8', newline='') as f:
    f.write('\r\n'.join(fold(x) for x in L) + '\r\n')

# ---- Google CSV (times are read in the Google calendar's own time zone)
def us(ymd):
    return '%s/%s/%s' % (ymd[4:6], ymd[6:], ymd[:4])
def ampm(hm):
    h, m = int(hm[:2]), hm[2:]
    return '%d:%s %s' % ((h % 12) or 12, m, 'AM' if h < 12 else 'PM')
with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location', 'Private'])
    for a in alldays:
        w.writerow([a['title'], us(a['date']), '', us(a['date']), '', 'True', a['desc'], a['loc'], 'False'])
    for e in events:
        w.writerow([e['title'], us(e['date']), ampm(e['start']), us(e['date']), ampm(e['end']), 'False', e['desc'], e['loc'], 'False'])
print('days', len(alldays), 'events', len(events))
