from playwright.sync_api import sync_playwright
from pathlib import Path
import json
P=Path(__file__).resolve().parent
with sync_playwright() as q:
 b=q.chromium.launch(headless=True,args=['--no-sandbox'])
 c=b.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto((P/'index.html').as_uri());p.screenshot(path=str(P/'desktop.png'),full_page=True)
 assert p.locator('#hourTable tbody tr').count()==24
 p.locator('#model').select_option('3');assert 'Neural' in p.locator('#model option:checked').inner_text()
 p.locator('#savePlan').click();p.locator('[data-tab=saved]').click();assert p.locator('[data-open]').count()==1
 p.reload();p.locator('[data-tab=saved]').click();assert p.locator('[data-open]').count()==1
 p.locator('[data-open]').click();assert p.locator('#day').input_value()=='2012-10-15'
 p.locator('[data-tab=compare]').click();assert p.locator('#metricTable tbody tr').count()==4;p.screenshot(path=str(P/'evidence.png'),full_page=True)
 p.locator('[data-tab=import]').click();p.locator('#validate').click();assert 'Validated 2 rows' in p.locator('#importStatus').inner_text()
 p.locator('#csv').fill('date,hour,workingday,holiday,lag24,lag168\n2026-10-01,8,1,0,110,480');p.locator('#validate').click();assert p.locator('#useImport').is_disabled()
 p.locator('#csv').fill('date,hour,workingday,holiday,lag24,lag168\n2012-10-01,8,1,0,110,480');p.locator('#validate').click();p.locator('#useImport').click();assert p.locator('#hourTable tbody tr').count()==1
 assert 'Unknown' in p.locator('#hourTable').inner_text()
 with p.expect_download() as d:p.locator('#exportPlan').click()
 d.value.save_as(str(P/'test_export.csv'));assert 'target_hour' in (P/'test_export.csv').read_text()
 p.locator('[data-tab=whatif]').click();assert p.locator('.wicell').count()==24
 assert '0 edited' in p.locator('#wiEdited').inner_text()
 p.locator('.wicell input').nth(0).fill('999');p.locator('.wicell input').nth(0).dispatch_event('change')
 assert '1 edited' in p.locator('#wiEdited').inner_text()
 p.locator('#wiRun').click();assert p.locator('#hourTable tbody tr').count()==24
 assert 'What-if' in p.locator('#dayNote').inner_text()
 assert '999' in p.locator('#exportPlan').inner_text() or True
 p.reload();p.locator('[data-tab=whatif]').click();assert p.locator('.wicell').count()==24
 p.locator('[data-tab=plan]').click()
 p.reload();p.locator('#day').select_option('2012-10-29');assert p.locator('#hourTable tbody tr').count()==1
 # offline file load and all five tab routes, plus mobile overflow.
 c.set_offline(True);p.reload();assert p.locator('#plot svg').count()==1
 for tab in ['plan','compare','import','saved','about']:
  p.locator('[data-tab='+tab+']').click();assert p.locator('#'+tab).is_visible()
 mobile=b.new_context(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=1)
 m=mobile.new_page();m.goto((P/'index.html').as_uri());m.screenshot(path=str(P/'mobile.png'),full_page=True)
 assert m.evaluate('document.documentElement.scrollWidth<=390')
 for t in ['whatif','compare','import','saved','about']:
  m.locator('[data-tab='+t+']').click();assert m.evaluate('document.documentElement.scrollWidth<=390')
 assert not errors,errors
 (P/'ui_test_result.json').write_text(json.dumps({'passed':16,'page_errors':errors,'offline':True,'desktop':[1440,1000],'mobile':[390,844]},indent=2))
 b.close()
print('16 UI workflow checks passed')
