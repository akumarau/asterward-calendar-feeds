"""Make the itinerary follow the calendar: fold past days, open on today, mark Now and Next.
Usage: dayflow.py <html_in> <html_out>"""
import re, sys
src, dst = sys.argv[1:3]
s = open(src, encoding='utf-8').read()

CSS = """
/*dayflow*/
.chip.past{opacity:.45}
section.day.past{opacity:.8}
section.day.past .dn{background:var(--muted)}
section.day.past:not(.open)>*:not(header):not(.pastbar){display:none}
section.day.past:not(.open) header{margin-bottom:6px}
.pastbar{margin:0 0 4px}
.pastbar button{font:inherit;font-size:.88em;padding:6px 12px;border:1px solid var(--line);border-radius:999px;background:var(--soft);color:var(--ink);cursor:pointer}
.daybadge{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;font-size:.72em;font-weight:700;vertical-align:middle;letter-spacing:.02em}
.daybadge.today{background:var(--accent);color:#fff}
.daybadge.tomorrow{background:var(--soft);color:var(--ink);border:1px solid var(--line)}
.daybadge.done{background:var(--soft);color:var(--muted)}
.ev.done{opacity:.45}
.ev.live{background:var(--warn);border-radius:12px;box-shadow:0 0 0 2px var(--accent) inset}
.ev .evflag{display:inline-block;margin-right:6px;padding:1px 7px;border-radius:999px;font-size:.72em;font-weight:700;vertical-align:middle}
.ev.live .evflag{background:var(--accent);color:#fff}
.ev.next .evflag{background:var(--accent2);color:#fff}
#nownext{margin:10px 0 0;padding:10px 12px;border-radius:12px;background:var(--warn);border:1px solid var(--warnline);font-size:.95em;line-height:1.45}
#nownext b{color:var(--accent)}
"""

JS = r"""<script id='dayflow'>(function(){try{
function tk(){var f=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).formatToParts(new Date()),o={};f.forEach(function(p){o[p.type]=p.value});return {d:o.year+'-'+o.month+'-'+o.day,m:(+o.hour%24)*60+(+o.minute)}}
function mins(t){var a=t.split(':');return (+a[0])*60+(+a[1])}
function addDays(d,n){var x=new Date(d+'T12:00:00Z');x.setUTCDate(x.getUTCDate()+n);return x.toISOString().slice(0,10)}
var now=tk(),T=now.d,TM=addDays(T,1);
var days=[].slice.call(document.querySelectorAll('section.day[data-date]'));
function badge(sec,cls,txt){var h=sec.querySelector('header h2');if(!h||h.querySelector('.daybadge'))return;var b=document.createElement('span');b.className='daybadge '+cls;b.textContent=txt;h.appendChild(b)}
days.forEach(function(sec){var d=sec.getAttribute('data-date'),chip=document.querySelector('.chip[data-date="'+d+'"]');
 if(d<T){sec.classList.add('past');if(chip)chip.classList.add('past');badge(sec,'done','Done');
  if(!sec.querySelector('.pastbar')){var p=document.createElement('p');p.className='pastbar';var b=document.createElement('button');b.type='button';b.textContent='Show details';
   b.addEventListener('click',function(){sec.classList.toggle('open');b.textContent=sec.classList.contains('open')?'Hide details':'Show details'});p.appendChild(b);var h=sec.querySelector('header');h.parentNode.insertBefore(p,h.nextSibling)}}
 else if(d===T){badge(sec,'today','Today')}
 else if(d===TM){badge(sec,'tomorrow','Tomorrow')}});
function openFor(id){var el=document.getElementById(id);if(el&&el.classList.contains('past')){el.classList.add('open');var b=el.querySelector('.pastbar button');if(b)b.textContent='Hide details'}}
document.addEventListener('click',function(e){var a=e.target.closest?e.target.closest("a[href^='#']"):null;if(a)openFor(a.getAttribute('href').slice(1))},true);
if(location.hash.length>1)openFor(location.hash.slice(1));
var today=document.querySelector('section.day[data-date="'+T+'"]');
function tick(){var n=tk();if(n.d!==T){location.reload();return}
 if(!today)return;var evs=[].slice.call(today.querySelectorAll('ol.timeline>li.ev')),live=null,next=null;
 evs.forEach(function(li){li.classList.remove('done','live','next');var f=li.querySelector('.evflag');if(f)f.remove();
  var t=li.querySelector('.t');if(!t)return;var m=t.textContent.match(/(\d\d):(\d\d)\D+(\d\d):(\d\d)/);if(!m)return;
  var a=mins(m[1]+':'+m[2]),z=mins(m[3]+':'+m[4]);if(z<=a)z=a+15;
  if(n.m>=z)li.classList.add('done');else if(n.m>=a){if(!live)live=li}else if(!next)next=li});
 function flag(li,c,txt){if(!li)return;li.classList.add(c);var h=li.querySelector('h4'),f=document.createElement('span');f.className='evflag';f.textContent=txt;h.insertBefore(f,h.firstChild)}
 flag(live,'live','Now');flag(next,'next','Next');
 var box=document.getElementById('nownext');if(!box){box=document.createElement('p');box.id='nownext';var hd=today.querySelector('header');hd.parentNode.insertBefore(box,hd.nextSibling)}
 function nm(li){var h=li.querySelector('h4').cloneNode(true);[].slice.call(h.querySelectorAll('.evflag,.tag')).forEach(function(x){x.remove()});return h.textContent.trim()}
 function tm(li,i){return li.querySelector('.t').textContent.match(/\d\d:\d\d/g)[i]}
 var html='';if(live)html+='<b>Now:</b> '+nm(live)+' until '+tm(live,1)+'.';
 if(next)html+=(html?'<br>':'')+'<b>Next:</b> '+tm(next,0)+' '+nm(next)+'.';
 if(!live&&!next)html='<b>Done for today.</b> Tomorrow\u2019s plan is below.';
 box.innerHTML=html}
tick();setInterval(tick,60000);
if(today&&location.hash.length<2){setTimeout(function(){var nav=document.querySelector('nav'),off=(nav?nav.offsetHeight:0)+8;window.scrollTo(0,today.getBoundingClientRect().top+window.pageYOffset-off)},120)}
}catch(e){}})();</script>"""

s = re.sub(r"\n/\*dayflow\*/.*?#nownext b\{[^}]*\}\n", '\n', s, flags=re.S)
s = s.replace('</style>', CSS + '</style>', 1)
s = re.sub(r"<script id='dayflow'>.*?</script>", '', s, flags=re.S)
s = s.replace('</body>', JS + '</body>', 1)
open(dst, 'w', encoding='utf-8').write(s)
print('dayflow ok')
