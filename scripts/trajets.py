#!/usr/bin/env python3
"""Génère assets/data/trajets.json : temps de trajet en voiture depuis le studio
vers chaque commune d'Île-de-France et chaque arrondissement de Paris.

Sources publiques, sans clé : geo.api.gouv.fr et le calcul d'itinéraire de l'IGN.
Durées sans trafic. À relancer seulement si la liste doit être recalculée :
    python3 scripts/trajets.py
"""
import json
import math
import pathlib
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

STUDIO = (2.470571, 48.85433)  # 10 avenue Victor Hugo, Fontenay-sous-Bois
DEPARTEMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]
SORTIE = pathlib.Path(__file__).parent.parent / "assets/data/trajets.json"
# Reprise après une interruption : les durées déjà obtenues sont gardées ici.
CACHE = pathlib.Path(tempfile.gettempdir()) / "attitud-trajets-cache.json"
# Quand le centre d'une commune n'est pas relié à la route (forêt, champ), on essaie autour.
DECALAGES = [(0, 0)] + [(dx * pas, dy * pas) for pas in (0.005, 0.01, 0.02) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
GEO = "https://geo.api.gouv.fr"
ROUTE = "https://data.geopf.fr/navigation/itineraire"
CHAMPS = "fields=nom,code,centre,codesPostaux&format=json"


def lire(url):
    for essai in range(5):
        try:
            with urllib.request.urlopen(url, timeout=30) as reponse:
                return json.load(reponse)
        except urllib.error.HTTPError as erreur:
            if erreur.code == 404:
                return None
            time.sleep(2 * (essai + 1))
        except OSError:
            time.sleep(2 * (essai + 1))
    raise RuntimeError(url)


def minutes(destination):
    for dx, dy in DECALAGES:
        parametres = {
            "resource": "bdtopo-valhalla",
            "start": "%f,%f" % STUDIO,
            "end": "%f,%f" % (destination[0] + dx, destination[1] + dy),
            "profile": "car",
            "optimization": "fastest",
            "timeUnit": "minute",
            "getSteps": "false",
            "getBbox": "false",
        }
        trajet = lire(ROUTE + "?" + urllib.parse.urlencode(parametres))
        if trajet:
            return math.ceil(trajet["duration"])
    raise RuntimeError(destination)


def communes():
    for departement in DEPARTEMENTS:
        if departement != "75":
            yield from lire(f"{GEO}/departements/{departement}/communes?{CHAMPS}")
    yield from lire(f"{GEO}/communes?codeDepartement=75&type=arrondissement-municipal&{CHAMPS}")


cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
lignes = []
for commune in communes():
    nom = commune["nom"].replace(" Arrondissement", "")
    if commune["code"] not in cache:
        cache[commune["code"]] = minutes(commune["centre"]["coordinates"])
        CACHE.write_text(json.dumps(cache))
        time.sleep(0.2)
    lignes.append([nom, commune["codesPostaux"][0], cache[commune["code"]]])
    if len(lignes) % 100 == 0:
        print(len(lignes), flush=True)

lignes.sort(key=lambda ligne: ligne[0])
SORTIE.write_text(json.dumps(lignes, ensure_ascii=False, separators=(",", ":")))
print(len(lignes), "communes")
