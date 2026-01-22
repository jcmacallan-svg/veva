# Classification helper (Excel/CSV) + apply script

## 1) Build the real Landmacht set first
Run your downloader so `app/data.json` contains all Landmacht items + images.

## 2) Fill the template
Open `vehicle_classification_template.xlsx` and fill the **class** column using the dropdown.

## 3) Apply back into the app
From your project folder:

```bash
python3 apply_classifications.py --data app/data.json --in vehicle_classification_template.xlsx
```

It updates `app/data.json` and creates a backup `app/data.json.bak`.
