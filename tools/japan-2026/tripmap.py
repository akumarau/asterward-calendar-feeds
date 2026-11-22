"""Build the trip map card (inline SVG) and insert it after the overview card.
Usage: tripmap.py <html_in> <html_out> <countries-10m.json>"""
import json, math, re, sys

src, dst, topo = sys.argv[1:4]
LON0, LON1, LAT0, LAT1 = 131.6, 140.4, 33.55, 36.75
W = 760
K = math.cos(math.radians(35.2))
SX = W / ((LON1 - LON0) * K)
H = round((LAT1 - LAT0) * SX)

def P(lon, lat):
    return ((lon - LON0) * K * SX, (LAT1 - lat) * SX)

# ---- coastline from Natural Earth via world-atlas (public domain)
t = json.load(open(topo))
sc, tr = t['transform']['scale'], t['transform']['translate']
arcs = []
for a in t['arcs']:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy
        pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
    arcs.append(pts)
def arc(i):
    return arcs[i] if i >= 0 else arcs[~i][::-1]
jp = [g for g in t['objects']['countries']['geometries'] if g['properties'].get('name') == 'Japan'][0]
polys = jp['arcs'] if jp['type'] == 'MultiPolygon' else [jp['arcs']]
paths = []
for poly in polys:
    ring = []
    for i in poly[0]:
        ring += arc(i)
    if not any(LON0 - 1 < lo < LON1 + 1 and LAT0 - 1 < la < LAT1 + 1 for lo, la in ring):
        continue
    pts, last = [], None
    for lo, la in ring:
        x, y = P(lo, la)
        if last is None or abs(x - last[0]) + abs(y - last[1]) > 1.2:
            pts.append((x, y)); last = (x, y)
    if len(pts) < 4: continue
    paths.append('M' + 'L'.join('%.1f,%.1f' % p for p in pts) + 'Z')
land = ''.join(paths)

# ---- stops: key, name, lat, lon, days, label offset (dx, dy, anchor), dates
STOPS = [
    ('tokyo', 'Tokyo', 35.73, 139.77, 'D1 to D3', (10, -8, 'start'), ['2026-11-15', '2026-11-16', '2026-11-17', '2026-11-18']),
    ('hakone', 'Hakone', 35.25, 139.05, 'D4', (0, 22, 'middle'), ['2026-11-19']),
    ('takayama', 'Takayama', 36.14, 137.25, 'D5', (10, -6, 'start'), ['2026-11-20']),
    ('kyoto', 'Kyoto', 35.01, 135.77, 'D6 to D8', (-10, -16, 'end'), ['2026-11-21', '2026-11-22', '2026-11-23']),
    ('osaka', 'Osaka', 34.67, 135.50, 'D9 to D10', (-12, 10, 'end'), ['2026-11-24', '2026-11-25']),
    ('nara', 'Nara', 34.685, 135.84, 'D11 day trip', (10, 0, 'start'), []),
    ('koyasan', 'Koyasan', 34.21, 135.59, 'D11', (10, 12, 'start'), ['2026-11-26']),
    ('hiroshima', 'Hiroshima', 34.39, 132.46, 'D12 to D14', (-4, -26, 'middle'), ['2026-11-27', '2026-11-28']),
    ('miyajima', 'Miyajima', 34.30, 132.32, 'D13 day trip', (-22, 22, 'start'), []),
    ('mihara', 'Mihara', 34.40, 133.08, 'D14 night, D15 fly home', (10, 20, 'start'), ['2026-11-29', '2026-11-30']),
]
VIA = {'nagoya': ('Nagoya', 35.17, 136.88)}
S = {k: P(lon, lat) for k, _, lat, lon, *_ in STOPS}
S['nagoya'] = P(VIA['nagoya'][2], VIA['nagoya'][1])
S['hij'] = P(132.92, 34.44)
ROUTE = ['tokyo', 'hakone', 'nagoya', 'takayama', 'nagoya', 'kyoto', 'osaka', 'koyasan', 'osaka', 'hiroshima', 'mihara']
SIDE = [('osaka', 'nara'), ('hiroshima', 'miyajima')]

def line(a, b, cls):
    (x1, y1), (x2, y2) = S[a], S[b]
    return "<line class='%s' x1='%.1f' y1='%.1f' x2='%.1f' y2='%.1f'/>" % (cls, x1, y1, x2, y2)

segs = []
done = set()
for a, b in zip(ROUTE, ROUTE[1:]):
    key = tuple(sorted((a, b)))
    segs.append(line(a, b, 'rt' if key not in done else 'rt back'))
    done.add(key)
segs += [line(a, b, 'rt side') for a, b in SIDE]
nx, ny = S['nagoya']
via = ("<circle class='via' cx='%.1f' cy='%.1f' r='3.5'/><text class='vl' x='%.1f' y='%.1f' text-anchor='middle'>Nagoya (change trains)</text>"
       % (nx, ny, nx, ny + 16))
hx, hy = S['hij']
plane = ("<g class='fly'><circle cx='%.1f' cy='%.1f' r='3.5'/><text class='vl' x='%.1f' y='%.1f' text-anchor='middle'>Hiroshima Airport</text></g>"
         % (hx, hy, hx, hy - 10))
