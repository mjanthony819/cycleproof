# CycleProof

**Demand, with doubt.** A usable, entirely local historical bike-demand planning lab, built during Peninsula Innovation Hackathon in November 2026.

Open `index.html` in a modern browser. It is a self-contained offline app with real exported model weights, historical test records and measured results. No API key, login, Python server, paid service, analytics or external runtime is required.

**Update, November 16, 2026:** the app was reworked so the trained models drive the main workflow end to end. A new 02 / What-if lab tab lets you edit a base day's inputs and re-forecast live before opening the scenario in the planner, and the interface now uses the project's charcoal/lime design. Models, data, metrics and evaluation are unchanged. `CycleProof_Demo.mp4` and `captions.srt` were recorded for the original submission and show its earlier interface.

## What you can do

- Replay eligible days from the October-December 2012 holdout.
- Edit any replayable day in the What-if lab: change per-hour lag inputs, watch the live re-forecast preview, then open the edited scenario in the planner.
- Compare yesterday, last week, boosted trees and a trained 48-24 ReLU neural network.
- Inspect predictions, calibrated uncertainty and a hypothetical hourly rental-workload limit.
- Review chronological splits, errors by slice, four rolling-origin checks, largest misses and neural seed sensitivity.
- Import a strict historical scenario CSV, validate it before inference, inspect the preview, and open the plan.
- Save up to 20 plans in local browser storage, reopen, delete or export them as CSV.
- Export a model card with all measured results and limitations.

**Not live bike availability. Not station prediction. Rental events are not fleet size, simultaneous inventory or a staffing recommendation.** No operational or safety decisions should rely on this prototype.

## Actual experiment

UCI Bike Sharing (Fanaee-T, 2013): 17,379 hourly source rows from Capital Bikeshare, Washington D.C., 2011-2012. There are 165 absent hourly timestamps in the complete two-year grid. Exact timestamp lags exclude 429 existing rows, including the first week and rows whose day/week lag is missing. Evaluation is conditional on having both lags, not all hours.

| Block | Dates | Eligible rows |
|---|---|---:|
| Train | Jan 8 2011-Jun 30 2012 | 12,641 |
| Validation | Jul-Aug 2012 | 1,488 |
| Calibration | Sep 2012 | 720 |
| Final test | Oct-Dec 2012 | 2,101 |

| Model | Test MAE | Test RMSE | Nominal 90% band coverage |
|---|---:|---:|---:|
| Yesterday | 75.476 | 125.859 | 94.19% |
| Last week | 69.474 | 114.771 | 87.05% |
| Boosted trees | 58.388 | 91.381 | 92.96% |
| Neural 48-24, seed7 | 79.681 | 118.756 | 95.05% |

Units are rental events per hour. Trees beat these baselines on this test. The neural network does not. The app does not hide this result. Neural seeds 19/31 give test MAE 77.782/71.190; seed7 was predeclared, not selected from test scores. All neural runs reached the 180-epoch cap, so convergence is not claimed. The fixed 160-round tree uses depth3 selected from {2,3} on validation MAE. Training is not repeated on validation or calibration afterward.

Input features: sine/cosine hour, weekday and day of year; known workingday and holiday flags; count at exactly t-24h and t-168h. No `casual`, `registered`, `cnt`, row ID, target-day weather or future observed count is an input. Forecasts are made at the start of a target day using the completed previous day, assuming those counts are available without reporting delay. This is a rolling day-ahead protocol, not a single forecast issued before the entire 3-month test.

Bands use the finite-sample 90% absolute-residual quantile on September calibration data. Lower bounds are clipped at zero. Displayed width is the unclipped `2*q`; actual clipped width can be narrower. Serial dependence and drift mean nominal coverage is not a guarantee. Four additional quarter-by-quarter rolling-origin fits use fixed depth3 trees; they are separate from the fixed-model final test and are reported even when the weekly baseline wins.

