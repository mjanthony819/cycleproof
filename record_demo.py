import json,re,textwrap,wave,time
from pathlib import Path
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
texts=[
'A bike-demand forecast is easy to turn into a confident number. CycleProof asks a better question: what should a planner do when that number is wrong? This is a historical planning lab, not a live bike-availability service.',
'Pick a day and compare yesterday, last week, boosted trees, and a neural network. The shaded band shows uncertainty. Change the hypothetical hourly workload limit, and the app flags hours worth reviewing. Rental events are not fleet size.',
'These models were actually trained. On two thousand one hundred and one held-out hours, boosted trees have a mean absolute error of fifty-eight point four rentals per hour. Last week gets sixty-nine point five. The neural network gets seventy-nine point seven. Deep learning does not win this test.',
'Time stays in order. Training ends in June, validation uses July and August, calibration uses September, and the final test is October through December. Features use calendar and exact one-day and one-week lags. No target-day weather or component-count leakage.',
'Import a historical scenario as CSV. The app rejects wrong columns, impossible dates, duplicate hours, and missing or invalid counts. It predicts locally using exported model weights. Save a plan in your browser, or export the hourly review as a CSV.',
'The limits matter. Missing timestamps exclude some hours, so this is not an all-hours evaluation. There is only one eligible storm-period row. The data is one city from twenty eleven and twenty twelve, and uncertainty is not a guarantee. CycleProof makes those limits part of the decision.'
]
durations=[]
for i in range(1,7):
 with wave.open(str(P/f'seg{i}.wav')) as w:durations.append(w.getnframes()/w.getframerate())
(P/'narration.json').write_text(json.dumps({'segments':texts,'durations':durations},indent=2))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
cues=[];start=0
for txt,dur in zip(texts,durations):
 sentences=re.split(r'(?<=[.!?])\s+',txt)
 chunks=[]
 for sentence in sentences:
  words=sentence.split()
  while words:
   take=words[:13];words=words[13:];chunks.append(' '.join(take))
 total=sum(len(x.split()) for x in chunks);t=start
 for chunk in chunks:
  end=t+dur*len(chunk.split())/total;cues.append(f'{len(cues)+1}\n{stamp(t)} --> {stamp(end)}\n'+ '\n'.join(textwrap.wrap(chunk,62))+'\n');t=end
 start+=dur
(P/'captions.srt').write_text('\n'.join(cues))
with sync_playwright() as q:
 b=q.chromium.launch(args=['--no-sandbox']);c=b.new_context(viewport={'width':1440,'height':900},record_video_dir=str(P/'recording'),record_video_size={'width':1440,'height':900})
 p=c.new_page();p.goto((P/'index.html').as_uri());p.wait_for_selector('#plot svg')
 t0=time.monotonic()
 def until(sec):p.wait_for_timeout(max(0,(t0+sec-time.monotonic())*1000))
 until(durations[0]);p.evaluate('window.scrollTo(0,320)');p.locator('#model').select_option('1');p.wait_for_timeout(2500);p.locator('#model').select_option('2');p.locator('#capacity').fill('300');p.locator('#capacity').dispatch_event('change')
 until(sum(durations[:2]));p.locator('[data-tab=compare]').click();p.evaluate('window.scrollTo(0,390)')
 until(sum(durations[:3]));p.evaluate('window.scrollTo(0,0)')
 until(sum(durations[:4]));p.locator('[data-tab=import]').click();p.locator('#validate').click();p.wait_for_timeout(4000);p.locator('#useImport').click();p.evaluate('window.scrollTo(0,300)');p.locator('#savePlan').click()
 until(sum(durations[:5]));p.locator('[data-tab=about]').click();p.evaluate('window.scrollTo(0,190)')
 until(sum(durations));p.screenshot(path=str(P/'demo_final.png'))
 video=p.video.path();c.close();b.close()
 (P/'recording_path.txt').write_text(str(video));print(video)
