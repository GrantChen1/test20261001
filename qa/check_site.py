"""Chrome CDP checks. Requires websocket-client; serve project on port 8765.
Launch headless Chrome with remote debugging port 9223 before running.
"""
import base64
import json
import time
from pathlib import Path
from urllib.request import urlopen
import websocket

OUT=Path(__file__).resolve().parent
endpoint=next(t for t in json.load(urlopen('http://localhost:9223/json')) if t['type']=='page')['webSocketDebuggerUrl']
ws=websocket.create_connection(endpoint,origin='http://localhost:9223',timeout=20)
seq=0
requests=[]
errors=[]
def call(method,params=None):
 global seq
 seq+=1
 ws.send(json.dumps({'id':seq,'method':method,'params':params or {}}))
 while True:
  r=json.loads(ws.recv())
  if r.get('method')=='Network.requestWillBeSent': requests.append(r['params']['request'])
  if r.get('method')=='Runtime.exceptionThrown': errors.append(r['params'])
  if r.get('id')==seq:
   assert 'error' not in r,r
   return r.get('result',{})
def js(expression):
 r=call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
 assert 'exceptionDetails' not in r,r
 return r.get('result',{}).get('value')
def pause(): js('new Promise(resolve=>setTimeout(resolve,450))')
def click(selector):
 r=js(f'(() => {{ const e=document.querySelector({json.dumps(selector)}); e.scrollIntoView({{block:"center",behavior:"instant"}}); const r=e.getBoundingClientRect(); return {{x:r.x+r.width/2,y:r.y+r.height/2}}; }})()')
 call('Input.dispatchMouseEvent',{'type':'mousePressed','button':'left','clickCount':1,**r})
 call('Input.dispatchMouseEvent',{'type':'mouseReleased','button':'left','clickCount':1,**r})
 pause()
def key(name,code,vk):
 for kind in ('keyDown','keyUp'):
  params={'type':kind,'key':name,'code':code,'windowsVirtualKeyCode':vk}
  if name=='Enter' and kind=='keyDown': params['text']='\r'
  call('Input.dispatchKeyEvent',params)
 pause()
def fill(value):
 js(f'document.querySelector("#name").value={json.dumps(value)}; document.querySelector("#name").dispatchEvent(new Event("input",{{bubbles:true}}))')
def navigate(url):
 call('Page.navigate',{'url':url})
 for _ in range(100):
  time.sleep(.1)
  if js('document.readyState')=='complete': break
 else: raise AssertionError('load timeout')
