#!/usr/bin/env python3
"""Génère modeles/bon-cadeau.pdf : le bon cadeau à remplir, A5 paysage.

Dépendance : reportlab (pip install reportlab). Le dossier modeles/ n'est pas publié sur le site.
    python3 scripts/bon_cadeau.py
"""
import pathlib

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

RACINE = pathlib.Path(__file__).parent.parent
SORTIE = RACINE / "modeles/bon-cadeau.pdf"
FOND = HexColor("#f7f3ee")
TEXTE = HexColor("#1e1a16")
DISCRET = HexColor("#61605c")
TRAIT = HexColor("#ded5cd")
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"

pdfmetrics.registerFont(TTFont("Georgia", GEORGIA))
pdfmetrics.registerFont(TTFont("Georgia-Italique", GEORGIA.replace("Georgia.ttf", "Georgia Italic.ttf")))

LARGEUR, HAUTEUR = landscape(A5)
MARGE = 34
pdf = canvas.Canvas(str(SORTIE), pagesize=(LARGEUR, HAUTEUR))
pdf.setTitle("Bon cadeau ATTI-TUD Photo")
pdf.setAuthor("ATTI-TUD Photo")

pdf.setFillColor(FOND)
pdf.rect(0, 0, LARGEUR, HAUTEUR, stroke=0, fill=1)
pdf.setStrokeColor(TRAIT)
pdf.setLineWidth(0.8)
pdf.roundRect(14, 14, LARGEUR - 28, HAUTEUR - 28, 10, stroke=1, fill=0)

logo = ImageReader(str(RACINE / "static/logo.png"))
pdf.drawImage(logo, MARGE, HAUTEUR - 80, width=34, height=47, mask="auto")
pdf.setFillColor(TEXTE)
pdf.setFont("Helvetica-Bold", 10)
pdf.drawString(MARGE + 44, HAUTEUR - 53, "A T T I - T U D   P H O T O")
pdf.setFillColor(DISCRET)
pdf.setFont("Georgia-Italique", 11)
pdf.drawString(MARGE + 44, HAUTEUR - 68, "Calamithi")

pdf.setFillColor(TEXTE)
pdf.setFont("Georgia", 36)
pdf.drawString(MARGE, HAUTEUR - 128, "Bon cadeau")
pdf.setFillColor(DISCRET)
pdf.setFont("Georgia-Italique", 13)
pdf.drawString(MARGE, HAUTEUR - 150, "Un moment à vivre, des images à garder.")
pdf.setFont("Helvetica", 10)
pdf.drawString(MARGE, HAUTEUR - 170, "Une séance photo d'une heure, avec sa sélection de photos retouchées.")


def champ(nom, titre, x, y, largeur):
    pdf.setFillColor(DISCRET)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(x, y + 22, titre)
    pdf.acroForm.textfield(
        name=nom, tooltip=titre, x=x, y=y, width=largeur, height=20,
        fontName="Helvetica", fontSize=11, textColor=TEXTE, fillColor=None,
        borderColor=TRAIT, borderWidth=1, borderStyle="underlined", forceBorder=True,
    )


COLONNE = (LARGEUR - 2 * MARGE - 18) / 2
DROITE = MARGE + COLONNE + 18
champ("numero", "Numéro de commande", MARGE, 186, COLONNE)
champ("date_achat", "Date d'achat", DROITE, 186, COLONNE)
champ("formule", "Formule", MARGE, 144, COLONNE)
champ("ville", "Ville de la séance", DROITE, 144, COLONNE)
champ("limite", "Séance à réaliser avant le", MARGE, 102, COLONNE)

pdf.setFillColor(TEXTE)
pdf.setFont("Helvetica", 9)
pdf.drawString(MARGE, 76, "Pour réserver, contactez la photographe en indiquant le numéro de commande,")
pdf.drawString(MARGE, 63, "sans attendre le dernier moment : les disponibilités peuvent être limitées.")
pdf.setFillColor(DISCRET)
pdf.setFont("Helvetica", 8.5)
pdf.drawString(MARGE, 40, "calamithi@gmail.com  ·  06 07 47 27 65  ·  www.attitud.photo")
pdf.drawRightString(LARGEUR - MARGE, 40, "Conditions sur www.attitud.photo/cgv")

pdf.save()
print(SORTIE)
