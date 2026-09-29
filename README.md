# Banned Books Evidence Atlas

Owned by tmlee10. This handover contains only the banned-books project.

## Project files

`banned-books-project.zip` contains the complete project, including Python analysis and tests, source data, the prebuilt website, and downloadable research documents, PowerPoint and QGIS files. Extract it locally to work with the source. The original research package is inside `dist/downloads/banned-books-original-project.zip`.

This is a clean snapshot of the banned-books files from `danangnu/banned-books-evidence-atlas`, commit `0c872fed742c0403d69d4732a4799e1fb77e7ee0`. It excludes the separate redlining project and its Git history. The original repository remains in place. This repository does not transfer ownership of the existing Render service.

## Deploy on Render

Connect this private repository from the intended owner's Render account. Create a Static Site using:

- Branch: `main`
- Root directory: leave blank
- Build command: `unzip -o banned-books-project.zip && bash scripts/check-static.sh`
- Publish directory: `dist`
- No environment variables or start command.

Alternatively, use the root `render.yaml` as a Blueprint. The build extracts the prebuilt website; it does not fit statistical models. Verify the map, chart and both downloads before retiring any existing deployment.

## Local verification

After extraction:

```sh
python3 -m unittest discover -s tests -v
bash scripts/check-static.sh
```

Nine tests and the static-file check passed during handover on 28 September 2026. Research findings cover July 2021 through June 2025. District-level inferential analysis remains pending required inputs. Read `RESEARCH_README.md` in the archive for definitions and limitations.


## Website update — September 29, 2026

The archive now includes an earlier-study section, an availability table for demographic and survey variables, the original report, and a CSV transcription of all 50 historical model predictions. Ohio’s 2022–2023 prediction is marked historical and unvalidated; the conflicting Idaho conclusion and negative model outputs are disclosed. No new model has been fitted, and no individual profiles are inferred from state-level data.

Direct downloads include the V2 report, proposal, analysis plan, presentation and QGIS package. The report was revised September 29; the other documents retain the September 3 versions. Original survey responses and demographic model-input CSVs remain unavailable. The website keeps the exact reviewed RQ3 and data-quality checks.


## Historical forecast visuals
Added all-state map and chart, Ohio comparison and an accessible state selector/table. Reproduce with `python analysis/forecast_visuals.py` (matplotlib required), then `python analysis/package.py`. The public 2022–2023 PEN workbook is retained in data/pen_2022_2023.xlsx. Aggregation checks both sheets independently, reconciles 3,362 events across 33 states and verifies the five published leading-state counts. Ohio has zero entries in this index, not verified zero bans. Eighteen historical predictions are negative and are marked invalid rather than clamped. No new model has been fitted. Official 2024–2025 row-level data and original survey inputs remain pending.


## Affiliation and report revision — September 29, 2026

The current report and website now reproduce the original five-state religious and political labels with an explicit source audit, rather than treating them as current verified classifications. Religion.xlsx and partisan.xlsx, source years, and respondent survey/codebook remain unavailable. The report includes the Ohio retrospective comparison and exact reviewed RQ3/checks. Recreate the historical affiliation figure with `python analysis/affiliation_visuals.py` (matplotlib required). CSV values are figure transcriptions, not refitted estimates or religion/party percentages. The proposal, plan, slides, QGIS files and full September archive retain their earlier versions.
