"""Downloads every file listed in assets/manifest.txt that is not in the repo yet.
Runs inside GitHub Actions (see .github/workflows/fetch-assets.yml)."""
import os, sys, time, urllib.request

ok = fail = skipped = 0
for line in open("assets/manifest.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    path, url = line.split(" ", 1)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        skipped += 1
        continue
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (asset-migration)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) < 100:
                raise ValueError("file too small")
            with open(path, "wb") as f:
                f.write(data)
            ok += 1
            print(f"OK   {path} ({len(data)//1024} KB)")
            break
        except Exception as ex:
            print(f"retry {attempt+1} {path}: {ex}")
            time.sleep(3 * (attempt + 1))
    else:
        fail += 1
        print(f"FAIL {path} <- {url}")

print(f"\ndownloaded={ok} already-present={skipped} failed={fail}")
sys.exit(1 if fail else 0)
