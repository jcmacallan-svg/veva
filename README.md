# NL Defensie Materieelherkenning – Speaking Trainer (Offline images)

This version is designed for **GitHub Pages** and works **without hotlinking** images.

## Step 1: Open the app
Open `app/index.html` (Chrome/Edge).

## Step 2: Build the full Landmacht set with OFFLINE images
Run on your own laptop (internet required):

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install requests pillow beautifulsoup4
python build_landmacht_offline.py --out app --size 900x600 --delay 0.6
```

This will:
- download all Landmacht vehicle images from Defensie.nl item pages
- resize them to **900×600**
- save them into `app/images/`
- rewrite `app/data.json` to include all Landmacht vehicles

## Input mode: typing vs multiple choice
Open `app/data.json` and change:

- `settings.inputMode` = `"type"` (students type the name) **or**
- `settings.inputMode` = `"mcq"` (4 multiple-choice options)

## GitHub Pages
Settings → Pages → Deploy from branch → folder `/app`.

## Notes
Keep attribution to Defensie.nl when publishing.
