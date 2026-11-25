"""Fold the itinerary around today, in the HTML itself, so it works without scripts
(iPhone Files preview runs no JavaScript). Safe to run every day on its own output.

Usage: foldbake.py <html_in> <html_out> <YYYY-MM-DD>   (date = today in Asia/Tokyo)

Writes:
- Past days inside a closed <details id='pastdays'> group.
- Today (the focus day) open, between the two groups.
- Future days inside an open <details id='nextdays'> group, each day closed.
- A one line preview on tomorrow, the "Today in Japan" banner, chip states, a Jump to today link.
- The foldnav CSS and script, which redo all of this live when scripts do run.
Section tags, <h2> and timelines are left untouched, so html_to_cal.py and wx.py read the page as before."""
import html, re, sys
from datetime import date, timedelta

src, dst, T = sys.argv[1:4]
s = open(src, encoding='utf-8').read()
MON = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
def dm(d): return '%d %s' % (int(d[8:10]), MON[int(d[5:7]) - 1])
TM = (date.fromisoformat(T) + timedelta(days=1)).isoformat()

# 1. Drop the older per day fold from dayflow (replaced by foldnav)
s = s.replace("section.day.past:not(.open)>*:not(header):not(.pastbar){display:none}\n", "")
s = s.replace("section.day.past:not(.open) header{margin-bottom:6px}\n", "")
s = re.sub(r"badge\(sec,'done','Done'\);\n  if\(!sec\.querySelector\('\.pastbar'\)\)\{.*?h\.parentNode\.insertBefore\(p,h\.nextSibling\)\}\}",
           "badge(sec,'done','Done')}", s, flags=re.S)
for line in ["function openFor(id){var el=document.getElementById(id);if(el&&el.classList.contains('past')){el.classList.add('open');var b=el.querySelector('.pastbar button');if(b)b.textContent='Hide details'}}\n",
             "document.addEventListener('click',function(e){var a=e.target.closest?e.target.closest(\"a[href^='#']\"):null;if(a)openFor(a.getAttribute('href').slice(1))},true);\n",
             "if(location.hash.length>1)openFor(location.hash.slice(1));\n"]:
    s = s.replace(line, "")

# 2. CSS and script (replaced each run)
CSS = r"""/*foldnav*/
details.daygroup{margin:14px 0}
details.daygroup>summary{list-style:none;display:flex;align-items:center;gap:10px;min-height:52px;padding:10px 16px;border:1px solid var(--line);border-radius:14px;background:var(--card);color:var(--ink);font-size:15.5px;font-weight:700}
details.daygroup>summary::-webkit-details-marker{display:none}
details.daygroup>summary::before{content:'\203A';font-size:22px;line-height:1;color:var(--muted);transition:transform .15s}
details.daygroup[open]>summary::before{transform:rotate(90deg)}
details.daygroup>summary small{display:inline;margin-left:auto;font-weight:400;font-size:13px}
#pastdays section.day{opacity:.85}
#pastdays .dn{background:var(--muted)}
details.dayfold{margin:0}
details.dayfold>summary{list-style:none;display:inline-flex;align-items:center;min-height:36px;padding:0 14px;margin:0 0 4px;border:1px solid var(--line);border-radius:999px;background:var(--soft);color:var(--ink);font-size:14px;font-weight:600}
details.dayfold>summary::-webkit-details-marker{display:none}
details.dayfold>summary .hd{display:none}
details.dayfold[open]>summary .sh{display:none}
details.dayfold[open]>summary .hd{display:inline}
details.dayfold[open]>summary{margin-bottom:10px}
details.dayfold.focus>summary{display:none}
section.day:has(>details.dayfold.focus){outline:3px solid var(--accent);outline-offset:2px}
section.day:has(>details.dayfold:not(.focus)) header{cursor:pointer;margin-bottom:8px}
.preview{margin:0 0 8px;padding:8px 10px;border-radius:10px;background:var(--soft);font-size:14px;line-height:1.4}
.preview b{color:var(--accent)}
section.day:has(>details.dayfold[open]:not(.focus))>.preview{display:none}
#jumptoday{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:6;display:none;align-items:center;min-height:44px;padding:0 16px;border-radius:999px;background:var(--accent);color:#fff;font-weight:700;font-size:14.5px;text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.25)}
#jumptoday.show{display:inline-flex}
@media print{#jumptoday{display:none!important}details.dayfold>summary{display:none}}
/*/foldnav*/
"""
s = re.sub(r"/\*foldnav\*/.*?/\*/foldnav\*/\n", "", s, flags=re.S)
s = s.replace("</style>", CSS + "</style>", 1)

