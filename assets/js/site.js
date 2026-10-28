// Menu mobile et visionneuse plein écran des galeries. Aucune dépendance.
document.documentElement.classList.remove('no-js');

// Boucles vidéo muettes : lancées seulement si le visiteur n'a pas désactivé les animations.
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.querySelectorAll('video[data-boucle]').forEach((video) => {
    video.preload = 'auto';
    video.play().catch(() => {});
  });
}

(function () {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', () => {
      const open = header.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  const dialog = document.querySelector('[data-lightbox]');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const img = dialog.querySelector('img');
  const count = dialog.querySelector('.lightbox-count');
  let items = [];
  let current = 0;

  const show = (i) => {
    current = (i + items.length) % items.length;
    const link = items[current];
    img.src = link.href;
    img.alt = link.querySelector('img')?.alt || '';
    count.textContent = `${current + 1} / ${items.length}`;
    // Précharge la photo suivante pour un défilement fluide.
    new Image().src = items[(current + 1) % items.length].href;
  };

  document.querySelectorAll('[data-gallery]').forEach((gallery) => {
    const links = Array.from(gallery.querySelectorAll('a.gallery-item'));
    links.forEach((link, i) => {
      link.addEventListener('click', (event) => {
        if (event.metaKey || event.ctrlKey || event.shiftKey) return;
        event.preventDefault();
        items = links;
        show(i);
        dialog.showModal();
      });
    });
  });

  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-prev]').addEventListener('click', () => show(current - 1));
  dialog.querySelector('[data-next]').addEventListener('click', () => show(current + 1));
  dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => { img.removeAttribute('src'); });
  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') show(current - 1);
    if (event.key === 'ArrowRight') show(current + 1);
  });

  // Balayage tactile gauche / droite.
  let startX = null;
  dialog.addEventListener('touchstart', (event) => { startX = event.touches[0].clientX; }, { passive: true });
  dialog.addEventListener('touchend', (event) => {
    if (startX === null) return;
    const dx = event.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
    startX = null;
  });
})();
