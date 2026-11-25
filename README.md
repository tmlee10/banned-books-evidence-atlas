# Banned Books Evidence Atlas

Owned by tmlee10. This repository contains only the banned-books project.

## Website revision — October 1, 2026

The update adds a 2022–2023 population-rate map, a searchable and sortable 50-state table, count/rate charts, descriptive correlations and sensitivity results. It incorporates the revised comparison report and the full reproducibility download. Exact RQ3 and checks before analysis are preserved.

The retained PEN workbook contains 3,362 event entries, including one Texas entry with no title. Counting only entries with nonblank titles produces 3,361. Both counting rules are documented. The reconstructed state comparison uses Census 2022 total residents, Gallup 2017 political shares and Pew 2014 religious shares. Florida’s rounded religion-category tie is preserved. Historical predictions remain unvalidated; no new causal model or forecast is claimed.

## Files and deployment

- `banned-books-project.zip`: prebuilt website, corrected counting audit, source tables, research scripts and historical documents/QGIS files.
- `banned-books-revised-data-code.zip`: the current report and full reproducibility download. This stays next to the project archive so each file fits the GitHub web-upload limit.
- `render.yaml`: existing static-site deployment configuration.

The Render build command remains:

```sh
unzip -o banned-books-project.zip && bash scripts/check-static.sh
```

Publish directory: `dist`. The check script copies the separate reproducibility ZIP into the website downloads and checks 63 page references, data totals and download integrity. No server process or secret is required. Use the existing Render service; this commit does not create another service.

## Reproduction and limitations

After extracting the project:

```sh
python3 run_review.py
python3 -m pip install -r state_reconstruction/requirements.txt
python3 state_reconstruction/complete_state_analysis.py
python3 analysis/export_state_map.py
```

The core audit passes 16 tests. New source joins cover all 50 states. No-entry states are not treated as proven absence of bans. The 2024–2025 map remains a published-summary map; the new rate map covers 2022–2023 and uses residents, not students.

Original chapter-model training records, respondent survey/codebook, district enrollment and restriction histories, and the 2024–2025 event export are still required for the remaining analyses. Older slides/QGIS retain their September 3 versions. See the revised report for details.


## GDELT validation website update — October 3, 2026

The website now includes `gdelt-validation.html`, a homepage summary and six CSV review tables. The frozen October 2 analysis contains 15,767 annual GDELT records, a 1,054-record candidate set and a fixed 36-record sample (12 school-topic, 4 public-library/unrelated, 20 unresolved). Eight sample records support at least one original district candidate. No new dated event links, causal claims or forecasts are accepted. Independent human review is pending.

`banned-books-gdelt-reviewed.zip` is a separate repository-root file, copied into `dist/downloads` by the existing build command. It contains the preserved exports and reproducible analysis snapshot, including its historical publication-status note. The previous state analysis, report, slides and QGIS files retain their stated versions.

No new service, credential, billing change or BigQuery job is required. `scripts/check_gdelt.py` verifies the sample counts, record IDs, candidate results, exact RQ3 and local page links.


## GDELT follow-up v12 — October 3, 2026

The same 36 selected records now include 13 supported school-topic records, four other records and 19 unresolved records. Nine support an original district candidate. The CNN Davis article was recovered; posted district minutes verify a June 20, 2023 vote to reinstate the Bible. Actual reshelving, removal onset and duration remain unverified. No model or causal estimate was added. Version 11 tables remain available as history. Eight current and historical comparison tables are linked from the validation page; the package contains primary minutes, checksums and the complete offline pipeline.


## Date audit v13 — October 4, 2026

The original workbook confirms March 2023 for Indian River and Miami-Dade, and May 2023 for Davis. Earlier report prose was one month too early; the CSV conversion was correct. All 3,362 extracted rows were checked directly against the workbook. The Indian River month conflict is withdrawn. Other date/stage questions and exact restriction durations remain unresolved.

