"""Targeted checks after Claude round 1; CDP port 9223, HTTP port 8766.
Reuse the CDP helpers only; do not rerun the round-1 form/storage suite.
"""
from pathlib import Path
import re
import hashlib
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parent.parent
exec(ROOT.joinpath('qa/check_site.py').read_text().split('results={}')[0])
OUT=ROOT/'qa/round2'
OUT.mkdir(exist_ok=True)
current=ROOT.joinpath('index.html').read_text()
previous=ROOT.joinpath('qa/round1/index.html').read_text()
form=lambda s: re.search(r'<form\b.*?</form>',s,re.S).group()
script=lambda s: re.findall(r'<script>(.*?)</script>',s,re.S)[0]
assert form(current)==form(previous)
normalize=lambda s: re.sub(r'//[^\n]*','',s).strip()
assert normalize(script(current))==normalize(script(previous))
class Check(HTMLParser):
 def __init__(self):super().__init__();self.stack=[];self.ids=[]
 def handle_starttag(self,t,attrs):
  if t not in {'meta','link','input','br','hr','img'}: self.stack.append(t)
  self.ids += [v for k,v in attrs if k=='id']
 def handle_endtag(self,t):
  assert self.stack[-1]==t,(t,self.stack)
  self.stack.pop()
parser=Check();parser.feed(current)
assert not parser.stack and len(parser.ids)==len(set(parser.ids))
results={'scope':'layout, comparison attributes, link names/targets, static categories, affected focus path; no full form/storage retest',
 'unchangedFormHTML':True,'unchangedExecutableInlineJavaScript':True,'htmlNestingAndUniqueIDs':True,
 'htmlSHA256':hashlib.sha256(current.encode()).hexdigest()}
call('Accessibility.enable');call('DOM.enable')
for width in (375,768,1440):
 call('Emulation.setDeviceMetricsOverride',{'width':width,'height':900,'deviceScaleFactor':1,'mobile':False})
 navigate('http://127.0.0.1:8766/')
 assert js('typeof bootstrap')=='object'
 m=js('''(() => {
 const h=document.querySelector('h1'),node=h.firstChild,lines={};
 for(let i=0;i<node.length;i++) {const r=document.createRange();r.setStart(node,i);r.setEnd(node,i+1);const y=r.getBoundingClientRect().y;lines[y]=(lines[y]||'')+node.textContent[i];}
 return {viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,
 titleLines:Object.values(lines),titleWidth:h.getBoundingClientRect().width,
 cards:[...document.querySelectorAll('#models .card')].map(e=>{
 const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,
 disclaimer:e.querySelector('dl').previousElementSibling.textContent,
 attributes:[...e.querySelectorAll('dt')].map(dt=>({label:dt.textContent,value:dt.nextElementSibling.textContent})),
 linkText:e.querySelector('a').textContent,ariaLabel:e.querySelector('a').getAttribute('aria-label'),
 overflowing:[...e.querySelectorAll('.card-body,dl,dt,dd,a')].filter(n=>n.scrollWidth>n.clientWidth+1).length};}),
 staticCategory:[...document.querySelectorAll('#models p')].find(e=>e.textContent.startsWith('分類索引')).textContent,
 badAnchors:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.querySelector(a.getAttribute('href'))).length};})()''')
 assert m['documentWidth']<=width and m['badAnchors']==0
 assert '靜態文字' in m['staticCategory']
 assert js('document.querySelector(".category-list")===null')
 expected={375:1,768:2,1440:3}[width]
 assert sum(abs(c['y']-m['cards'][0]['y'])<1 for c in m['cards'])==expected
 assert min(map(len,m['titleLines']))>=3,m['titleLines']
 doc=call('DOM.getDocument')['root']['nodeId']
 names=[]
 for i,c in enumerate(m['cards']):
  assert c['disclaimer']=='虛構示意屬性（非真車規格）'
  assert [a['label'] for a in c['attributes']]==['動力','座位','情境']
  assert c['ariaLabel'] is None and c['overflowing']==0
  node=call('DOM.querySelector',{'nodeId':doc,'selector':f'#models .col:nth-child({i+1}) a'})['nodeId']
  ax=call('Accessibility.getPartialAXTree',{'nodeId':node,'fetchRelatives':False})['nodes'][0]
  name=ax['name']['value'];assert name.startswith('了解示範流程')
  assert c['linkText'].split('：')[1] in name
  names.append(name)
  click(f'#models .col:nth-child({i+1}) a')
  assert js('location.hash')=='#contact'
 m['accessibleLinkNames']=names
 m['columns']=expected
 if width==375:
  js('document.querySelector(".navbar-toggler").focus()')
  key('Enter','Enter',13)
  assert js('document.querySelector(".navbar-toggler").getAttribute("aria-expanded")')=='true'
  key('Tab','Tab',9);key('Tab','Tab',9)
  assert js('document.activeElement.getAttribute("href")')=='#models'
  key('Enter','Enter',13)
  assert js('document.activeElement.id')=='models'
  assert js('document.querySelector(".navbar-toggler").getAttribute("aria-expanded")')=='false'
  m['affectedFocusPath']='keyboard menu -> models; focus transfer and collapse passed'
 js('document.activeElement.blur();scrollTo({top:0,behavior:"instant"})')
 size=call('Page.getLayoutMetrics')['cssContentSize']
 shot=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True,'clip':{'x':0,'y':0,'width':width,'height':size['height'],'scale':1}})
 OUT.joinpath(f'{width}.png').write_bytes(base64.b64decode(shot['data']))
 results[str(width)]=m
assert not errors,errors
results['runtimeErrors']=errors
OUT.joinpath('results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
ws.close()
