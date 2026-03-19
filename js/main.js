/* ============================================
   MB Capital Strategies Global
   Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // === Navbar Scroll Effect ===
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    let scrollTicking = false;
    window.addEventListener('scroll', () => {
        if (!scrollTicking) {
            window.requestAnimationFrame(() => {
                const currentScroll = window.scrollY;
                if (currentScroll > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
                lastScroll = currentScroll;
                scrollTicking = false;
            });
            scrollTicking = true;
        }
    });

    // === Mobile Navigation ===
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        });

        // Close menu on link click
        navMenu.querySelectorAll('.nav-link:not(.dropdown-toggle)').forEach(link => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Mobile dropdown toggle
        navMenu.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    var dropdown = toggle.closest('.dropdown');
                    if (dropdown) dropdown.classList.toggle('active');
                }
            });
        });
    }

    // === FAQ Accordion ===
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', () => {
            const item = question.closest('.faq-item');
            const isActive = item.classList.contains('active');

            // Close all
            document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));

            // Toggle clicked
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // === Scroll Animations ===
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Animate cards, section headers
    document.querySelectorAll(
        '.glass-card, .section-header, .about-philosophy, .hero-stats, .hero-cta'
    ).forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });

    // === Newsletter Form ===
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = newsletterForm.querySelector('.form-input');
            if (input && input.value) {
                const btn = newsletterForm.querySelector('.btn');
                if (btn) {
                    btn.textContent = 'Subscribed!';
                    btn.style.background = '#28a745';
                    input.value = '';
                    setTimeout(() => {
                        btn.textContent = 'Subscribe Free';
                        btn.style.background = '';
                    }, 3000);
                }
            }
        });
    }

    // === Smooth scroll for anchor links ===
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // === Cookie Consent Banner ===
    const cookieBanner = document.getElementById('cookieBanner');
    if (cookieBanner && !localStorage.getItem('cookie_consent')) {
        cookieBanner.classList.add('show');
    }

    const cookieAccept = document.getElementById('cookieAccept');
    const cookieReject = document.getElementById('cookieReject');

    if (cookieAccept) {
        cookieAccept.addEventListener('click', () => {
            localStorage.setItem('cookie_consent', 'accepted');
            if (cookieBanner) cookieBanner.classList.remove('show');
        });
    }

    if (cookieReject) {
        cookieReject.addEventListener('click', () => {
            localStorage.setItem('cookie_consent', 'rejected');
            if (cookieBanner) cookieBanner.classList.remove('show');
            // Disable GA4 if rejected
            window['ga-disable-G-FSW7J7QYL8'] = true;
        });
    }

    // Block GA4 if previously rejected
    if (localStorage.getItem('cookie_consent') === 'rejected') {
        window['ga-disable-G-FSW7J7QYL8'] = true;
    }

});
