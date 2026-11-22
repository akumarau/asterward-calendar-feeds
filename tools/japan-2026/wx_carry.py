"""Copy the latest weather rows from the live iCloud page into the master before a rebuild.
Usage: wx_carry.py <live.html> <master_in> <master_out>"""
import re, sys
live, src, dst = sys.argv[1:4]
L = open(live, encoding='utf-8').read()
s = open(src, encoding='utf-8').read()
rows = {}
for m in re.finditer(r"<section id='(d\d+)' class='card day'.*?</section>", L, re.S):
    w = re.search(r"<div class='wxrow'>.*?</div>", m.group(0), re.S)
    if w: rows[m.group(1)] = w.group(0)
n = 0
for m in list(re.finditer(r"<section id='(d\d+)' class='card day'.*?</section>", s, re.S)):
    d = m.group(1)
    if d not in rows: continue
    sec = m.group(0)
    sec2 = re.sub(r"<div class='wxrow'>.*?</div>", '', sec, flags=re.S).replace("<dl class='facts'>", "<dl class='facts'>" + rows[d], 1)
    if sec2 != sec:
        s = s.replace(sec, sec2, 1); n += 1
open(dst, 'w', encoding='utf-8').write(s)
print('weather rows carried', n)
