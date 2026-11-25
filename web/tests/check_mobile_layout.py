"""Browser-only geometry and touch regression; no simulated combat claims."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
(root/'reports').mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':844,'height':390},has_touch=True,is_mobile=True)
    page.set_content('<meta name="viewport" content="width=device-width,initial-scale=1"><canvas id="canvas" width="1280" height="720"></canvas>')
    page.add_style_tag(path=str(root/'web/ui/web_ui.css'))
    page.add_script_tag(path=str(root/'web/ui/web_ui.js'))
    page.evaluate('fdm.busy(false);fdm.state(JSON.stringify({scene:"battle",cards:["Soldado"]}))')
    assert page.locator('[data-action=medkit]').inner_text()=='Kit médico'
    assert page.locator('[data-action=ammo]').inner_text()=='Munição'
    assert page.get_by_role('button',name='Mais controles').inner_text()=='⋯'
    measurements=[]
    for width,height in [(568,320),(844,390),(915,412),(1280,720)]:
        page.set_viewport_size({'width':width,'height':height});page.wait_for_function('''() => {const c=document.querySelector('#canvas').getBoundingClientRect(), h=document.querySelector('#battle-web-hud').getBoundingClientRect();return Math.abs(h.width-c.width*488/1280)<1 && Math.abs(h.left-(c.left+c.width*290/1280))<1;}''')
        canvas=page.locator('#canvas').bounding_box()
        hud=page.locator('#battle-web-hud').bounding_box()
        assert abs(canvas['width']/canvas['height']-16/9)<.01
        assert canvas['height']>=min(height,width*9/16)-1
        assert hud['x']>=canvas['x']+canvas['width']*278/1280
        assert hud['x']+hud['width']<=canvas['x']+canvas['width']*790/1280
        for action in ['medkit','ammo']:
            page.locator(f'[data-action="{action}"]').tap()
            assert page.evaluate('JSON.parse(fdm.drain())')==[{'action':action}]
        page.touchscreen.tap(canvas['x']+canvas['width']/2,canvas['y']+canvas['height']/2)
        click=page.evaluate('JSON.parse(fdm.drain())')[0]
        assert click['action']=='click' and abs(click['x']-640)<3 and abs(click['y']-360)<3
        measurements.append({'viewport':[width,height],'canvas':canvas,'hud':hud})
    page.locator('#full').tap();page.wait_for_function('Boolean(document.fullscreenElement)')
    page.locator('#full').tap();page.wait_for_function('!document.fullscreenElement')
    page.evaluate('() => {document.documentElement.requestFullscreen=()=>Promise.reject(new Error("unsupported"));}')
    page.locator('#full').tap();assert page.locator('body').evaluate('(el)=>el.classList.contains("immersive")')
    page.locator('#full').tap();assert not page.locator('body').evaluate('(el)=>el.classList.contains("immersive")')
    page.evaluate('fdm.state(JSON.stringify({scene:"title"}))')
    page.locator('#full').tap()
    assert page.locator('#canvas').bounding_box()['height'] <= page.viewport_size['height']-123
    page.locator('#full').tap()
    assert page.locator('#full').is_visible() and not page.locator('#battle-web-hud').is_visible()
    page.evaluate('fdm.state(JSON.stringify({scene:"battle"}))')
    page.get_by_role('button',name='Mais controles').tap()
    assert page.locator('#touch-cards').is_hidden() # no cards in the final state
    assert page.locator('[data-action="save"]').is_visible()
    page.locator('#controls-close').tap()
    (root/'reports/mobile-layout.json').write_text(json.dumps(measurements,indent=2))
    browser.close()
print('Responsive HUD and touch mapping passed at four sizes.')
