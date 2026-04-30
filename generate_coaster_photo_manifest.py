import html
import json
import re
import hashlib
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd


CSV_PATH = Path("coasters_full_list_no_kings.csv")
OUTPUT_PATH = Path("coaster_photo_manifest.json")
IMAGES_DIR = Path("coaster_images")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

PIC_JSON_PATTERNS = [
    re.compile(r'<script[^>]+id=["\']pic_json["\'][^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'id=pic_json[^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL),
]
FEATURE_PAT = re.compile(
    r'id=["\']opfAnchor["\'][^>]*data-url=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def fetch_html(url: str) -> str:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def download_image(url: str, destination: Path) -> bool:
    if not url:
        return False

    try:
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = (response.headers.get("Content-Type") or "").lower()
            if "image" not in content_type:
                return False
            data = response.read()
        destination.write_bytes(data)
        return True
    except Exception:
        return False


def extract_manifest_entry(page_url: str, page_html: str) -> dict[str, str]:
    image_url = ""
    thumb_url = ""

    pic_json = None
    for pattern in PIC_JSON_PATTERNS:
        match = pattern.search(page_html)
        if not match:
            continue
        try:
            pic_json = json.loads(html.unescape(match.group(1)))
        except json.JSONDecodeError:
            pic_json = None
        break

    if pic_json and pic_json.get("pictures"):
        picture = pic_json["pictures"][0]
        sizes = picture.get("sizes") or []
        if sizes:
            thumb_url = urljoin(page_url, sizes[0].get("url", ""))
            image_url = urljoin(page_url, sizes[-1].get("url", ""))
        elif pic_json.get("sprite_url"):
            thumb_url = urljoin(page_url, pic_json["sprite_url"])

    feature_match = FEATURE_PAT.search(page_html)
    if feature_match and not image_url:
        image_url = urljoin(page_url, html.unescape(feature_match.group(1)))

    if image_url and not thumb_url:
        thumb_url = image_url

    return {
        "image_url": image_url,
        "thumb_url": thumb_url,
    }


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    IMAGES_DIR.mkdir(exist_ok=True)
    cache: dict[str, dict[str, str]] = {}
    rows: list[dict[str, str]] = []

    for row in df.to_dict("records"):
        source_url = row.get("height_drop_source_url") or row.get("track_length_source_url") or ""
        source_url = source_url if isinstance(source_url, str) else ""

        manifest_row = {
            "coaster": row["coaster"],
            "park": row["park"],
            "image_url": "",
            "thumb_url": "",
            "local_image_path": "",
            "source_url": source_url,
        }

        if source_url and "rcdb.com" in source_url:
            if source_url not in cache:
                try:
                    cache[source_url] = extract_manifest_entry(source_url, fetch_html(source_url))
                except Exception:
                    cache[source_url] = {"image_url": "", "thumb_url": ""}

            manifest_row.update(cache[source_url])

        # Save a local thumbnail copy to avoid cross-site hotlink rendering issues.
        image_candidate = manifest_row["thumb_url"] or manifest_row["image_url"]
        if image_candidate:
            stable_id = hashlib.sha1(f"{manifest_row['park']}|{manifest_row['coaster']}".encode("utf-8")).hexdigest()[:12]
            local_file = IMAGES_DIR / f"{stable_id}.jpg"
            if not local_file.exists():
                download_image(image_candidate, local_file)
            if local_file.exists():
                manifest_row["local_image_path"] = f"./{IMAGES_DIR.name}/{local_file.name}"

        rows.append(manifest_row)

    OUTPUT_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    image_count = sum(1 for row in rows if row["image_url"])
    print(f"Wrote {OUTPUT_PATH} with {image_count}/{len(rows)} coaster images.")


if __name__ == "__main__":
    main()