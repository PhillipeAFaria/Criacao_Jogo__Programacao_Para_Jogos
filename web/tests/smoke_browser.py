from pathlib import Path
from playwright.sync_api import sync_playwright
import json, threading, http.server, functools, os
root=Path(__file__).resolve().parents[2]
(root/'reports').mkdir(exist_ok=True)
server=http.server.ThreadingHTTPServer(('127.0.0.1',8768),functools.partial(http.server.SimpleHTTPRequestHandler,directory=os.environ.get('FDM_TEST_SITE',str(root/'.web-build/web_game/build/web'))))
threading.Thread(target=server.serve_forever,daemon=True).start()
results={};logs=[]
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 context=browser.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True,device_scale_factor=1)
 page=context.new_page()
 page.add_init_script('''
 window.loadingLabels=[];
 new MutationObserver(()=>{const text=document.getElementById('load-label')?.textContent;
 if(text && !window.loadingLabels.includes(text))window.loadingLabels.push(text);
 }).observe(document,{subtree:true,childList:true,characterData:true});
 ''')
 page.on('console',lambda m:logs.append(m.type+': '+m.text))
 page.on('pageerror',lambda e:logs.append('ERROR: '+str(e)))
 def ready():
  for i in range(90):
   page.wait_for_timeout(1000)
   if i in (3,12,25,45):page.touchscreen.tap(420,190)
   if page.evaluate('window.fdmState?.scene === "title"'):return
  raise AssertionError('Menu did not load')
 def scene(name):page.wait_for_function('(name)=>window.fdmState?.scene===name && !window.fdmBusy',arg=name,timeout=120000)
 def tap(x,y):
  r=page.locator('#canvas').bounding_box();page.touchscreen.tap(r['x']+x*r['width']/1280,r['y']+y*r['height']/720);page.wait_for_timeout(450)
 try:
  page.goto(os.environ.get('FDM_TEST_URL','http://127.0.0.1:8768'+os.environ.get('FDM_TEST_PATH','/')));ready()
  results['cold_menu_download']=page.evaluate('window.fdmNetwork')
  page.screenshot(path=str(root/'reports/mobile-menu.png'))
  tap(180,295);scene('profile');tap(500,240)
  page.locator('#player-name').tap()
  page.keyboard.type('Teste Web Mobilx',delay=60)
  page.keyboard.press('Backspace')
  page.keyboard.type('e',delay=60)
  assert page.locator('#player-name').input_value()=='Teste Web Mobile'
  results['native_keyboard_typing_and_backspace']=True
  page.locator('button[value="save"]').tap();scene('difficulty')
  tap(200,520);scene('campaign');tap(200,320);scene('battle')
  page.get_by_role("button",name="Mais controles").tap()
  page.locator('[data-action="save"]').tap();page.wait_for_timeout(1500)
  saved=page.evaluate('localStorage.getItem("fabrica-dos-mortos:web:save:v1")')
  assert saved and 'campanha.settings.json' in saved
  page.locator('#controls-close').tap()
  page.locator('#full').tap();page.wait_for_timeout(500)
  assert page.evaluate('Boolean(document.fullscreenElement)')
  results['native_fullscreen']=True
  results['battle_canvas']=page.locator('#canvas').bounding_box()
  assert results['battle_canvas']['height']>=389
  results['touch_campaign_and_profile']=True
  page.screenshot(path=str(root/'reports/mobile-battle.png'))
  results['cold_city_download']=page.evaluate('window.fdmNetwork')
  labels=page.evaluate('window.loadingLabels')
  assert 'Preparando o jogo…' in labels, labels
  assert any('animações' in text for text in labels), labels
  assert not any('Ã' in text or 'â€' in text or '\ufffd' in text for text in labels), labels
  results['loading_unicode_labels']=labels
  page.reload();ready()
  assert page.evaluate('window.fdmState.player')=='Teste Web Mobile'
  tap(180,267);scene('battle');results['reload_and_continue']=True
  results['warm_city_download']=page.evaluate('window.fdmNetwork')
  page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>true});document.dispatchEvent(new Event("visibilitychange"))')
  page.wait_for_timeout(800)
  assert page.evaluate('window.fdmState.combat.paused')
  page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>false});document.dispatchEvent(new Event("visibilitychange"))')
  page.wait_for_timeout(800)
  assert page.evaluate('window.fdmState.combat.paused')
  results['simulated_visibility_pause_and_no_auto_resume']=True
  page.get_by_role('button',name='Mais controles').tap()
  sound=page.evaluate('window.fdmState.sound')
  page.locator('[data-action="sound"]').tap();page.wait_for_timeout(500)
  assert page.evaluate('window.fdmState.sound')!=sound
  page.locator('#controls-close').tap()
  results['audio_initialized_and_toggle']=page.evaluate('window.fdmState.audio')
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(800)
  assert page.locator('#rotate').is_visible();results['portrait_notice']=True
  page.screenshot(path=str(root/'reports/mobile-portrait.png'))
  page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(800)
  results['error']=page.evaluate('window.fdmState.error')
  assert not results['error']
 except Exception as e:
  results['failure']=str(e);page.screenshot(path=str(root/'reports/mobile-failure.png'))
  raise
 finally:
  (root/'reports/mobile-tests.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
  (root/'reports/mobile-browser.log').write_text('\n'.join(logs),encoding='utf-8')
  browser.close();server.shutdown()