The current validation page and archive include the corrections, workbook-cell audit, and a blank 36-record independent-review form. Review responses have not been received. The new comparison script validates returned JSON and lists disagreements without overwriting decisions. Current counts remain 13 supported school-topic records, four other records and 19 unresolved. All 116 output files regenerate byte-identically. Historical v11/v12 files preserve the prior record and should not be used for current month descriptions. No new BigQuery query, model, causal estimate or paid usage.


## Current 2025–26 analysis — November 9, 2026

The website now has a separate page, `current-2025-2026.html`, for the new analysis of PEN America’s 2025–26 index. It does not compare school years. The homepage keeps the July 2021–June 2025 study and the verification of the earlier report, with a banner and navigation link to the new page.

The page shows 11,982 recorded instances in 23 states (one title restricted in one district), with 7,370 unique titles and 114 districts as context. It includes a labelled state map, rates per million residents (Census July 2025), a searchable 50-state table, and the association with the 2024 presidential margin (FEC). It also reports negative binomial model results with leave-one-state-out validation, and Texas/Florida sensitivity. A short table separates PEN’s school-year figures from the American Library Association’s calendar-2025 statistics. Grey states have no count on PEN’s map; that does not establish that no bans occurred. The model is not a forecast.

New downloads, inside `banned-books-project.zip`: the 2025–26 presentation (PPTX and PDF) and `banned-books-2025-2026-analysis.zip` (saved sources, analysis script, tests, results and the map script). The build command and Render service are unchanged. `scripts/check_current.py` now runs in `check-static.sh` and checks the new page’s links, the 50-state data and the key totals.

## DigitalOcean deployment — November 11, 2026

The website is deployed at https://bannedbooks.research3.org/ on the existing
Research3 DigitalOcean droplet. The current analysis is at
https://bannedbooks.research3.org/current-2025-2026.html.

The deployment passed HTTPS page, state-data and all 16 download checks.
Public DNS resolves to 143.198.36.166. A separate Let's Encrypt certificate
and automatic renewal are configured for bannedbooks.research3.org.

See deployment/digitalocean/README.md for installation, DNS, HTTPS, verification
and rollback instructions. The installer uses a separate static web root and
Nginx site. Research pages and saved model outputs are unchanged.

render.yaml and the existing supporting research archives are preserved.
A GitHub push does not update DigitalOcean automatically; run the documented
installer for future deployments. The old Render service is not retired by
this change and may still deploy on commits if automatic deployment is enabled.

## Demographics, forecast test and 2026–27 outlook — November 17, 2026

`current-2025-2026.html` gains two sections. Section 06 compares the ten highest-rate states with the other forty on 13 Census measures (ACS 2025 1-year; 2020 Census urban share): they look much alike, and only the share under 18 differs beyond chance (p = 0.031), about what 13 measures would give by chance. Section 07 reports a forecast test, fitted on 2022–23 and scored on 2025–26 with only figures published before each school year began: repeating each state’s earlier recorded status got 36 of 50 states right; the population-and-election model got 27, picking up Ohio and Maryland but making 11 additional false calls. Adding a Census measure did not consistently help.

It also shows the 2026–27 outlook as of November 17, 2026 (PEN’s 2025–26 results became available after the 2026–27 school year began). The starting point is each state’s 2025–26 recorded status, with the model alongside; they agree in 30 states and disagree in 20, and agreement is not evidence that either is right. Six states with 2022–23 entries and no 2025–26 count, where the methods disagree, are described as worth monitoring, not as predictions. The outlook rates use ACS 5-year 2019–23 population (Texas 276.4 per million); the map uses the July 2025 estimate (258.4), for the same 8,193 instances. The outlook concerns where PEN will record bans.

New downloads: `banned-books-forecast-test-and-outlook.zip` and `banned-books-state-demographics-2025.zip`. They are stored beside `banned-books-project.zip` (like the GDELT package) to keep each upload under GitHub’s 25 MB limit. `check-static.sh` copies them into `dist/downloads` for Render; the DigitalOcean installer reads them from the deployment package, checks their SHA-256 values (`LOCAL_EXTRAS`) and copies them in. `PROJECT_SHA` is updated for the new archive. The presentation downloads are updated to the 47-slide deck. The DigitalOcean site changes only when the installer is rerun.

