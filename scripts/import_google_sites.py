"""Télécharge les images de l'ancien site Google Sites, page par page, en pleine définition.

Usage : python3 scripts/import_google_sites.py [dossier_de_sortie]
Résultat : <sortie>/<page>/NN.<ext> et <sortie>/manifest.json (page, ordre, URL source).
Les images présentes sur au moins 3 pages (logo, icônes) sont rangées dans <sortie>/_commun.
"""
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SITE = "https://www.attitud.photo/"
PAGES = [
    "accueil", "portraits-souvenirs", "mariages", "spectacles-evenements", "regard-dartiste",
    "un-peu-de-moi", "temoignages", "contact",
    "leyla", "sylvie-poupé", "comédiens", "cécile", "laura",
    "mariage-thaïri-zahir", "mariage-angélique", "mariage-pauline",
    "cléo-bataille", "prince-des-poètes", "festival-infatigables", "disparitions2",
    "chantal-de-mage", "evenements-publics",
]
IMG = re.compile(r"https://lh\d+-\w+\.googleusercontent\.com/sitesv-images-rt/[A-Za-z0-9_\-]+")
EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif"}
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read(), r.headers.get_content_type()


def download(u):
    """Plus grande taille disponible ; None si Google refuse toutes les variantes."""
    for suffix in ("=s0", "=w16383", "=w2400", "=w1280"):
        for attempt in range(3):
            try:
                return get(u + suffix)
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    time.sleep(5 * (attempt + 1))
                    continue
                break
    return None


def main(out):
    out = pathlib.Path(out)
    found = {}
    for page in PAGES:
        html, _ = get(SITE + urllib.parse.quote(page))
        urls = list(dict.fromkeys(IMG.findall(html.decode("utf-8", "replace"))))
        found[page] = urls
        print(f"{page}: {len(urls)} images", flush=True)

    counts = {}
    for urls in found.values():
        for u in urls:
            counts[u] = counts.get(u, 0) + 1

    manifest = []
    for page, urls in found.items():
        n = 0
        for u in urls:
            folder = "_commun" if counts[u] >= 3 else page
            if folder == "_commun" and any(m["source"] == u for m in manifest):
                continue
            got = download(u)
            if got is None:
                print(f"  échec : {page} {u}", flush=True)
                manifest.append({"page": page, "fichier": None, "source": u, "octets": 0})
                continue
            data, ctype = got
            n += 1
            dest = out / folder / f"{n if folder != '_commun' else len(manifest) + 1:02d}.{EXT.get(ctype, 'bin')}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            manifest.append({"page": page, "fichier": str(dest.relative_to(out)), "source": u, "octets": len(data)})
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    ok = [m for m in manifest if m["fichier"]]
    print(f"{len(ok)} images sur {len(manifest)}, {sum(m['octets'] for m in ok) / 1e6:.1f} Mo")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "import")
