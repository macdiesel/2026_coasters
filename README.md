# Coasters

This repository is a small roller coaster data project to track all the coasters we will be riding in 2026

The current dataset includes:

- 97 coasters
- 8 parks
- 5 states or provinces
- published track length for 81 coasters
- height for 85 coasters
- drop height for 62 coasters
- ride time for 65 coasters
- photo coverage for 82 coasters in the local manifest

## Repository Contents

- `coasters_full_list_no_kings.csv`
  The main dataset. This is the source of truth for coaster stats and family ride credits.

- `coaster_analysis.ipynb`
  The main analysis notebook. It contains Plotly charts for:
  - coaster counts by type
  - coaster counts by state or province
  - combined drop height by park
  - total track length by park using published values only
  - coasters per park by type
  - speed vs. drop scatterplots
  - family ride totals by park and by manufacturer

- `coaster_credits_editor.html`
  A one-page HTML app for editing family ride credits visually. It shows each coaster as a card, includes a photo when available, and lets you toggle ride credit for `Kobra Kid`, `Melanie`, `DooDad`, and `Mom`.

- `coaster_photo_manifest.json`
  A generated lookup file used by the HTML editor to attach coaster images to each card.

- `generate_coaster_photo_manifest.py`
  A helper script that rebuilds the photo manifest by scraping embedded photo metadata from the RCDB source URLs already stored in the CSV.

- `rcdb_sample.html`
  A local sample page used while inspecting RCDB markup during development.

## Dataset Schema

The CSV currently contains these columns:

- `park`
- `state`
- `coaster`
- `year_built`
- `manufacturer`
- `max_height_ft`
- `drop_ft`
- `max_speed_mph`
- `coaster_type`
- `track_length_ft`
- `track_length_source_url`
- `track_length_match_type`
- `height_drop_source_url`
- `height_drop_match_type`
- `Kobra Kid`
- `Melanie`
- `DooDad`
- `Mom`
- `ride_time_sec`

Family columns use `True`, `False`, or blank values:

- `True` means the person has ridden the coaster
- `False` means the person has not ridden the coaster
- blank means unknown or not filled in yet

## Data Sources

Most enrichment in this project comes from RCDB, the Roller Coaster DataBase.

- Track length was pulled from RCDB coaster pages.
- Height and drop values were pulled from RCDB coaster pages.
- Ride time was pulled from RCDB when a duration was published.
- Photo metadata for the editor is also derived from RCDB page data.

The CSV stores source URLs and match metadata so the provenance for enriched values is preserved.

## Using the Notebook

Open `coaster_analysis.ipynb` in VS Code or Jupyter and run the cells from top to bottom.

The first code cell:

- loads the CSV into a pandas DataFrame
- normalizes coaster type labels for display
- sets shared Plotly color mappings

If you update the CSV outside the notebook, re-run the first code cell before running the later analysis cells so the notebook picks up the newest data.

## Using the Credits Editor

The editor is intended to make family ride-credit changes easier than editing CSV rows by hand.

### What it does

- loads the coaster CSV
- displays coasters as cards with photos when available
- supports search and filtering by park and person
- allows per-person ride-credit toggles
- supports bulk mark or clear for the currently visible set
- saves the CSV back out when the browser allows it, or downloads an updated copy otherwise

### Recommended way to run it

Serve the folder locally and open the HTML app in a browser.

Example on Windows with the existing virtual environment:

```powershell
c:/Users/macdiesel/Downloads/coasters/.venv/Scripts/python.exe -m http.server 8000
```

Then open:

```text
http://localhost:8000/coaster_credits_editor.html
```

Why use a local server:

- the app fetches `coasters_full_list_no_kings.csv`
- the app fetches `coaster_photo_manifest.json`
- many browsers restrict these reads when the file is opened directly from disk

## Rebuilding the Photo Manifest

If the dataset changes or you add more coasters, regenerate the image manifest:

```powershell
c:/Users/macdiesel/Downloads/coasters/.venv/Scripts/python.exe generate_coaster_photo_manifest.py
```

This reads the RCDB source URLs already stored in the CSV and writes a fresh `coaster_photo_manifest.json`.

## Python Environment

This workspace already contains a `.venv` virtual environment. The notebook and helper scripts assume Python plus the packages needed for:

- `pandas`
- `plotly`
- Jupyter notebook execution in VS Code

If you recreate the environment elsewhere, make sure those dependencies are installed.

## Typical Workflow

1. Update or review coaster records in `coasters_full_list_no_kings.csv`.
2. If needed, regenerate `coaster_photo_manifest.json`.
3. Use `coaster_credits_editor.html` to adjust family ride credits more quickly.
4. Re-run `coaster_analysis.ipynb` to refresh the visualizations.

## Notes

- Not every coaster has a published track length, drop, or ride time.
- Not every coaster has a photo available in the local manifest.
- Some newer or less-documented coasters may still have missing values.