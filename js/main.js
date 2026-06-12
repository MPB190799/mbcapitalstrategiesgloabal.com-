/* ============================================
   MB Capital Strategies Global
   Main JavaScript
   ============================================ */

/* Premium Polish: soft corner glows on every non-luxe-v3 sub-page.
   Font-Guard 2026-06-12: Cormorant Garamond injection removed — brand font is Outfit (design-style-guide.md).
   Cormorant was never used in css/style.css body rules, causing ~200ms wasted font-parse per sub-page. */
(function(){
  /* Font guard: ensure brand fonts Outfit + IBM Plex Mono are loaded if missing (sub-pages without preload in <head>) */
  if (!document.querySelector('link[href*="Outfit"]')) {
    var f = document.createElement('link');
    f.rel = 'stylesheet';
    f.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap';
    document.head.appendChild(f);
  }
  if (!document.documentElement.hasAttribute('data-luxe-v3') && !document.getElementById('mbcs-premium-polish')) {
    var s = document.createElement('style');
    s.id = 'mbcs-premium-polish';
    s.textContent = '.mbcs-corner-glow{position:fixed;pointer-events:none;z-index:1;opacity:.55;will-change:transform}.mbcs-corner-glow.top-right{top:-160px;right:-160px;width:520px;height:520px;background:radial-gradient(circle,rgba(212,175,55,.18),rgba(212,175,55,0) 65%);filter:blur(8px)}.mbcs-corner-glow.bottom-left{bottom:-200px;left:-200px;width:600px;height:600px;background:radial-gradient(circle,rgba(212,175,55,.12),rgba(212,175,55,0) 60%);filter:blur(10px);animation:mbcsAuroraDrift 22s ease-in-out infinite alternate}@keyframes mbcsAuroraDrift{0%{transform:translate(0,0)}100%{transform:translate(80px,-60px)}}.mbcs-mini-compass{position:fixed;right:24px;bottom:24px;width:64px;height:64px;z-index:2;opacity:.18;pointer-events:none;transition:opacity .4s ease}.mbcs-mini-compass:hover{opacity:.42}.mbcs-mini-compass svg{width:100%;height:100%;animation:mbcsCompassSpin 60s linear infinite}@keyframes mbcsCompassSpin{from{transform:rotate(0)}to{transform:rotate(360deg)}}@media(max-width:640px){.mbcs-mini-compass{display:none}}@media(prefers-reduced-motion:reduce){.mbcs-corner-glow,.mbcs-mini-compass svg{animation:none}}';
    document.head.appendChild(s);
    document.addEventListener('DOMContentLoaded', function(){
      var a=document.createElement('div');a.className='mbcs-corner-glow top-right';
      var b=document.createElement('div');b.className='mbcs-corner-glow bottom-left';
      document.body.appendChild(a);document.body.appendChild(b);
      var c=document.createElement('div');c.className='mbcs-mini-compass';c.setAttribute('aria-hidden','true');
      c.innerHTML='<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="46" fill="none" stroke="#d4af37" stroke-width="1" opacity=".7"/><circle cx="50" cy="50" r="38" fill="none" stroke="#d4af37" stroke-width=".5" opacity=".4"/><polygon points="50,8 54,50 50,58 46,50" fill="#d4af37" opacity=".9"/><polygon points="92,50 50,46 42,50 50,54" fill="#d4af37" opacity=".55"/><polygon points="50,92 46,50 50,42 54,50" fill="#d4af37" opacity=".55"/><polygon points="8,50 50,46 58,50 50,54" fill="#d4af37" opacity=".55"/><circle cx="50" cy="50" r="3.5" fill="#d4af37"/></svg>';
      document.body.appendChild(c);
    });
  }
})();

