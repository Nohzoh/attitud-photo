// Calculatrice de bon cadeau de la page Offrir. Tarifs : front matter « calculateur ».
(function () {
  const form = document.querySelector('[data-calculateur]');
  if (!form) return;
  const tarifs = JSON.parse(form.dataset.tarifs);
  const champ = form.querySelector('#calc-ville');
  const liste = form.querySelector('#calc-villes');
  const payer = form.querySelector('[data-payer]');
  const message = form.querySelector('[data-message]');
  let communes = null;
  const liens = form.dataset.liens ? JSON.parse(form.dataset.liens) : null;
  let commune = null;
  let lien = null;
  let actif = -1;

  const normaliser = (texte) => texte.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[-']/g, ' ').toLowerCase();
  const euros = (montant) => montant.toLocaleString('fr-FR') + ' €';

  function chargerCommunes() {
    if (communes) return;
    communes = [];
    fetch(form.dataset.trajets).then((reponse) => reponse.json()).then((lignes) => {
      communes = lignes.map(([nom, cp, minutes]) => ({ nom, cp, minutes, cle: normaliser(nom) }));
      calculer();
    });
  }

  function chercher(texte) {
    const cle = normaliser(texte.trim());
    if (cle.length < 2) return [];
    const debut = communes.filter((c) => c.cle.startsWith(cle) || c.cp.startsWith(cle));
    const milieu = communes.filter((c) => c.cle.includes(cle) && !c.cle.startsWith(cle));
    const parProximite = (a, b) => a.minutes - b.minutes;
    return debut.sort(parProximite).concat(milieu.sort(parProximite)).slice(0, 8);
  }

  function fermerListe() {
    liste.hidden = true;
    champ.setAttribute('aria-expanded', 'false');
    champ.removeAttribute('aria-activedescendant');
    actif = -1;
  }

  function choisir(trouvee) {
    commune = trouvee;
    champ.value = trouvee.nom + ' (' + trouvee.cp + ')';
    fermerListe();
    calculer();
  }

  function afficherListe() {
    const resultats = chercher(champ.value);
    liste.replaceChildren(...resultats.map((c, i) => {
      const li = document.createElement('li');
      li.id = 'calc-ville-' + i;
      li.setAttribute('role', 'option');
      li.textContent = c.nom + ' (' + c.cp + ')';
      li.addEventListener('mousedown', (evenement) => { evenement.preventDefault(); choisir(c); });
      return li;
    }));
    liste.hidden = !resultats.length;
    champ.setAttribute('aria-expanded', resultats.length ? 'true' : 'false');
    actif = -1;
    return resultats;
  }

  function surligner(sens) {
    const options = [...liste.children];
    if (!options.length) return;
    actif = (actif + sens + options.length) % options.length;
    options.forEach((option, i) => option.setAttribute('aria-selected', i === actif ? 'true' : 'false'));
    champ.setAttribute('aria-activedescendant', options[actif].id);
  }

  function calculer() {
    const label = new FormData(form).get('personnes');
    const seance = tarifs.personnes.find((p) => p.label === label);
    const lignes = [[label + (label === '1' ? ' personne' : ' personnes') + ', ' + tarifs.duree, seance.prix]];
    // Remise des offres du moment : sur la séance seulement, pas sur le déplacement.
    const remise = Number(form.dataset.remise || 0);
    if (remise) lignes.push(['Remise de ' + remise + ' %', -Math.round(seance.prix * remise / 100)]);

    let bloque = '';
    lien = null;
    if (!commune) {
      if (champ.value.trim() && communes && communes.length && !chercher(champ.value).length) {
        bloque = 'Ville introuvable : <a href="' + form.dataset.contact + '">écrivez-moi</a> pour un devis.';
      } else {
        bloque = 'Indiquez la ville pour voir le prix total.';
      }
    } else {
      const minutes = Math.ceil(commune.minutes * (1 + tarifs.marge_trajet / 100));
      const forfait = tarifs.deplacement.find((t) => minutes <= t.max);
      if (forfait) {
        lignes.push(['Déplacement à ' + commune.nom, forfait.prix]);
        if (liens) {
          const ville = normaliser(commune.nom).replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '') + '-' + commune.cp;
          lien = liens[remise ? 'remise' : 'normal'][label][forfait.prix] + '?client_reference_id=' + ville;
        }
      } else {
        bloque = 'Pour ' + commune.nom + ', le déplacement se fait sur devis : <a href="' + form.dataset.contact + '">écrivez-moi</a>.';
      }
    }

    const total = lignes.reduce((somme, ligne) => somme + ligne[1], 0);
    form.querySelector('[data-total]').textContent = bloque ? 'À partir de ' + euros(total) : euros(total);
    form.querySelector('[data-lignes]').replaceChildren(...[[seance.photos + ' photos', null], ...lignes].map(([texte, prix]) => {
      const li = document.createElement('li');
      li.textContent = texte;
      if (prix !== null) {
        const montant = document.createElement('span');
        montant.textContent = prix === 0 ? 'Offert' : prix < 0 ? '− ' + euros(-prix) : euros(prix);
        li.append(montant);
      }
      return li;
    }));
    message.hidden = !bloque;
    message.innerHTML = bloque;
    payer.classList.toggle('calc-inactif', Boolean(bloque));
    payer.setAttribute('aria-disabled', bloque ? 'true' : 'false');
    payer.href = lien || '#paiement';
    payer.textContent = bloque ? 'Offrir ce bon' : 'Offrir ce bon · ' + euros(total);
  }

  form.addEventListener('change', calculer);
  form.addEventListener('submit', (evenement) => evenement.preventDefault());
  champ.addEventListener('focus', chargerCommunes);
  champ.addEventListener('input', () => { commune = null; afficherListe(); calculer(); });
  champ.addEventListener('blur', fermerListe);
  champ.addEventListener('keydown', (evenement) => {
    if (evenement.key === 'ArrowDown') { evenement.preventDefault(); surligner(1); }
    if (evenement.key === 'ArrowUp') { evenement.preventDefault(); surligner(-1); }
    if (evenement.key === 'Escape') fermerListe();
    if (evenement.key === 'Enter') {
      evenement.preventDefault();
      const resultats = chercher(champ.value);
      if (resultats.length) choisir(resultats[Math.max(actif, 0)]);
    }
  });
  payer.addEventListener('click', (evenement) => {
    if (!lien) evenement.preventDefault();
  });
  calculer();
})();
