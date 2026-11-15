from pathlib import Path
import json
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
P=Path(__file__).resolve().parent;R=json.loads((P/'results.json').read_text())
d=Document();sec=d.sections[0];sec.top_margin=Inches(.7);sec.bottom_margin=Inches(.65);sec.left_margin=sec.right_margin=Inches(.8)
styles=d.styles
for n in ['Normal','Body Text']:
 styles[n].font.name='Calibri';styles[n].font.size=Pt(11);styles[n].paragraph_format.space_after=Pt(7)
for n,size in [('Title',34),('Heading 1',25),('Heading 2',16),('Heading 3',12)]:
 styles[n].font.name='Calibri';styles[n].font.size=Pt(size);styles[n].font.color.rgb=RGBColor.from_string('176855')
styles['Normal'].paragraph_format.line_spacing=1.1
header=sec.header.paragraphs[0];header.text='CYCLEPROOF  /  TECHNICAL & INTERVIEW MANUAL';header.style='Caption'
f=sec.footer.paragraphs[0];f.text='M J Anthony  ·  November 2026  |  Historical research prototype  ·  '
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');f._p.append(fld)
def p(s,style=None):d.add_paragraph(s,style)
def h(s):d.add_heading(s,2)
def page(title):d.add_page_break();d.add_heading(title,1)
def bullets(items):
 for x in items:p(x,'List Bullet')
def tbl(headers,rows):
 t=d.add_table(rows=1,cols=len(headers));t.style='Light Shading Accent 1'
 for c,s in zip(t.rows[0].cells,headers):c.text=str(s)
 for row in rows:
  for c,s in zip(t.add_row().cells,row):c.text=str(s)
