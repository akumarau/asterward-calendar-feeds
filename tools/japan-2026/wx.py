"""Add a daily weather row to each upcoming day of the personal itinerary.

Usage: python3 wx.py <html_in> <forecast.json> <html_out> <today YYYY-MM-DD> <checked label>
forecast.json is the Open-Meteo response for PLACES (same order), fetched with
  https://api.open-meteo.com/v1/forecast?latitude=<lats>&longitude=<lons>
  &daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code
  &timezone=Asia/Tokyo&forecast_days=16
"""
import json, re, sys, html as H

PLACES = [  # name, lat, lon
    ('Tokyo', 35.68, 139.76), ('Hakone', 35.25, 139.05), ('Takayama', 36.14, 137.25),
    ('Kyoto', 35.00, 135.77), ('Osaka', 34.67, 135.50), ('Nara', 34.685, 135.84),
    ('Koyasan', 34.21, 135.59), ('Hiroshima', 34.39, 132.46), ('Miyajima', 34.30, 132.32),
    ('Mihara', 34.40, 133.08)]
# where you spend each day, in the order you are there
DAYS = {'2026-11-16': ['Tokyo'], '2026-11-17': ['Tokyo'], '2026-11-18': ['Tokyo'],
        '2026-11-19': ['Hakone'], '2026-11-20': ['Takayama'], '2026-11-21': ['Takayama', 'Kyoto'],
        '2026-11-22': ['Kyoto'], '2026-11-23': ['Kyoto'], '2026-11-24': ['Kyoto', 'Osaka'],
        '2026-11-25': ['Osaka'], '2026-11-26': ['Nara', 'Koyasan'], '2026-11-27': ['Koyasan', 'Hiroshima'],
        '2026-11-28': ['Miyajima'], '2026-11-29': ['Hiroshima', 'Mihara'], '2026-11-30': ['Mihara']}

def sky(code, rain):
    if code in (71, 73, 75, 77, 85, 86):
        return 'snow likely' if rain >= 50 else 'snow possible'
    if code >= 95: return 'thunderstorms'
    if rain >= 60: return 'rain likely'
    if rain >= 30: return 'chance of showers'
    if code in (0, 1): return 'sunny'
    if code == 2: return 'partly cloudy'
    if code in (45, 48): return 'foggy'
    return 'cloudy'

def t(x):
    v = round(x)
    return '−%d' % -v if v < 0 else '%d' % v

def advice(lo, hi, rain, code):
    a = []
    if lo <= 2: a.append('Thermals, warm jacket, gloves and beanie.')
    elif lo <= 7: a.append('Warm jacket with a layer underneath.')
    elif hi >= 18: a.append('Light layers.')
    else: a.append('Light jacket.')
    if code in (71, 73, 75, 77, 85, 86): a.append('Waterproof shoes, paths may be icy.')
    if rain >= 60: a.append('Umbrella, and the rain cover on the camera bag.')
    elif rain >= 30: a.append('Small umbrella.')
    if lo <= 3: a.append('Spare battery in an inner pocket.')
    return 'Wear: ' + ' '.join(a)

src, fj, dst, today, checked = sys.argv[1:6]
s = open(src, encoding='utf-8').read()
data = json.load(open(fj))
if isinstance(data, dict): data = [data]
fc = {}
for (name, _, _), d in zip(PLACES, data):
    dd = d['daily']
    for i, day in enumerate(dd['time']):
        fc[(name, day)] = (dd['temperature_2m_min'][i], dd['temperature_2m_max'][i],
                           dd['precipitation_probability_max'][i] or 0, dd['weather_code'][i])
CSS = ".facts dd.wx small{display:block;color:var(--muted,#6b6b6b);font-size:.82em;margin-top:2px}"
if 'dd.wx small' not in s:
    s = s.replace('</style>', CSS + '</style>', 1)
done = 0
for m in list(re.finditer(r"<section id='(d\d+)' class='card day' data-date='([\d-]+)'>.*?</section>", s, re.S)):
    date = m.group(2)
    if date < today or date not in DAYS: continue
    parts, short, worst = [], None, None
    for name in DAYS[date]:
        if (name, date) not in fc: continue
        lo, hi, rain, code = fc[(name, date)]
        parts.append('%s %s to %s °C, %s (%d%%)' % (name, t(lo), t(hi), sky(code, rain), rain))
        cand = (min(lo, worst[0]) if worst else lo, max(hi, worst[1]) if worst else hi,
                max(rain, worst[2]) if worst else rain, code if not worst or code > worst[3] else worst[3])
        worst = cand
    if not parts: continue
    short = '%s to %s \u00b0C' % (t(worst[0]), t(worst[1]))
    row = ("<div class='wxrow'><dt>Weather</dt><dd class='wx' data-wxshort='%s'>%s<br>%s <small>Forecast checked %s</small></dd></div>"
           % (H.escape(short), H.escape('. '.join(parts)) + '.', H.escape(advice(*worst)), H.escape(checked)))
    sec = m.group(0)
    sec2 = re.sub(r"<div class='wxrow'>.*?</div>", '', sec, flags=re.S)
    sec2 = sec2.replace("<dl class='facts'>", "<dl class='facts'>" + row, 1)
    s = s.replace(sec, sec2, 1); done += 1
open(dst, 'w', encoding='utf-8').write(s)
print('weather rows', done)