dots = []
for k, name, lat, lon, days, (dx, dy, anc), dates in STOPS:
    x, y = S[k]
    side = not dates
    dots.append(
        "<g class='stop%s' data-k='%s' data-dates='%s'><circle class='halo' cx='%.1f' cy='%.1f' r='13'/>"
        "<circle class='dot' cx='%.1f' cy='%.1f' r='%s'/><text class='nm' x='%.1f' y='%.1f' text-anchor='%s'>%s</text>"
        "<text class='dd' x='%.1f' y='%.1f' text-anchor='%s'>%s</text></g>"
        % (' side' if side else '', k, ' '.join(dates), x, y, x, y, '4.5' if side else '6',
           x + dx, y + dy, anc, name, x + dx, y + dy + 13, anc, days))
svg = ("<svg class='tripsvg' viewBox='0 0 %d %d' role='img' aria-label='Map of the trip route across Japan'>"
       "<rect class='sea' width='%d' height='%d' rx='12'/><path class='land' d='%s'/>%s%s%s%s</svg>"
       % (W, H, W, H, land, ''.join(segs), via, '', ''.join(dots)))

LEG = [('d1', 'D1 to D3', 'Tokyo'), ('d4', 'D4', 'Hakone'), ('d5', 'D5', 'Takayama'), ('d6', 'D6 to D8', 'Kyoto'),
       ('d9', 'D9 to D10', 'Osaka'), ('d11', 'D11', 'Nara, then Koyasan'), ('d12', 'D12 to D14', 'Hiroshima and Miyajima'),
       ('d14', 'D14 to D15', 'Mihara, fly home')]
legend = ''.join("<li><a href='#%s'><b>%s</b> %s</a></li>" % a for a in LEG)
CSS = """
#tripmap .mapwrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:6px 0 10px;border-radius:12px}
#tripmap .tripsvg{width:100%;min-width:680px;height:auto;display:block}
#tripmap .sea{fill:#e3edf5}
#tripmap .land{fill:var(--card);stroke:#c9d6e2;stroke-width:1}
@media (prefers-color-scheme:dark){#tripmap .sea{fill:#16202b}#tripmap .land{fill:#26292e;stroke:#33404d}}
#tripmap .rt{stroke:var(--accent);stroke-width:2.6;stroke-linecap:round;fill:none}
#tripmap .rt.back{stroke-dasharray:1 6;stroke-width:2.2}
#tripmap .rt.side{stroke:var(--accent2);stroke-dasharray:5 4;stroke-width:2}
#tripmap .via{fill:var(--card);stroke:var(--muted);stroke-width:1.5}
#tripmap .fly circle{fill:var(--accent2)}
#tripmap .vl{font-size:10.5px;fill:var(--muted)}
#tripmap .dot{fill:var(--accent);stroke:var(--card);stroke-width:2}
#tripmap .stop.side .dot{fill:var(--accent2)}
#tripmap .halo{fill:var(--accent);opacity:0}
#tripmap .nm{font-size:13.5px;font-weight:700;fill:var(--ink)}
#tripmap .dd{font-size:11px;fill:var(--muted)}
#tripmap .stop.here .halo{opacity:.25;animation:tmpulse 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}
#tripmap .stop.here .nm{fill:var(--accent)}
@keyframes tmpulse{0%{transform:scale(.6);opacity:.45}100%{transform:scale(1.9);opacity:0}}
#tripmap .here-note{margin:0 0 4px;font-weight:600;color:var(--accent)}
#tripmap .legend{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}
#tripmap .legend a{display:block;padding:6px 10px;border:1px solid var(--line);border-radius:10px;text-decoration:none;color:var(--ink);font-size:.92em}
#tripmap .legend b{color:var(--accent)}
#tripmap .key{font-size:.85em;color:var(--muted);margin:8px 0 0}
"""
JS = """<script id='tripmapjs'>(function(){try{
var d=new Date(Date.now()+9*3600e3).toISOString().slice(0,10);
var g=document.querySelectorAll('#tripmap .stop'),hit=null;
g.forEach(function(e){if((e.getAttribute('data-dates')||'').split(' ').indexOf(d)>=0)hit=e;});
var n=document.getElementById('tmhere');
if(hit){hit.classList.add('here');n.textContent='You are here today: '+hit.querySelector('.nm').textContent;var w=document.getElementById('tmwrap'),c=hit.querySelector('.dot'),sv=w.querySelector('svg');if(w.scrollWidth>w.clientWidth){var x=c.cx.baseVal.value*sv.clientWidth/760;w.scrollLeft=Math.max(0,x-w.clientWidth/2);}}
else{n.textContent=d<'2026-11-15'?'Trip starts 15 Nov':'Trip complete';}
}catch(e){}})();</script>"""
card = ("<section id='tripmap' class='card'><h2>Trip map</h2><p class='here-note' id='tmhere'></p><div class='mapwrap' id='tmwrap'>%s</div>"
        "<ul class='legend'>%s</ul><p class='key'>Red line: the route. Dotted: the same track again. Blue dashed: day trips. "
        "Swipe the map sideways on a phone. Tap a day to jump to it.</p></section>%s" % (svg, legend, JS))

s = open(src, encoding='utf-8').read()
s = re.sub(r"<section id='tripmap'.*?</section><script id='tripmapjs'>.*?</script>", '', s, flags=re.S)
if '#tripmap .tripsvg' not in s:
    s = s.replace('</style>', CSS + '</style>', 1)
i = s.index("<section id='overview'"); j = s.index('</section>', i) + len('</section>')
s = s[:j] + '\n' + card + s[j:]
if "href='#tripmap'" not in s:
    s = s.replace("<a href='#overview' class='chip'>Trip</a>", "<a href='#overview' class='chip'>Trip</a><a href='#tripmap' class='chip'>Map</a>", 1)
open(dst, 'w', encoding='utf-8').write(s)
print('map', W, H, len(land))
