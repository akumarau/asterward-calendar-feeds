"""Small helpers for editing the itinerary HTML."""
import re, html
from urllib.parse import quote

def links(q, url=None):
    e = html.escape(quote(q, safe=''), quote=True)
    if url:
        u = html.escape(url, quote=True)
        return ("<div class='links'><a class='btn' href='%s' target='_blank' rel='noopener'>Map</a>"
                "<a class='btn' href='https://www.google.com/maps/dir/?api=1&amp;travelmode=transit&amp;destination=%s' target='_blank' rel='noopener'>Directions</a></div>") % (u, e)
    return ("<div class='links'><a class='btn' href='https://www.google.com/maps/search/?api=1&amp;query=%s' target='_blank' rel='noopener'>Map</a>"
            "<a class='btn' href='https://www.google.com/maps/dir/?api=1&amp;travelmode=transit&amp;destination=%s' target='_blank' rel='noopener'>Directions</a></div>") % (e, e)

def a(label, url):
    return "<a href='%s' target='_blank' rel='noopener'>%s</a>" % (html.escape(url, quote=True), html.escape(label))

def picks(summary, items):
    """items: list of (label, url_or_None, note)"""
    lis = []
    for label, url, note in items:
        head = a(label, url) if url else html.escape(label)
        lis.append('<li>%s%s</li>' % (head, (': ' + html.escape(note)) if note else ''))
    return "<details><summary>%s</summary><ul class='steps'>%s</ul></details>" % (html.escape(summary), ''.join(lis))

def ev(kind, t1, t2, title, loc, paras=(), opt=False, url=None, extra=''):
    tag = "<span class='tag'>Optional</span>" if opt else ''
    return ("<li class='ev %s'><div class='t'>%s<small>to %s</small></div><div class='b'><h4>%s%s</h4><p class='loc'>%s</p>%s%s%s</div></li>"
            % (kind, t1, t2, title, tag, html.escape(loc), ''.join('<p>%s</p>' % p for p in paras), extra, links(loc, url)))

def day(s, d):
    m = re.search(r"<section id='%s' class='card day'.*?</section>" % d, s, re.S)
    assert m, d
    return m

def set_timeline(s, d, events_html):
    m = day(s, d); sec = m.group(0)
    sec = re.sub(r"<ol class='timeline'>.*?</ol>", lambda _: "<ol class='timeline'>" + events_html + "</ol>", sec, count=1, flags=re.S)
    return s[:m.start()] + sec + s[m.end():]

def set_in_day(s, d, pattern, repl, count=1):
    m = day(s, d); sec = m.group(0)
    new, n = re.subn(pattern, lambda _: repl, sec, count=count, flags=re.S)
    assert n, (d, pattern[:60])
    return s[:m.start()] + new + s[m.end():]

def set_notes(s, d, items):
    m = day(s, d); sec = m.group(0)
    ul = "<ul class='notes'>%s</ul>" % ''.join('<li>%s</li>' % i for i in items)
    if "<ul class='notes'>" in sec:
        sec = re.sub(r"<ul class='notes'>.*?</ul>", lambda _: ul, sec, count=1, flags=re.S)
    else:
        sec = sec.replace('</dl>', '</dl>\n  ' + ul, 1)
    return s[:m.start()] + sec + s[m.end():]

def set_facts(s, d, facts):
    """facts: list of (dt, dd); keeps the Lenses row if present."""
    m = day(s, d); sec = m.group(0)
    lens = re.search(r"<div><dt>Lenses</dt><dd>[^<]*</dd></div>", sec)
    body = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % f for f in facts) + (lens.group(0) if lens else '')
    sec = re.sub(r"<dl class='facts'>.*?</dl>", lambda _: "<dl class='facts'>%s</dl>" % body, sec, count=1, flags=re.S)
    return s[:m.start()] + sec + s[m.end():]

def set_photo(s, d, head_rows, light, shots, label='Camera bag today · moving day'):
    m = day(s, d); sec = m.group(0)
    rows = ''.join('<p><b>%s:</b> %s</p>' % r for r in head_rows)
    items = ''.join("<li><div class='st'><b>%s</b> %s</div><p><span class='k'>Lens</span> %s</p><p><span class='k'>Settings</span> %s</p><p class='muted'>%s</p></li>"
                    % (t, html.escape(ti), html.escape(le), se, html.escape(no)) for t, ti, le, se, no in shots)
    block = ("<div class='photo'><div class='hk'>%s</div>%s<p class='muted'>%s</p>"
             "<div class='hk' style='margin-top:8px'>Shots</div><ul class='shots'>%s</ul></div>") % (label, rows, light, items)
    sec = re.sub(r"<div class='photo'>.*?</ul></div>", lambda _: block, sec, count=1, flags=re.S)
    return s[:m.start()] + sec + s[m.end():]

SET = {
 'S': "f/8 · 1/500 · ISO 125 in sun, ISO 1000 in shade",
 'P': "f/2.8 · 1/250 · ISO 400 in shade, ISO 3200 indoors",
 'L': "f/8 to f/11 · 1/250 · ISO 100 to 400",
 'N': "f/2.8 · 1/125 · ISO 6400 for people. Still scenes: 1/4 s · ISO 1600, hold steady",
 'A': "f/2.8 · 1/2000 · ISO 1600 outdoors, ISO 12800 indoors · Pre-Capture on",
 'Q': "Silent shutter on",
}
