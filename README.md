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
