"""Relance le téléchargement des images en échec dans import/manifest.json, lentement (Google limite le débit)."""
import json
import pathlib
import time
import urllib.error

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from import_google_sites import EXT, get  # noqa: E402

out = pathlib.Path("import")
manifest = json.loads((out / "manifest.json").read_text())
for m in manifest:
    if m["fichier"]:
        continue
    got = None
    for suffix in ("=s0", "=w2048", ""):
        try:
            got = get(m["source"] + suffix)
            break
        except urllib.error.HTTPError as e:
            print(f"  {e.code} {m['page']} {suffix or '(sans suffixe)'}", flush=True)
            time.sleep(1)
    if got is None:
        continue
    data, ctype = got
    folder = out / m["page"]
    n = len(list(folder.glob("*"))) + 1 if folder.exists() else 1
    dest = folder / f"r{n:02d}.{EXT.get(ctype, 'bin')}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    m["fichier"], m["octets"] = str(dest.relative_to(out)), len(data)
    print(f"ok {dest}", flush=True)
    time.sleep(1)
(out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
print(sum(1 for m in manifest if not m["fichier"]), "échecs restants")
