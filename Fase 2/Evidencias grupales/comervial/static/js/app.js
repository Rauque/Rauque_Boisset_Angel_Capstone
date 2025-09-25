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
