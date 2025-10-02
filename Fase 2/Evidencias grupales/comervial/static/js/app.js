// Navbar transparente → blanco al scrollear
(function(){
  const nav = document.getElementById('mainNav');
  if(!nav) return;
  const onScroll = () => {
    if (window.scrollY > 10) {
      nav.classList.add('navbar-scrolled');
      nav.classList.remove('navbar-initial');
    } else {
      nav.classList.add('navbar-initial');
      nav.classList.remove('navbar-scrolled');
    }
  };
  onScroll();
  document.addEventListener('scroll', onScroll, { passive: true });
})();

const nav = document.getElementById('mainNav');
const logo = document.getElementById('brandLogo');

function onScroll() {
  if (window.scrollY > 10) {
    nav.classList.add('scrolled');       // tu clase que pone fondo blanco
    nav.classList.remove('navbar-dark');
    nav.classList.add('navbar-light');   // para que el toggler se vea en fondo blanco
    if (logo) logo.src = '/static/img/comervial-logo-dark.png';
  } else {
    nav.classList.remove('scrolled');
    nav.classList.add('navbar-dark');
    nav.classList.remove('navbar-light');
    if (logo) logo.src = '/static/img/comervial-logo-light.png';
  }
}
window.addEventListener('scroll', onScroll);
onScroll();

