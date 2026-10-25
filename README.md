# attitud.photo

Site de Calamithi (ATTI-TUD Photo), photographe à Fontenay-sous-Bois. Site statique [Hugo](https://gohugo.io) publié sur GitHub Pages à chaque modification de la branche `main`.

## Organisation

| Dossier | Contenu |
| --- | --- |
| `content/_index.md` | Texte de la page d'accueil |
| `content/selection/` | Photos de l'accueil : la première sert d'image d'ouverture, les suivantes de sélection |
| `content/portraits/`, `mariages/`, `spectacles/` | Une rubrique par prestation : texte et formules dans `_index.md`. Les photos posées à côté illustrent la page : la première sert de bandeau, les suivantes s'affichent sous le texte |
| `content/<rubrique>/<galerie>/` | Une galerie = un dossier avec un `index.md` et ses photos |
| `content/regard-dartiste/` | Texte et photos de la page artistique |
| `content/a-propos/`, `contact/`, `mentions-legales/` | Pages fixes |
| `data/temoignages.yaml` | Avis clients et rubriques où ils apparaissent |
| `hugo.toml` | Nom du site, coordonnées, réseaux sociaux, menu |

## Ajouter une galerie

1. Créer un dossier, par exemple `content/portraits/famille-au-parc/`.
2. Y mettre un `index.md` :

   ```yaml
   ---
   title: "Famille au parc"
   sous_titre: "Une séance d'automne au bois de Vincennes"
   weight: 60
   ---
   Deux ou trois lignes sur la séance (facultatif).
   ```

3. Y déposer les photos. Elles s'affichent dans l'ordre des noms de fichiers (`01.jpg`, `02.jpg`…) ; la première sert de couverture, sauf si `couverture: "nom.jpg"` est indiqué.

Depuis le site de GitHub : ouvrir le dossier de la rubrique, puis « Add file › Upload files ».

## Placer une photo à côté d'un paragraphe

Sur une page fixe (comme `content/a-propos/index.md`), encadrer le paragraphe avec le nom de la photo qui l'illustre :

```markdown
{{< illustration photo="02.jpg" alt="Description de la photo" >}}
## Titre du paragraphe

Texte du paragraphe.
{{< /illustration >}}
```

Les photos alternent à droite et à gauche du texte (sous le texte sur mobile). Une photo à côté du titre de la page s'indique dans l'en-tête avec `photo_entete: "01.jpg"`. Dès qu'une page utilise `illustration`, la galerie en bas de page disparaît : chaque photo doit donc être placée.

## Préparer les photos

Exporter en JPEG, **2 400 pixels sur le côté le plus long**, qualité 85 (environ 400 à 700 Ko par photo). Hugo fabrique lui-même les versions plus petites (WebP 800, 1 600 et 2 400 px) : ne jamais déposer de fichiers RAW ni d'originaux pleine définition, le dépôt grossirait inutilement.

Les photos actuelles ont été reprises de l'ancien site Google Sites (2 048 px au plus) ; les remplacer par les exports originaux en 2 400 px quand ils sont disponibles.

## Travailler en local

```bash
hugo server
```

Puis ouvrir http://localhost:1313. La première construction est lente (traitement des images), les suivantes réutilisent le dossier `resources/`.

## Anciennes adresses

Les adresses de l'ancien site Google Sites (`/portraits-souvenirs`, `/leyla`, `/cléo-bataille`…) sont déclarées dans le champ `aliases` des pages concernées et redirigent vers les nouvelles.

## Droits

Les photographies et textes sont la propriété de Calamithi, tous droits réservés ; le code du site est sous licence MIT. Voir [LICENSE.md](LICENSE.md).
