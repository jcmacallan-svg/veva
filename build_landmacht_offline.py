#!/usr/bin/env python3
"""
Offline Landmacht builder for the Speaking Trainer.

What it does:
- Reads the Defensie.nl topic page: /onderwerpen/materieel/voertuigen
- Extracts all item links
- For each item:
  - extracts the first /binaries/large/... image
  - downloads and resizes to 900×600
  - saves as app/images/<asset>.jpg
- Writes app/data.json with a complete Landmacht question set (asset-based, offline)

Run (in this repo folder):
  python -m venv .venv
  # Windows: .venv\\Scripts\\activate
  # macOS/Linux: source .venv/bin/activate
  pip install requests pillow beautifulsoup4
  python build_landmacht_offline.py --out app --size 900x600 --delay 0.6

Then commit the app/ folder to GitHub Pages (folder /app).
"""
import argparse, os, re, time, json
from urllib.parse import urljoin
import requests
from PIL import Image, ImageOps
from io import BytesIO
from bs4 import BeautifulSoup

BASE = "https://www.defensie.nl"
TOPIC = f"{BASE}/onderwerpen/materieel/voertuigen"
UA = {"User-Agent":"Mozilla/5.0 (education speaking trainer offline builder)"}

def fetch(url):
    r = requests.get(url, timeout=60, headers=UA)
    r.raise_for_status()
    return r.text

def extract_title(html):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.I|re.S)
    if not m: return None
    t = re.sub(r"<[^>]+>", "", m.group(1))
    return re.sub(r"\\s+"," ",t).strip()

def extract_large_image_url(html):
    m = re.search(r"/binaries/large/[^\"'>\s]+", html)
    if not m:
        return None
    return urljoin(BASE, m.group(0))

def slug(s):
    s = s.lower()
    s = re.sub(r"[’'\\\"`]", "", s)
    s = re.sub(r"[^a-z0-9]+","-", s).strip("-")
    return (s[:60] or "item")

def resize_to(jpg_bytes, size):
    im = Image.open(BytesIO(jpg_bytes)).convert("RGB")
    im = ImageOps.exif_transpose(im)
    im = ImageOps.fit(im, size, method=Image.Resampling.LANCZOS, centering=(0.5,0.5))
    out = BytesIO()
    im.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return out.getvalue()

def aliases(title):
    t = title.lower()
    t = re.sub(r"\\(.*?\\)", "", t).strip()
    t = re.sub(r"\\s+"," ",t)
    a=set([t])
    if " - " in t: a.add(t.split(" - ")[0].strip())
    parts=t.split()
    if len(parts)>=2: a.add(" ".join(parts[:2]))
    return sorted(x for x in a if x)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="app", help="Output app folder (contains index.html, data.json, images/)")
    ap.add_argument("--size", default="900x600", help="e.g. 900x600")
    ap.add_argument("--delay", type=float, default=0.6, help="Delay between requests")
    args = ap.parse_args()
    w,h = map(int, args.size.lower().split("x"))

    out_dir = args.out
    img_dir = os.path.join(out_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    # load existing data.json to keep settings + UI configuration
    with open(os.path.join(out_dir,"data.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Fetching topic page:", TOPIC)
    topic_html = fetch(TOPIC)
    soup = BeautifulSoup(topic_html, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/onderwerpen/materieel/voertuigen/") and href != "/onderwerpen/materieel/voertuigen":
            links.append(urljoin(BASE, href.split("#")[0].split("?")[0]))
    # dedupe
    seen=set(); item_pages=[]
    for u in links:
        if u not in seen:
            seen.add(u); item_pages.append(u)

    print("Items found:", len(item_pages))

    questions=[]
    for i, page in enumerate(item_pages, 1):
        try:
            html = fetch(page)
            title = extract_title(html) or f"Landmacht item {i}"
            img_url = extract_large_image_url(html)
            asset = slug(title)

            if img_url:
                img_bytes = requests.get(img_url, timeout=90, headers=UA).content
                jpg = resize_to(img_bytes, (w,h))
                with open(os.path.join(img_dir, asset+".jpg"), "wb") as f:
                    f.write(jpg)
            else:
                # if no image found, keep placeholder
                asset = "missing"

            questions.append({
                "id": f"army_{asset}_{i}",
                "branch": "army",
                "asset": asset,
                "answer": title,
                "aliases": aliases(title),
                "source_page": page
            })
            print(f"[{i}/{len(item_pages)}] OK:", title)
            time.sleep(args.delay)
        except Exception as e:
            print(f"[{i}/{len(item_pages)}] SKIP:", page, e)

    data["questions"] = questions
    # keep only Landmacht active labels; others remain for later
    with open(os.path.join(out_dir,"data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("DONE. Questions:", len(questions))
    print("You can now open:", os.path.join(out_dir,"index.html"))

if __name__ == "__main__":
    main()