# 1
p('FIELD NOTES / 01', 'Subtitle');d.add_heading('CycleProof',0);d.add_heading('Demand, with doubt.',1)
p('A historical bike-demand planning lab with actual machine-learning and neural training, transparent uncertainty and local browser inference.')
p('Technical walkthrough, reproducibility guide and 32 interview questions with answers.')
p('Built for Peninsula Innovation Hackathon during November 2026. Solo entrant: M J Anthony. AI assistance is disclosed in the app, source and entry.')
h('The one-sentence explanation')
p('CycleProof lets a student or mobility planner replay historical system-wide bike demand, compare baselines with trained models, and keep an exportable decision trail without pretending that a point forecast is certain.')
h('The result to remember')
p('On 2,101 eligible held-out hours, boosted trees achieved MAE 58.39 rental events/hour, the weekly baseline 69.47, and the predeclared neural model 79.68. The neural network did not win.')
h('The boundary to remember')
p('This is Washington D.C. data from 2011-2012. It is not current availability, station inventory, fleet sizing, a staffing recommendation or an operationally validated forecasting service.')
h('Read this manual in four passes')
bullets(['Pages 2-3: demo and system design.','Pages 4-8: data, experiment, uncertainty and limitations.','Pages 9-10: reproduce and defend the product.','Pages 11-14: interview questions and direct answers.'])
#2
page('02 / A two-minute demonstration')
bullets(['Open index.html. No server or account is needed. Start with October 15, 2012.','Compare Yesterday, Last week, Boosted trees and Neural 48-24 using the model selector. The plotted actual demand stays fixed.','Change the illustrative workload limit from 400 to 300. Notice how the number of review hours changes without changing the forecast.','Open Evidence. Read the full test table before mentioning any model score. Show that neural performance is worse than the weekly baseline.','Show the chronological split and the one-row storm slice. This is an opportunity to explain what the experiment cannot establish.','Open Import a plan. Validate the provided CSV, inspect predictions, then introduce a wrong column or impossible date and show rejection.','Open the imported plan, save it, reopen it from Saved work, and export hourly CSV.','Finish with Model card: intended use, limits, data attribution and AI disclosure.'])
h('What to say while pointing at the chart')
p('The dark line is observed demand in the historical replay. The green line is the selected model. The band is a calibration-based interval. The dashed line is my hypothetical rental-workload limit. A flagged hour means review, not an automatic staffing decision.')
h('If the app is offline')
p('That is expected. It is a single HTML file with embedded parameters and records. Network access is only used if someone chooses an external credit link. No remote inference or API key is involved.')
h('If an imported plan has no actual count')
p('The app shows Unknown and does not report accuracy. Validation proves the format, not the truth or suitability of the data.')
#3
page('03 / System architecture')
tbl(['Layer','Input → output'],[['Source','hour.csv → timestamp-indexed count series'],['Feature builder','calendar + exact t-24h/t-168h count lookups'],['Training','CPU scikit-learn → actual tree and dense parameters'],['Evaluation','chronological masks → metrics, slices, residual quantiles'],['Export','model.json + test_records.json + results.json'],['Build','template.html + engine.js + app.js → one offline index.html'],['Interaction','local validation → JavaScript inference → review/save/export']])
h('Why this design')
p('The UI is useful even without a backend. A judge can download one file, inspect a historical day and run imported rows through actual model parameters. Separate readable source files keep the delivered app auditable. The trained parameter JSON avoids unsafe pickle loading in the browser.')
h('Inference details')
p('A tree starts at node zero, compares one feature against a threshold, follows its left or right child, and returns a leaf value. The boosted prediction is the training-set constant plus learning rate times the sum of 160 tree outputs. The neural network standardizes ten inputs using training-only means/scales, applies dense 48-unit and 24-unit ReLU layers, then one linear output. The target is transformed back using training mean and standard deviation. Negative predictions are clipped to zero.')
h('Correctness boundary')
p('Forty fixtures span the final test. All four JavaScript outputs match Python reference outputs within 1e-7. This establishes export/inference parity, not the validity of the predictive model in another city.')
#4
page('04 / Data rights and data meaning')
p('The source is UCI Bike Sharing, Hadi Fanaee-T (2013), DOI 10.24432/C5W894. It contains system-wide hourly served rental counts for Capital Bikeshare in Washington D.C., 2011-2012. The downloaded hour.csv contains 17,379 rows. UCI metadata says 17,389 instances; the code verifies and reports the actual file count instead of repeating that metadata discrepancy.')
h('Rights and credit')
p('The current official UCI dataset page identifies Creative Commons Attribution 4.0 International. The original bundled README requires citation to Fanaee-T and Gama, Event labeling combining ensemble detectors and background knowledge, Progress in Artificial Intelligence (2013), DOI 10.1007/s13748-013-0040-3. Both citations and the original README are preserved. App code is MIT; the dataset is not relicensed as MIT.')
h('What the target means')
p('cnt is the total served rental events in an hour, equal to casual plus registered. Those two component counts are forbidden inputs because they reveal the answer. Served rentals are not unmet demand, station stock, simultaneous bikes in use, or neighborhood access.')
h('Missing hours')
p('The full two-year hourly grid has 165 timestamps absent from the file. A row shift would silently turn a 24-row lag into something other than 24 hours. CycleProof reindexes exact timestamps. Of the existing rows, 429 are excluded because one or both lag timestamps are unavailable; this includes the initial week. No missing value is filled with zero.')
h('Source verification')
p('hour.csv SHA256: '+R['sha256'])
p('The fetch script checks this exact hash and refuses a changed source. A clean rerun independently downloaded the ZIP again and reproduced the model, results, test records and parity fixtures byte for byte.')
#5
page('05 / Forecast protocol and leakage')
h('Forecast origin')
p('At the start of each target day, assume the previous day is complete and its counts are available without reporting delay. Predict the next 24 target hours using calendar and counts at exactly 24 and 168 hours before each target. This is a rolling day-ahead protocol. It is not one forecast issued before the entire three-month test; later test days legitimately use observed earlier test-day counts that would then be known.')
h('Ten inputs')
bullets(['Sine and cosine of hour, weekday and day of year: six cyclical features.','Known workingday and holiday flags: two features.','Exact same-hour count one day ago and one week ago: two features.'])
h('Deliberate exclusions')
p('No target count, casual, registered, row ID, target-day observed weather or future count is an input. The product does not need an oracle-weather disclaimer because it does not use weather to predict. Observed weather is used after prediction to inspect the rain/snow error slice.')
h('Chronological separation')
tbl(['Block','Range','Rows'],[[n,s['start'][:10]+' to '+s['end'][:10],s['n']] for n,s in R['splits'].items()])
h('What is still imperfect')
p('Count reporting could be delayed in a real service; that delay is not modeled. Local hourly labels are retained without timezone conversion, and no new daylight-saving reconstruction is claimed. Holiday flags come from the source; future holiday calendars are not supplied by a live service. Import validation cannot prove that the user supplied truly available lag values.')
#6
page('06 / Training the actual models')
h('Baselines first')
p('Yesterday returns lag24 and Last week returns lag168. They require no fitted parameters. A complicated model must beat a plausible seasonal baseline, not an arbitrary constant, to justify itself.')
h('Boosted trees')
p('GradientBoostingRegressor, 160 estimators, learning rate0.05, Huber loss, seed7. Maximum depth 2 and3 were compared on July-August validation MAE. Depth3 won: MAE53.36 versus54.26. The selected model remains fitted on the original training block only. The app uses its actual exported thresholds, children and leaf values.')
h('Neural model')
p('MLPRegressor with hidden widths48 and24, ReLU, Adam, alpha0.03, batch128, learning rate0.001, max180 epochs. Input standardization and target mean/std are fitted on training only. No internal random validation split is used. All runs reached the180-epoch cap; convergence is not claimed. Seed7 was predeclared as the app model. Seeds19 and31 are reported as sensitivity runs, not selected on the final test.')
h('Why not call this a temporal CNN')
p('It is a multilayer perceptron over engineered calendar and lag features. It has two hidden layers, so it is a genuine trained neural network, but it does not learn a convolution over a raw temporal sequence. Naming the architecture precisely matters more than sounding advanced.')
h('No result manufacture')
p('The training program computes all metrics from saved predictions. The app embeds those results. There are no fabricated benchmark values, paid inference calls, synthetic target labels or pretrained black-box models. AI assistance helped write and test the implementation, not replace the measured experiment.')
#7
page('07 / Results and what they support')
tbl(['Model','MAE','RMSE','Coverage'],[[n,f"{v['test']['mae']:.2f}",f"{v['test']['rmse']:.2f}",f"{v['test']['coverage90']*100:.2f}%"] for n,v in R['report'].items()])
p('All test errors are rental events per hour over the same 2,101 eligible target rows. Lower MAE and RMSE are better. Tree MAE is about 16% lower than the weekly baseline on this fixed test. This is one historical city and time split, not a universal improvement claim.')
h('Neural sensitivity')
tbl(['Seed','MAE','RMSE'],[[x['seed'],f"{x['mae']:.2f}",f"{x['rmse']:.2f}"] for x in R['seed_sensitivity']])
p('The neural network did worse than the weekly baseline in each reported run. More tuning might help, but any future tuning would require a new final holdout. Reusing this test for architecture selection would change its status from untouched evaluation to development data.')
h('Rolling-origin stability')
tbl(['Quarter start','Tree MAE','Weekly MAE'],[[x['start'],f"{x['tree']['mae']:.1f}",f"{x['weekly']['mae']:.1f}"] for x in R['backtests']])
p('These separate fixed-depth 3 tree refits use only data before each quarter. The weekly baseline wins in some quarters. The final fixed-model result is therefore not evidence that boosted trees always win. No statistical significance, causal effect or production SLA is claimed.')
#8
page('08 / Uncertainty, failure and harm')
h('Interval construction')
p('For each model, compute absolute calibration residuals on September. Sort them and take rank ceil((n+1)×0.90), capped at n. For a prediction p, display [max(0,p-q),p+q]. The model-specific q is fixed before the October-December test. The results table reports unclipped width2q; a lower bound clipped at zero has a narrower displayed interval.')
h('Why 90% is not a promise')
p('The usual exchangeable-residual interpretation is not assured for serially dependent, drifting demand. We report actual later-block coverage. Last week covers87.05%, below the90% nominal target, while other models over-cover. Wider bands can achieve coverage while being less useful. Do not rank interval quality by coverage alone.')
h('Known missingness bias')
p('Only one October29-30 row remains eligible after exact-lag filtering. That is not enough to evaluate the storm. The dataset and missingness cannot support a hurricane-robustness claim. Complete-lag evaluation may omit exactly the disruptions where a planner most needs help.')
h('Potential harms')
bullets(['Treating system-wide counts as station-level demand could misallocate resources.','Confusing rental events with simultaneous bikes could produce a false fleet-size estimate.','Historical served demand can hide unmet demand and inequity.','Overconfident forecasts could create bad staffing or financial decisions.','Imported private rider records would be inappropriate, even though the app is local.'])
h('Product response')
p('The app labels its scope at the top, exposes actual error and partial days, rejects unsupported current dates, shows model comparisons, and frames the threshold as a review aid. No automated allocation, purchase or operational action is taken.')
#9
page('09 / Reproduce, test and debug')
h('Minimal run')
p('Open index.html. For source changes, run python build.py. For the full experiment, create a Python virtual environment, install requirements.txt, run python fetch_data.py, python train.py, python build.py, then node test.js. Training is CPU-only. The pinned versions and source hash are recorded in results.json.')
h('Evidence layers')
bullets(['55 engine/data/schema checks, including40 parity fixtures with all four outputs checked.','16 UI workflow checks at1440px desktop and390px mobile, all five tabs, import success/failure, local persistence, missing-hour replay and CSV download.','Offline reload with networking disabled.','Actual desktop/mobile pixels inspected, including a fixed mobile overflow issue.','Clean-directory source re-download and complete retraining matched all five core artifact SHA256 hashes exactly.','Final repository clone is checked separately after publication; the finished distribution includes reproduction evidence.'])
h('Common issues')
p('Blank page: use a current browser and inspect its console; no npm install is required. CSV rejection: use the provided exact schema, no quotes, blank values or extra target columns. No saved plan: local storage may be disabled, cleared or full; export a CSV. Partial day: the app deliberately refuses to invent missing lags. Changed source hash: stop and investigate rather than silently changing the benchmark.')
h('What tests do not prove')
p('Passing UI and parity checks proves that the implemented workflow runs and exported inference matches Python. It does not prove future accuracy, fairness, correct imported lags, station-level utility, causal effects or operational suitability.')
#10
page('10 / Product decisions and next month')
h('Who this helps now')
p('Students and early-stage community-mobility researchers can inspect a real forecast experiment, make a hypothetical review plan, and keep the assumptions next to the result. The product joins a decision workflow to the benchmark instead of presenting an isolated accuracy number.')
h('Why offline')
p('No server means no recurring inference cost, no API secrets, no account setup and no data upload. It also limits synchronization, access control and live data. Local storage is convenience, not secure multi-user infrastructure. The one-file build trades code duplication for reliable demonstration and backup access.')
h('Why strict historical imports')
p('Allowing arbitrary2026 data into a2011-2012 city model would make the app look more capable than the evidence supports. The schema therefore limits dates and count ranges. These guardrails can reject plausible out-of-distribution inputs; that is a deliberate scope boundary, not a universal validator.')
h('Month-one plan')
bullets(['Week1: interview planners about whether a workload review changes decisions; obtain a permitted newer dataset.','Week2: model reporting delay and all-hour missing-data strategies without zero-fill leakage.','Week3: use rolling calibration, assess neighborhoods and demand suppression, compare a calendar-aware seasonal model.','Week4: run a retrospective decision study before considering a human-reviewed pilot. Keep all automatic operational actions disabled.'])
h('What was built during the event')
p('The concept, training/evaluation/export pipeline, local planning app, validation, save/export workflow, test suite, narrated captioned demo and manual were created in November2026. The historical dataset and dependencies are reused with credit. AI helped with design, code, tests, writing and synthetic narration; the model results are measured. No claim of independent unaided authorship is made.')
QA=[
('What is CycleProof?','A historical day-ahead bike-demand planning lab. It combines four model comparisons with uncertainty, strict CSV import and saved/exportable review plans. Its purpose is to expose what a forecast can and cannot support, not to run a live bike system.'),
('What problem does it solve?','It closes the gap between a benchmark score and a planning discussion. A user can see which hours might exceed a hypothetical workload limit, inspect uncertainty and preserve the assumptions. The prototype does not claim that this decision support is operationally validated.'),
('What is original here?','The original contribution is the offline end-to-end planning workflow, portable trained-model inference, temporal evaluation and explicit failure boundaries. The dataset, boosted-tree algorithm and MLP algorithm are established and credited; I do not claim a new learning algorithm.'),
('Why bike sharing rather than another classifier?','It makes time, missingness and uncertainty central. A model can look good on average and still miss a rush hour or disruption. The planning interface lets those differences affect a review workflow rather than ending at a single accuracy metric.'),
('Why use regression metrics?','The target is a nonnegative count, not a class. MAE is interpretable as average rental events missed per hour. RMSE penalizes large errors more heavily. Neither metric alone captures the cost of underprediction at important times.'),
('Why not use accuracy?','Accuracy normally assumes class labels or a tolerance that has to be defined. Calling a count forecast accurate without a threshold would be vague. MAE, RMSE and empirical band coverage state the error and interval behavior directly.'),
('How did you avoid target leakage?','The model never receives cnt, casual, registered, target-day observed weather or future count. It uses known calendar and exact24h / 168h historical counts. Preprocessing is fitted on train only. Tuning uses validation; interval calibration and final test remain later blocks.'),
('Why is casual plus registered dangerous?','Those are the components of cnt. Giving them to a model predicting cnt would effectively give it the answer. A near-perfect score from that setup would measure leakage, not forecasting ability.'),
('Why chronological splits?','A deployed forecast cannot train on future demand. A shuffled split would mix nearby future and past patterns and overstate realistic performance. The fixed chronological split tests later months and makes temporal drift visible.'),
('Can test-period counts ever be features?','Yes, under a rolling day-ahead protocol, an earlier test day becomes observed history before a later target day is forecast. It is not allowed to use a count that would still be future at that specific forecast origin. This is not a single three-month-ahead forecast.'),
('Why exact timestamp lags?','There are165 absent hours. A24-row shift is not necessarily24hours. Timestamp reindexing looks up the intended same hour, refuses unavailable lags and avoids silently changing the forecast problem.'),
('What selection bias remains?','The benchmark contains only rows with both lags. Missingness can be informative, and disruptions may disappear from evaluation. The storm slice has only one eligible row. The score is conditional on complete lags, not all-hours robustness.'),
('What neural architecture is used?','A dense multilayer perceptron with10inputs, hidden ReLU layers of48and24units and one linear output. Features and targets are scaled using train-only statistics. It is not a temporal CNN, recurrent model or pretrained model.'),
('Did deep learning win?','No. The predeclared neural seed7 has test MAE79.68 versus69.47 for last week and58.39 for boosted trees. Seeds19and31 also do worse than the weekly baseline. The app shows this instead of hiding or renaming the loss.'),
('Why might the MLP lose?','Possible reasons include sample size, fixed hyperparameters, incomplete optimization, engineered features favoring trees and temporal drift. Those are hypotheses, not measured causal explanations. All runs hit180epochs, so I do not claim convergence.'),
('How was the tree selected?','Two depths,2and3, were compared on July-August validation MAE. Depth3won. Both used160rounds, Huber loss, learning rate0.05 and seed7. The selected model was not refitted on calibration or the final test.'),
('What do the rolling backtests show?','Four fixed-depth 3 trees are refitted before successive2012quarters. They test temporal stability separately from the final fixed model. The weekly baseline wins some quarters, so one good final-test result does not establish universal superiority.'),
('How are intervals calculated?','Use September absolute residuals and a finite-sample90%quantile. Add/subtract the model-specific quantile from each prediction and clip the lower bound at zero. The threshold is fixed before the test. This is a simple calibration method, not a guaranteed time-series interval.'),
('Why is coverage not guaranteed?','Residuals are time-dependent and the demand distribution drifts. Exchangeability is not established. We show actual later coverage: the weekly baseline under-covers at87.05%, while the other bands over-cover. Wider bands can be less useful even with high coverage.'),
('Does a workload limit determine fleet size?','No. Rentals/hour are events, not simultaneous inventory. A rider may return a bike that another rider uses later. Fleet and station planning require trip duration, flows, rebalancing, unmet demand and operational constraints that this dataset does not provide.'),
('What happens with a current-city CSV?','The validator rejects dates outside2011-2012. It is a historical scenario tool with explicit scope. Even valid historical dates do not prove another city or synthetic scenario is in distribution. The model card warns against operational use.'),
('What does validation check?','Exact header, row/file limits, valid historical dates, unique target hours, integer hours, binary flags, nonnegative bounded lag counts and workingday conflicts. It does not verify that lag values are true or known at the forecast origin.'),
('Where does imported data go?','It remains in browser memory until saved locally. No inference request, upload or telemetry is sent. Saved plans use localStorage and remain in that browser. They are not encrypted backups, and clearing browser data deletes them.'),
('How does JavaScript run a trained model?','The exported JSON contains actual tree arrays and dense matrices. JavaScript traverses each tree and evaluates the dense layers with the saved preprocessing. Forty fixtures test all four outputs against Python within1e-7.'),
('Why not just show precomputed predictions?','Historical replay does use preserved test records, but imported rows execute the exported model locally. That second path makes it a working inference product rather than a static score dashboard. Parity tests check the inference math.'),
('How can another person reproduce it?','Install the pinned CPU requirements, fetch the hash-verified source, run train.py, build.py and test.js. The clean re-download/retrain matched all five core artifact hashes exactly. The repo and complete ZIP include source, parameters, results and instructions.'),
('What are the biggest harms?','Misreading system demand as station availability, treating forecasts as staffing orders, overlooking unmet demand or inequity, and assuming intervals guarantee safety. The app places these boundaries next to the controls and never takes operational actions.'),
('What did AI do?','AI assisted concept work, implementation, tests, documentation and synthetic narration. The source dataset is credited, the models were trained from scratch and all reported metrics are computed. AI assistance is disclosed rather than presented as unaided human work.'),
('What licenses apply?','Original code/docs are MIT. The dataset is CC BY4.0 according to the official current UCI page, with original README and publication citation preserved. Third-party dependencies retain their licenses. This does not imply endorsement by the dataset creators.'),
('What would you improve first?','Validate with a permitted newer dataset and a planner interview, then model reporting delays and missingness, use rolling calibration and inspect neighborhood outcomes. More neural layers would not be the first priority without evidence that they solve a real failure.'),
('What would make it production-ready?','A live permitted data source, reporting-delay handling, monitoring, operational cost evaluation, fairness review, access control, reliability and human review are missing. A successful offline demo and a low historical MAE are not sufficient.'),
('What is the honest closing pitch?','CycleProof is valuable because it makes uncertainty and model failure usable in a real review workflow. It trains actual models, lets a simple baseline compete, and refuses claims its historical evidence cannot support. It is a research product, not a promise of future performance.')]
for start in range(0,len(QA),8):
 page(f'{11+start//8:02} / Interview answers {start+1}-{min(start+8,len(QA))}')
 for i,(q,a) in enumerate(QA[start:start+8],start+1):
  d.add_heading(f'{i}. {q}',3);p(a)
d.core_properties.title='CycleProof Technical and Interview Manual';d.core_properties.author='M J Anthony';d.core_properties.subject='Historical bike-demand planning, actual trained ML/DL, honest evaluation'
d.save(P/'CycleProof_Interview_Manual.docx')
print('Saved DOCX,',len(QA),'questions')