document.addEventListener('DOMContentLoaded', () => {

    // === Background Effects (Gold Waves + Aurora Orbs) ===
    if (!document.querySelector('.bg-lines')) {
        var orbs = document.createElement('div');
        orbs.className = 'bg-lines';
        orbs.innerHTML = '<span></span><span></span><span></span><span></span><span></span><span></span>';
        document.body.insertBefore(orbs, document.body.firstChild);
    }
    if (!document.querySelector('.bg-wave')) {
        var wave = document.createElement('div');
        wave.className = 'bg-wave';
        wave.innerHTML =
            '<svg viewBox="0 0 2400 1200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">' +
            '<path d="M0,600 C200,300 400,900 600,600 C800,300 1000,900 1200,600 C1400,300 1600,900 1800,600 C2000,300 2200,900 2400,600" fill="none" stroke="url(#ewg1)" stroke-width="1.5" opacity=".7"/>' +
            '<path d="M0,500 C200,250 400,750 600,500 C800,250 1000,750 1200,500 C1400,250 1600,750 1800,500 C2000,250 2200,750 2400,500" fill="none" stroke="url(#ewg1)" stroke-width="1" opacity=".3"/>' +
            '<defs><linearGradient id="ewg1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#d4af37" stop-opacity="0"/><stop offset="30%" stop-color="#d4af37" stop-opacity=".6"/><stop offset="50%" stop-color="#f0d060" stop-opacity="1"/><stop offset="70%" stop-color="#d4af37" stop-opacity=".6"/><stop offset="100%" stop-color="#d4af37" stop-opacity="0"/></linearGradient></defs>' +
            '</svg>' +
            '<svg viewBox="0 0 2400 1200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">' +
            '<path d="M0,700 C250,400 500,1000 750,700 C1000,400 1250,1000 1500,700 C1750,400 2000,1000 2250,700 C2400,550 2400,700 2400,700" fill="none" stroke="url(#ewg2)" stroke-width="1.2" opacity=".6"/>' +
            '<defs><linearGradient id="ewg2" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#e8c95a" stop-opacity="0"/><stop offset="40%" stop-color="#d4af37" stop-opacity=".8"/><stop offset="60%" stop-color="#f0d060" stop-opacity=".8"/><stop offset="100%" stop-color="#d4af37" stop-opacity="0"/></linearGradient></defs>' +
            '</svg>';
        document.body.insertBefore(wave, document.body.firstChild);
    }

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

    // Scroll Reveal for .sr elements (bento homepage)
    document.querySelectorAll('.sr').forEach(el => observer.observe(el));

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

    // === Reading Progress Bar ===
    const articleContent = document.querySelector('.page-content') || document.querySelector('.blog-post-content') || document.querySelector('article');
    if (articleContent) {
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.style.width = '0%';
        document.body.prepend(progressBar);

        window.addEventListener('scroll', () => {
            const rect = articleContent.getBoundingClientRect();
            const totalHeight = articleContent.offsetHeight;
            const scrolled = Math.max(0, -rect.top);
            const progress = Math.min(100, (scrolled / (totalHeight - window.innerHeight)) * 100);
            progressBar.style.width = progress + '%';
        }, { passive: true });
    }

    // === Back to Top Button ===
    const backToTop = document.createElement('button');
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '↑';
    backToTop.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTop);

    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    }, { passive: true });

    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // === GA4 Affiliate Click Tracking ===
    if (typeof gtag === 'function') {
        document.querySelectorAll('a[href*="everflow"], a[href*="impact.com"], a[href*="investingpro"]').forEach(function(link) {
            link.addEventListener('click', function() {
                gtag('event', 'affiliate_click', {
                    event_category: 'monetization',
                    event_label: link.href
                });
            });
        });

        // === GA4 Scroll Depth Tracking (25%, 50%, 75%, 90%) ===
        var scrollMarkers = {25: false, 50: false, 75: false, 90: false};
        window.addEventListener('scroll', function() {
            var scrollHeight = document.body.scrollHeight - window.innerHeight;
            if (scrollHeight <= 0) return;
            var pct = Math.round((window.scrollY / scrollHeight) * 100);
            [25, 50, 75, 90].forEach(function(m) {
                if (pct >= m && !scrollMarkers[m]) {
                    scrollMarkers[m] = true;
                    gtag('event', 'scroll_depth', {
                        event_category: 'engagement',
                        event_label: m + '%'
                    });
                }
            });
        }, { passive: true });
    }

});
