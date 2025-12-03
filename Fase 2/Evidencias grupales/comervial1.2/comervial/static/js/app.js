// Navbar: oscuro en home (transparente) y claro al scrollear.
// En el resto de páginas, siempre claro desde arriba.
(function () {
  const nav = document.getElementById('mainNav');
  if (!nav) return;

  // soporta data-is-home="1" (nuevo) y data-home="1" (por si quedó del anterior)
  const isHome =
    nav.dataset.isHome === '1' || nav.dataset.home === '1';

  const logo = document.getElementById('brandLogo');
  const lightLogo = logo ? (logo.dataset.light || '/static/img/comervial-logo-light.png') : null;
  const darkLogo  = logo ? (logo.dataset.dark  || '/static/img/comervial-logo-dark.png')  : null;

  function setInitial() {
    nav.classList.add('navbar-initial', 'navbar-dark');
    nav.classList.remove('navbar-scrolled', 'navbar-light');
    if (logo && lightLogo) logo.src = lightLogo;
  }

  function setScrolled() {
    nav.classList.add('navbar-scrolled', 'navbar-light');
    nav.classList.remove('navbar-initial', 'navbar-dark');
    if (logo && darkLogo) logo.src = darkLogo;
  }

  if (isHome) {
    const onScroll = () => (window.scrollY > 10 ? setScrolled() : setInitial());
    onScroll(); // estado correcto al cargar
    window.addEventListener('scroll', onScroll, { passive: true });
  } else {
    // páginas no-home: navbar claro desde arriba, logo oscuro
    setScrolled();
  }
})();