The Oct29-30 storm slice has **only one eligible row** after missing-hour/lag filtering. No claim of hurricane robustness is supported. Weather labels are used only for error slicing, not model input. System-wide served rentals do not measure unmet demand or neighborhood fairness.

## Run, test and reproduce

Tested with Python 3.10.12 and Node v22.23.4. Install the pinned CPU dependencies in an isolated environment:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python train.py
python build.py
node test.js
```

`hour.csv` and `DATA_README.txt` are included with attribution. To fetch the unchanged original dataset again:

```sh
python fetch_data.py
```

The source CSV SHA256 is `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f`.

Training writes `model.json`, `results.json`, `test_records.json`, `parity.json`, and logs measured results. `build.py` embeds them with the separate source HTML/JS into `index.html`. No pickled code or model deserialization is needed in the browser. Dense and tree inference match scikit-learn on 40 parity fixtures within 1e-7, all four outputs checked. `test.js` runs 55 parity/data/schema checks.

Optional browser workflow tests and demo recording use Playwright:

```sh
pip install playwright
python -m playwright install chromium
python ui_test.py
```

Sixteen desktop/mobile/offline workflow checks cover all five tabs, model choice, persistence, import failure and success, downloads and missing-hour replay. Screenshots were inspected at 1440px desktop and 390px mobile. The full app was tested with networking disabled. `reproduction.json` records the independent clean-directory retraining comparison.

## CSV contract

Plain unquoted CSV, exact header:

```csv
date,hour,workingday,holiday,lag24,lag168
2012-10-01,8,1,0,110,480
2012-10-01,9,1,0,150,260
```

1-744 rows, at most 1MB; valid 2011-2012 dates; unique target hours; integer hour0-23; binary flags; nonnegative lag counts0-1000; no conflicting weekend/holiday workingday flag. Inputs are sorted by target time. No target count column accepted. Calendar day/hour labels remain local to the source, not timezone-converted. Validation cannot prove the lags are truthful or known at forecast time. Do not import personal rider data. Storage is browser-local, not encrypted cloud backup.

## Files

- `train.py`: full training, split logic, calibration, backtests and portable export.
- `engine.js`: offline inference and import contracts.
- `app.js`, `template.html`, `build.py`: readable app source and build.
- `model.json`: actual trained tree and neural parameters plus preprocessing.
- `results.json`, `test_records.json`, `parity.json`: measured evaluation and fixtures.
- `hour.csv`, `DATA_README.txt`: credited source data and unchanged original README.
- `CycleProof_Interview_Manual.docx` and `.pdf`: architecture, science, workflow, tradeoffs, interview answers.
- `CycleProof_Demo.mp4`, `captions.srt`: narrated, visibly captioned walkthrough.
- `CycleProof_Complete.zip`: a complete offline/source distribution.

## Credit, license and AI disclosure

Data: Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5W894 . Official page: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset . Current UCI page identifies **Creative Commons Attribution 4.0 International**: https://creativecommons.org/licenses/by/4.0/legalcode . Original bundled README requires citation to Fanaee-T, Hadi and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge," Progress in Artificial Intelligence (2013), DOI10.1007/s13748-013-0040-3. Both are credited here and in the app. Data is transformed into lag features and derived test records; this project is not endorsed by the dataset creators or Capital Bikeshare.

Original app code and documentation: MIT, see `LICENSE`. Dataset remains CC BY4.0, not relicensed as MIT. Dependencies retain their respective licenses. AI assistance was used for concept development, code, tests, documentation and synthetic narration. Models were actually trained from scratch, no paid or pretrained inference API. Claims are limited to the packaged historical experiment. Solo entrant: M J Anthony. AI is not presented as an independent human teammate.

## Next month

Obtain a permitted newer dataset; evaluate all-hour missing-data strategies without invented zeros; use rolling calibration; test neighborhood-specific outcomes and reporting delays; compare a calendar-aware seasonal statistical model; interview planners before any operational trial. No live integration or automatic allocation is claimed.
