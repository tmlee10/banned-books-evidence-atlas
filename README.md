# Banned Books Evidence Atlas

Owned by tmlee10. This handover contains only the banned-books project.

## Project files

`banned-books-project.zip` contains the complete 24-file project, including Python analysis and tests, source data, the prebuilt website, and downloadable research documents, PowerPoint and QGIS files. Extract it locally to work with the source. The original research package is inside `dist/downloads/banned-books-original-project.zip`.

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