JS = r"""<script id='foldnav'>(function(){try{
var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function dm(d){return (+d.slice(8,10))+' '+MON[+d.slice(5,7)-1]}
function addDays(d,n){var x=new Date(d+'T12:00:00Z');x.setUTCDate(x.getUTCDate()+n);return x.toISOString().slice(0,10)}
var T=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date()),TM=addDays(T,1);
var days=[].slice.call(document.querySelectorAll('section.day[data-date]'));if(!days.length)return;
var first=days[0].getAttribute('data-date'),last=days[days.length-1].getAttribute('data-date'),F=T<first?first:(T>last?'':T);
function fd(sec){for(var x=sec.firstElementChild;x;x=x.nextElementSibling)if(x.tagName==='DETAILS'&&x.classList.contains('dayfold'))return x;return null}
var main=days[0].parentNode;while(main&&main.tagName!=='MAIN')main=main.parentNode;if(!main)return;
function top(n){while(n.parentNode!==main)n=n.parentNode;return n}
function grp(id){var g=document.getElementById(id);if(!g){g=document.createElement('details');g.id=id;g.className='daygroup';g.appendChild(document.createElement('summary'))}return g}
var pg=grp('pastdays'),ng=grp('nextdays'),mk=document.createComment('days');main.insertBefore(mk,top(days[0]));main.insertBefore(pg,mk);
[].forEach.call(document.querySelectorAll('section.day>.preview'),function(x){x.parentNode.removeChild(x)});
var P=[],N=[];
days.forEach(function(sec){var d=sec.getAttribute('data-date'),f=fd(sec);
 if(f){f.classList.toggle('focus',d===F);f.open=d===F}
 if(d===F)main.insertBefore(sec,mk);
 else if(d<T){P.push(d);pg.appendChild(sec)}
 else{N.push(d);if(ng.parentNode!==main)main.insertBefore(ng,mk);ng.appendChild(sec)}
 if(d===TM&&d!==F&&f){var n=sec.querySelector('ul.notes>li'),w=sec.querySelector('dd.wx'),bits=[];
  if(n)bits.push(n.textContent.trim());if(w&&w.getAttribute('data-wxshort'))bits.push(w.getAttribute('data-wxshort'));
  if(bits.length){var p=document.createElement('p');p.className='preview';p.innerHTML='<b>Tomorrow:</b> ';p.appendChild(document.createTextNode(bits.join(' · ')));sec.insertBefore(p,f)}}});
main.insertBefore(ng,mk);main.removeChild(mk);
function sum(g,L,title,open){if(!L.length){g.hidden=true;g.open=false;return}g.hidden=false;g.open=open;
 g.querySelector('summary').innerHTML=title+' ('+L.length+')<small>'+(L.length>1?dm(L[0])+' to '+dm(L[L.length-1]):dm(L[0]))+'</small>'}
sum(pg,P,'Past days',!F);sum(ng,N,'Coming up',true);
[].forEach.call(document.querySelectorAll('.chip[data-date]'),function(c){var d=c.getAttribute('data-date');c.classList.toggle('past',d<T);c.classList.toggle('now',d===T)});
var tb=document.getElementById('todaybox');if(tb&&!document.querySelector('section.day[data-date="'+T+'"]')){tb.hidden=true;tb.innerHTML=''}
days.forEach(function(sec){var h=sec.querySelector('header');if(h)h.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('a,button,summary'))return;var f=fd(sec);if(f&&!f.classList.contains('focus'))f.open=!f.open})});
function openFor(id){var el=id&&document.getElementById(id);if(!el)return;if(el.matches&&el.matches('section.day')){var f=fd(el);if(f)f.open=true}
 for(var n=el;n;n=n.parentNode)if(n.tagName==='DETAILS')n.open=true}
document.addEventListener('click',function(e){var a=e.target.closest?e.target.closest("a[href^='#']"):null;if(a)openFor(a.getAttribute('href').slice(1))},true);
if(location.hash.length>1)openFor(location.hash.slice(1));
window.addEventListener('beforeprint',function(){[].forEach.call(document.querySelectorAll('details.daygroup,details.dayfold'),function(g){g.open=true})});
var fs=F?document.querySelector('section.day[data-date="'+F+'"]'):null,j=document.getElementById('jumptoday');
if(!fs){if(j)j.parentNode.removeChild(j)}else{if(!j){j=document.createElement('a');j.id='jumptoday';document.body.appendChild(j)}
 j.href='#'+fs.id;j.textContent=F===T?'Jump to today':'Jump to Day 0';j.classList.add('show');
 if('IntersectionObserver' in window)new IntersectionObserver(function(es){es.forEach(function(e){j.classList.toggle('show',!e.isIntersecting)})}).observe(fs.querySelector('header')||fs)}
}catch(e){}})();</script>
"""
s = re.sub(r"<script id='foldnav'>.*?</script>\n", "", s, flags=re.S)
if "<script id='dayflow'>" in s:
    s = s.replace("<script id='dayflow'>", JS + "<script id='dayflow'>", 1)
