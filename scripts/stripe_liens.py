#!/usr/bin/env python3
"""Crée dans Stripe les articles et les liens de paiement des bons cadeaux, puis écrit data/stripe_liens.json.

À lancer dans son propre terminal : la clé est demandée sans s'afficher et n'est enregistrée nulle part.
    python3 scripts/stripe_liens.py

Une clé de test (sk_test_, rk_test_) travaille en mode test, une clé réelle dans le compte réel.
Le script ne touche qu'à ses propres articles et liens, et ne supprime rien : on peut le relancer sans doublons.
Un lien existant sans facture ou avec un champ personnalisé est mis à jour, son adresse ne change pas.
"""
import getpass
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.stripe.com/v1"
SORTIE = pathlib.Path(__file__).parent.parent / "data/stripe_liens.json"
MERCI = "https://www.attitud.photo/merci/"
REMISE = 10
FACTURE = {
    "invoice_creation[enabled]": "true",
    "invoice_creation[invoice_data][footer]": "TVA non applicable, article 293 B du CGI.",
}
# Mêmes valeurs que data/bon_cadeau.yaml.
FORMULES = [
    {"id": "individuel", "nom": "Bon cadeau Individuel", "label": "1", "prix": 180, "photos": 15},
    {"id": "duo", "nom": "Bon cadeau Duo", "label": "2", "prix": 220, "photos": 20},
    {"id": "groupe", "nom": "Bon cadeau Groupe (3 à 5 personnes)", "label": "3 à 5", "prix": 280, "photos": 30},
]
FORFAITS = [0, 15, 25, 40]
PRODUIT_DEPLACEMENT = "bon_cadeau_deplacement"


def stripe(cle, methode, chemin, donnees=None):
    corps = urllib.parse.urlencode(donnees or {}).encode()
    url = API + chemin
    if methode == "GET" and donnees:
        url, corps = url + "?" + corps.decode(), None
    requete = urllib.request.Request(url, data=corps if methode == "POST" else None, method=methode)
    requete.add_header("Authorization", "Bearer " + cle)
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return json.load(reponse)
    except urllib.error.HTTPError as erreur:
        if erreur.code == 404 and methode == "GET":
            return None
        message = json.load(erreur).get("error", {}).get("message", "")
        sys.exit(f"Erreur Stripe ({erreur.code}) sur {chemin} : {message}")


def produit(cle, identifiant, nom, description):
    if stripe(cle, "GET", "/products/" + identifiant):
        return
    stripe(cle, "POST", "/products", {"id": identifiant, "name": nom, "description": description})
    print("Article créé :", nom)


def prix(cle, cle_recherche, identifiant_produit, euros, surnom):
    existants = stripe(cle, "GET", "/prices", {"lookup_keys[]": cle_recherche, "active": "true"})["data"]
    if existants:
        return existants[0]["id"]
    return stripe(cle, "POST", "/prices", {
        "product": identifiant_produit,
        "currency": "eur",
        "unit_amount": euros * 100,
        "nickname": surnom,
        "lookup_key": cle_recherche,
    })["id"]


def liens_existants(cle):
    liens = {}
    parametres = {"active": "true", "limit": 100}
    while True:
        page = stripe(cle, "GET", "/payment_links", parametres)
        for lien in page["data"]:
            if "cle" in lien.get("metadata", {}):
                liens[lien["metadata"]["cle"]] = lien
        if not page["has_more"]:
            return liens
        parametres["starting_after"] = page["data"][-1]["id"]


def creer_lien(cle, identifiant, formule, forfait, remise, prix_seance, prix_deplacement):
    donnees = {
        "line_items[0][price]": prix_seance,
        "line_items[0][quantity]": 1,
        "after_completion[type]": "redirect",
        "after_completion[redirect][url]": MERCI,
        "metadata[cle]": identifiant,
        **FACTURE,
    }
    informations = {"formule": formule["nom"], "forfait_deplacement": forfait, "remise": remise}
    for nom, valeur in informations.items():
        donnees[f"metadata[{nom}]"] = valeur
        donnees[f"payment_intent_data[metadata][{nom}]"] = valeur
    if forfait:
        donnees["line_items[1][price]"] = prix_deplacement[forfait]
        donnees["line_items[1][quantity]"] = 1
    return stripe(cle, "POST", "/payment_links", donnees)["url"]


def creer_tout(cle):
    produit(cle, PRODUIT_DEPLACEMENT, "Forfait de déplacement", "Selon le temps de trajet depuis Fontenay-sous-Bois.")
    prix_deplacement = {
        forfait: prix(cle, f"bon_deplacement_{forfait}", PRODUIT_DEPLACEMENT, forfait, f"Déplacement {forfait} €")
        for forfait in FORFAITS if forfait
    }
    existants = liens_existants(cle)
    resultat = {"normal": {}, "remise": {}}
    for formule in FORMULES:
        identifiant_produit = "bon_cadeau_" + formule["id"]
        produit(cle, identifiant_produit, formule["nom"], f"Séance photo d'une heure, {formule['photos']} photos.")
        for type_prix, remise in (("normal", 0), ("remise", REMISE)):
            euros = formule["prix"] - formule["prix"] * remise // 100
            prix_seance = prix(cle, f"bon_{formule['id']}_{type_prix}", identifiant_produit, euros, f"{euros} € ({type_prix})")
            colonne = resultat[type_prix].setdefault(formule["label"], {})
            for forfait in FORFAITS:
                identifiant = f"bon_{formule['id']}_{type_prix}_{forfait}"
                lien = existants.get(identifiant)
                if not lien:
                    url = creer_lien(cle, identifiant, formule, forfait, remise, prix_seance, prix_deplacement)
                    print("Lien créé :", identifiant)
                else:
                    url = lien["url"]
                    if not lien.get("invoice_creation", {}).get("enabled") or lien.get("custom_fields"):
                        stripe(cle, "POST", "/payment_links/" + lien["id"], {**FACTURE, "custom_fields": ""})
                        print("Lien mis à jour :", identifiant)
                colonne[str(forfait)] = url
    return resultat


def main():
    cle = getpass.getpass("Clé Stripe (invisible à la saisie) : ").strip()
    if not cle.startswith(("sk_", "rk_")):
        sys.exit("Ce n'est pas une clé secrète ou restreinte Stripe.")
    test = "_test_" in cle
    if not test and input("Clé RÉELLE : créer les articles et les liens dans le vrai compte ? (oui/non) ").strip().lower() != "oui":
        sys.exit("Annulé.")
    resultat = creer_tout(cle)
    resultat["mode"] = "test" if test else "réel"
    SORTIE.write_text(json.dumps(resultat, ensure_ascii=False, indent=2) + "\n")
    print(f"Terminé en mode {resultat['mode']} : {SORTIE}")


if __name__ == "__main__":
    main()
