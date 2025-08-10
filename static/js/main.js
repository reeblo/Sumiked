//integracion del navbar y footer
fetch('navbar.html').then(r => r.text()).then(t => document.getElementById('navbar-include').innerHTML = t);
fetch('footer.html').then(r => r.text()).then(t => document.getElementById('footer-include').innerHTML = t);

//funciones en el navbar
// Script para manejar el submenú del dropdown
document.querySelectorAll('.dropdown-submenu > a').forEach(function(element){
    element.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        let submenu = this.nextElementSibling;
        if(submenu) {
            submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
        }
    });
});

// Cerrar menú al hacer click en un enlace en móviles
document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    link.addEventListener('click', () => {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (navbarCollapse.classList.contains('show')) {
            const bsCollapse = new bootstrap.Collapse(navbarCollapse);
            bsCollapse.hide();
        }
    });
});

// Asegurar que los dropdowns funcionen en móvil
document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', function(e) {
        if (window.innerWidth < 992) {
            e.preventDefault();
            const dropdown = this.nextElementSibling;
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        }
    });
});

// funciones inicio
// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Efecto parallax para el hero section
window.addEventListener('scroll', function() {
    const hero = document.querySelector('.hero-section');
    if (hero) {
        const scrollPosition = window.pageYOffset;
        hero.style.backgroundPositionY = scrollPosition * 0.5 + 'px';
    }
});