else:
    s = s.replace("</body>", JS + "</body>", 1)

# 3. Remove the previous bake
s = re.sub(r"<details class='daygroup'[^>]*><summary>.*?</summary><!--/fg-->\n", "", s, flags=re.S)
s = s.replace("\n</details><!--/fgend-->", "")
s = re.sub(r"<!--fold-->.*?<!--/foldhead-->", "", s, flags=re.S)
s = s.replace("<!--fold-end--></details>\n", "")
s = re.sub(r"\n<a id='jumptoday'[^>]*>[^<]*</a>", "", s)
s = re.sub(r"<p id='todaybox'[^>]*>.*?</p>", "<p id='todaybox' class='today' hidden></p>", s, count=1, flags=re.S)
s = re.sub(r"(<a href='#d\d+' )class='chip[^']*'( data-date=)", r"\1class='chip'\2", s)

# 4. Bake for T
SEC = re.compile(r"<section id='(d\d+)' class='card day' data-date='([\d-]+)'>.*?</section>", re.S)
secs = list(SEC.finditer(s))
assert secs, 'no day sections'
dates = [m.group(2) for m in secs]
first, last = dates[0], dates[-1]
F = first if T < first else ('' if T > last else T)

def text(x): return html.unescape(re.sub(r'<[^>]+>', '', x)).strip()

def bake_day(m):
    sec, d = m.group(0), m.group(2)
    focus = d == F
    pre = ''
    if d == TM and not focus:
        bits = []
        n = re.search(r"<ul class='notes'><li>(.*?)</li>", sec, re.S)
        if n: bits.append(text(n.group(1)))
        w = re.search(r"data-wxshort='([^']+)'", sec)
        if w: bits.append(html.unescape(w.group(1)))
        if bits: pre = "<p class='preview'><b>Tomorrow:</b> %s</p>" % html.escape(' · '.join(bits), quote=False)
    head = ("<!--fold-->%s<details class='dayfold%s'%s><summary><span class='sh'>Show details</span>"
            "<span class='hd'>Hide details</span></summary><!--/foldhead-->") % (pre, ' focus' if focus else '', ' open' if focus else '')
    i = sec.index('</header>') + len('</header>')
    j = sec.rindex('</section>')
    return sec[:i] + head + sec[i:j] + "<!--fold-end--></details>\n" + sec[j:]

def group(gid, title, ds, is_open):
    rng = dm(ds[0]) if len(ds) == 1 else '%s to %s' % (dm(ds[0]), dm(ds[-1]))
    return "<details class='daygroup' id='%s'%s><summary>%s (%d)<small>%s</small></summary><!--/fg-->\n" % (
        gid, ' open' if is_open else '', title, len(ds), rng)

past = [m for m in secs if m.group(2) < T and m.group(2) != F]
fut = [m for m in secs if m.group(2) > T and m.group(2) != F]
out, pos = [], 0
for m in secs:
    out.append(s[pos:m.start()])
    d = m.group(2)
    if past and m is past[0]: out.append(group('pastdays', 'Past days', [x.group(2) for x in past], not F))
    if fut and m is fut[0]: out.append(group('nextdays', 'Coming up', [x.group(2) for x in fut], True))
    out.append(bake_day(m))
    if (past and m is past[-1]) or (fut and m is fut[-1]): out.append("\n</details><!--/fgend-->")
    pos = m.end()
out.append(s[pos:])
s = ''.join(out)

# Chips, banner, jump link
s = re.sub(r"<a href='#d\d+' class='chip' data-date='([\d-]+)'",
           lambda m: m.group(0).replace("class='chip'", "class='chip%s'" % (' past' if m.group(1) < T else (' now' if m.group(1) == T else ''))), s)
if F:
    fm = next(m for m in SEC.finditer(s) if m.group(2) == F)
    did = fm.group(1)
    if F == T:
        eb = re.search(r"<p class='eyebrow'>(.*?)</p>", fm.group(0), re.S)
        when = text(eb.group(1)).split(' · ')[0] if eb else dm(T)
        s = s.replace("<p id='todaybox' class='today' hidden></p>",
                      "<p id='todaybox' class='today'>Today in Japan is %s. <a href='#%s'>Go to %s ›</a></p>" % (html.escape(when), did, did.upper()), 1)
    s = s.replace("</main>", "</main>\n<a id='jumptoday' class='show' href='#%s'>%s</a>" % (did, 'Jump to today' if F == T else 'Jump to Day 0'), 1)

open(dst, 'w', encoding='utf-8').write(s)
print('foldbake %s: focus %s, past %d, coming up %d' % (T, F or 'none', len(past), len(fut)))