## Interactive charts — November 19, 2026

Four charts on `current-2025-2026.html` are now interactive: the state map, the highest-rates chart (top ten or all 23 states with a count; rate or instances), the rate-against-2024-vote chart (with or without Texas and Florida) and the 2026–27 outlook (all states, where the methods agree or disagree, and the six states worth monitoring). Pointing to, tapping or using the arrow keys on a state shows its figures; all four charts have a full-screen button for presenting. In full screen each chart is sized to fit the screen without scrolling. On the vote chart a note beside the checkbox states that hiding Texas and Florida changes the view while the fitted line still uses all 50 states; the live ranking chart carries a caption that holds for every view. The page also gains the site footer, and its two 50-state tables scroll inside a 560px frame with the header row kept in view, as on the homepage.

The charts are drawn by `dist/charts-2025-2026.js`, written by `tools/interactive_charts.py` from the same saved result files as the page. It uses no external libraries and makes no network requests. Every static image is kept: a chart replaces its image only after it has drawn without error, so the page still shows all charts without JavaScript, and the PNG downloads are unchanged. No figures, models or text conclusions changed. `scripts/check_current.py` also checks the four chart containers, their fallback images and the 50 states in the chart data.

## Pre-proofing review — November 20, 2026

Wording and labelling corrections ahead of proofing; no figures, models or data changed.

- `current-2025-2026.html`: the "Supported" box now reads "Nine of the ten highest-rate states voted Republican in 2024, but so did 14 of the 27 states with no recorded count." The "Not established" box adds removals that nobody reported (no national rule requires schools or libraries to report them) and widens "who challenged a book" to who challenged, reviewed or decided.
- `index.html`: two statements written before the forecast test existed ("no new causal model or forecast has been fitted"; the planned forecasting step) now point to the forecast test and dated outlook on the 2025–26 page. The 2022–23 correlation note says no causal model or forecast was fitted to those comparisons.
- Static map (`map-2025-2026.png`): Alaska and Hawaii labelled once; the Rhode Island leader no longer crosses the Connecticut label. Vote chart (`margin-2025-2026.png`): horizontal axis relabelled "Republican margin in 2024: Trump minus Harris vote share"; redrawn from the saved results, model not refitted.
- Presentation downloads: 49 slides. New slides on how a challenged book is decided (Wentzville, Missouri board minutes; Canby, Oregon review committee minutes; Clay County, Florida ballots) and on why state demographics cannot tell us who challenged a book, which quotes the earlier report's conclusion and states that the Census tables used do not measure religion, sexual orientation or gender identity. The records-request slide now lists Wentzville's board minutes as supplied (district reply of November 5, 2026).

`scripts/check_current.py` also checks that the stale homepage sentence is gone and the two new statements are present. Build command and Render service unchanged; the DigitalOcean site changes only when the installer is rerun.

## Study switch and side-by-side comparison — November 25, 2026

A bar at the top of the homepage (the previous study, July 2021–June 2025, with the review of the original report) and of `current-2025-2026.html` (the current analysis) lets a viewer move between the two, and to a new page, `compare.html`, that sets the original report, the 2022–23 baseline and the 2025–26 analysis side by side. The bar replaces the November 9 banner on the homepage.

The comparison covers the question each study asked, its data and method, where bans were recorded, party and religion, prediction, who challenged or decided, and what each cannot show. Quotations come from the original report's text; figures for the two later studies are read from the data files already published on the site. Because the three use different sources, school years and measures, the page states that reading across a row does not measure a rise or fall in book bans.

Generated by `tools/compare_page.py` from `tools/add_2025_26.py`. `scripts/check_current.py` checks the switch links on both pages, the eight comparison rows, the quoted conclusion and every local link on the new page. No figures, models or data changed.