call('Page.enable'); call('Runtime.enable'); call('Network.enable')
results={}
for width in (375,768,1440):
 call('Emulation.setDeviceMetricsOverride',{'width':width,'height':900,'deviceScaleFactor':1,'mobile':False})
 navigate('http://127.0.0.1:8765/')
 assert js('typeof bootstrap')=='object'
 m=js('''(() => ({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,
 cards:[...document.querySelectorAll('#models .card')].map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}}),
 badAnchors:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.querySelector(a.getAttribute('href'))).length,
 headings:[...document.querySelectorAll('h1,h2,h3')].map(e=>({tag:e.tagName,text:e.textContent}))}))()''')
 assert m['documentWidth']<=width,m
 assert m['badAnchors']==0
 expected={375:1,768:2,1440:3}[width]
 assert sum(abs(c['y']-m['cards'][0]['y'])<1 for c in m['cards'])==expected
 m['columns']=expected
 key('Tab','Tab',9)
 assert js('document.activeElement.textContent.trim()')=='跳到主要內容'
 key('Enter','Enter',13)
 assert js('document.activeElement.id')=='main'
 m['keyboardSkip']=True
 for target in ('research','models','approach','contact'):
  if width<992:
   click('.navbar-toggler')
   assert js('document.querySelector(".navbar-toggler").getAttribute("aria-expanded")')=='true', js('({scrollY,menu:document.querySelector("#menu").className,button:document.querySelector(".navbar-toggler").getBoundingClientRect().toJSON()})')
  click(f'#menu a[href="#{target}"]')
  assert js('location.hash')=='#'+target
  if width<992:
   assert js('document.querySelector(".navbar-toggler").getAttribute("aria-expanded")')=='false'
   assert js('document.activeElement.id')==target
 m['navigation']='4 links passed; collapse and focus passed on 375 / 768'
 for i in range(3):
  click(f'#models .col:nth-child({i+1}) a')
  assert js('location.hash')=='#contact'
 click('.hero .btn'); assert js('location.hash')=='#models'
 js('''window.storageWrites=[]; const originalSetItem=Storage.prototype.setItem;
 Storage.prototype.setItem=function(...args){storageWrites.push(args); return originalSetItem.apply(this,args)}''')
 start=len(requests)
 click('#demo-form button')
 assert js('document.querySelector("#name").validity.valueMissing')
 fill('   '); click('#demo-form button')
 assert js('document.querySelector("#name").validity.customError')
 fill('同學 A'); click('#demo-form button')
 assert js('document.querySelector("#interest").validity.valueMissing')
 js('document.querySelector("#interest").selectedIndex=1; document.querySelector("#interest").dispatchEvent(new Event("change",{bubbles:true})); document.querySelector("#name").focus()')
 key('Enter','Enter',13)
 assert '示範完成' in js('document.querySelector("#form-result").textContent')
 assert js('document.querySelector("#name").value + document.querySelector("#interest").value')==''
 assert js('storageWrites.length')==0
 assert js('localStorage.length+sessionStorage.length')==0
 assert js('document.cookie')==''
 assert len(requests)==start,requests[start:]
 m['form']={'empty':'blocked','whitespace':'blocked','missingCategory':'blocked','enterSubmit':'passed','fieldsCleared':True,'requestsDuringForm':0,'storageWrites':0,'cookies':''}
 js('scrollTo(0,0)')
 size=call('Page.getLayoutMetrics')['cssContentSize']
 shot=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True,'clip':{'x':0,'y':0,'width':width,'height':size['height'],'scale':1}})
 OUT.joinpath(f'{width}.png').write_bytes(base64.b64decode(shot['data']))
 results[str(width)]=m
call('Emulation.setScriptExecutionDisabled',{'value':True})
navigate('http://127.0.0.1:8765/')
assert js('document.querySelector("#demo-fields").disabled')
assert js('document.querySelector("noscript").getBoundingClientRect().height')>0
results['noJavaScript']='fieldset disabled; noscript message visible'
call('Emulation.setScriptExecutionDisabled',{'value':False})
call('Emulation.setDeviceMetricsOverride',{'width':375,'height':900,'deviceScaleFactor':1,'mobile':False})
navigate('http://127.0.0.1:8765/')
js('document.querySelector(".navbar-toggler").focus()')
key('Enter','Enter',13)
assert js('document.querySelector(".navbar-toggler").getAttribute("aria-expanded")')=='true'
key('Tab','Tab',9)
assert js('document.activeElement.getAttribute("href")')=='#research'
key('Enter','Enter',13)
assert js('document.activeElement.id')=='research'
js('document.querySelector("#name").focus()')
key('Tab','Tab',9); assert js('document.activeElement.id')=='interest'
key('Tab','Tab',9); assert js('document.activeElement.type')=='submit'
# Match key motion setting to confirm hover transform is removed.
call('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
assert js('getComputedStyle(document.querySelector(".card")).transitionDuration')=='0s'
assert js('getComputedStyle(document.querySelector(".card")).transform')=='none'
results["additionalChecks"] = {"keyboardMobileMenu": "Enter expands; Tab and Enter navigate with focus transfer", "keyboardForm": "Tab reaches select and submit", "reducedMotion": "no card transition or transform"}
results['runtimeErrors']=errors
assert not errors,errors
OUT.joinpath('results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
ws.close()
