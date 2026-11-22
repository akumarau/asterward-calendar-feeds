import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
JS = """<script id='navfix'>
(function(){
 function go(id){
  var el = id === 'top' ? null : document.getElementById(id);
  if (id !== 'top' && !el) return false;
  var nav = document.querySelector('nav');
  var off = (nav ? nav.offsetHeight : 0) + 8;
  var y = id === 'top' ? 0 : el.getBoundingClientRect().top + window.pageYOffset - off;
  try { window.scrollTo({top: y, behavior: 'instant'}); } catch (e) { window.scrollTo(0, y); }
  try { history.replaceState(null, '', '#' + id); } catch (e) {}
  return true;
 }
 document.addEventListener('click', function(e){
  var a = e.target.closest ? e.target.closest("a[href^='#']") : null;
  if (!a) return;
  var id = a.getAttribute('href').slice(1);
  if (id && go(id)) e.preventDefault();
 });
 if (location.hash.length > 1) { setTimeout(function(){ go(location.hash.slice(1)); }, 50); }
})();
</script>
"""
if "id='navfix'" not in s:
    assert s.count('</body>') == 1
    s = s.replace('</body>', JS + '</body>')
s = s.replace('html{scroll-behavior:smooth;scroll-padding-top:72px}', 'html{scroll-padding-top:72px}')
open(dst, 'w', encoding='utf-8').write(s)
print('ok')
