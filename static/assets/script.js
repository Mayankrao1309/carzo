/* ========================================
   Carzo — JavaScript
   ======================================== */


function initializeApp() {

    // -------- Navbar scroll shadow --------
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    if (navbar && !navbar.classList.contains('navbar--always-white')) {
        window.addEventListener('scroll', () => {
            const currentScroll = window.scrollY;
            if (currentScroll > 10) {
                navbar.classList.add('navbar--scrolled');
            } else {
                navbar.classList.remove('navbar--scrolled');
            }
            lastScroll = currentScroll;
        }, { passive: true });
    }



    // -------- Intersection Observer for card animations --------
    const cards = document.querySelectorAll('.car-card');

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    cards.forEach(card => {
        card.style.animationPlayState = 'paused';
        observer.observe(card);
    });

    // -------- Booking bar focus interactions --------
    const bookingBar = document.getElementById('booking-bar');
    const bookingInputs = document.querySelectorAll('.booking-bar__input');

    bookingInputs.forEach(input => {
        input.addEventListener('focus', () => {
            if (bookingBar) {
                bookingBar.style.transform = 'translateY(-2px) scale(1.005)';
            }
        });
        input.addEventListener('blur', () => {
            if (bookingBar) {
                bookingBar.style.transform = 'translateY(0) scale(1)';
            }
        });
    });

    // -------- Make entire booking field clickable to open date picker --------
    const bookingFields = document.querySelectorAll('.booking-bar__field');
    bookingFields.forEach(field => {
        field.addEventListener('click', (e) => {
            // Prevent opening date picker when clicking time picker
            if (e.target.closest('.booking-bar__input--time')) {
                return;
            }
            const dateInput = field.querySelector('.booking-bar__input--date');
            if (dateInput) {
                try {
                    dateInput.showPicker();
                } catch (err) {
                    console.error("showPicker not supported or failed:", err);
                }
            }
        });
    });



    // -------- Smooth hover tilt on car cards --------
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -1.5;
            const rotateY = ((x - centerX) / centerX) * 1.5;

            card.style.transform = `translateY(-4px) perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) perspective(800px) rotateX(0) rotateY(0)';
            card.style.transition = 'transform 0.4s ease';
        });

        card.addEventListener('mouseenter', () => {
            card.style.transition = 'transform 0.15s ease';
        });
    });

    // -------- Mobile hamburger (toggle) --------
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('navbar__links--open');
            hamburger.classList.toggle('navbar__hamburger--active');
        });
    }

    // -------- Dashboard sidebar hamburger (toggle) --------
    const dashHam = document.getElementById('dashboard-hamburger-btn');
    const dashSidebar = document.querySelector('.dashboard-sidebar');
    if (dashHam && dashSidebar) {
        dashHam.addEventListener('click', (e) => {
            e.stopPropagation();
            dashSidebar.classList.toggle('dashboard-sidebar--open');
        });
        document.addEventListener('click', (e) => {
            if (!dashSidebar.contains(e.target) && !dashHam.contains(e.target)) {
                dashSidebar.classList.remove('dashboard-sidebar--open');
            }
        });
    }

    // -------- Profile dropdown & Authentication toggling logic --------

    // Toggle dropdown menu
    const profileBtn = document.getElementById('profile-btn');
    const profileMenu = document.getElementById('profile-menu');
    if (profileBtn && profileMenu) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            profileMenu.classList.toggle('navbar__profile-menu--open');
        });

        // Close menu on clicking outside
        document.addEventListener('click', (e) => {
            if (!profileMenu.contains(e.target) && !profileBtn.contains(e.target)) {
                profileMenu.classList.remove('navbar__profile-menu--open');
            }
        });
    }

    // -------- Daily Price Slider Interaction --------
    const priceSlider = document.querySelector('.price-slider');
    const priceSliderCurrent = document.querySelector('.price-slider__current');
    if (priceSlider && priceSliderCurrent) {
        priceSlider.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            // Translate slider values (e.g. 50-600) to INR (e.g. 500-20000)
            const inrVal = val * 10;
            priceSliderCurrent.textContent = `max: ₹${inrVal.toLocaleString('en-IN')}`;
        });
    }

    // -------- Responsive Bottom Navigation Position Helper --------
    const navLinksElement = document.getElementById('nav-links');
    const navbarInnerElement = document.querySelector('.navbar__inner');
    
    function handleNavPosition() {
        if (!navLinksElement) {
            console.log("handleNavPosition: navLinksElement is null");
            return;
        }
        const isMobile = window.innerWidth <= 1024 || window.matchMedia('(max-width: 1024px)').matches;
        console.log("handleNavPosition: isMobile =", isMobile, "parent =", navLinksElement.parentNode ? navLinksElement.parentNode.tagName : "none");
        if (isMobile) {
            if (navLinksElement.parentNode !== document.body) {
                document.body.appendChild(navLinksElement);
                console.log("handleNavPosition: Moved nav-links to body successfully");
            }
        } else {
            if (navbarInnerElement && navLinksElement.parentNode !== navbarInnerElement) {
                const actionsElement = navbarInnerElement.querySelector('.navbar__actions');
                if (actionsElement) {
                    navbarInnerElement.insertBefore(navLinksElement, actionsElement);
                } else {
                    navbarInnerElement.appendChild(navLinksElement);
                }
                console.log("handleNavPosition: Moved nav-links to navbar__inner successfully");
            }
        }
    }
    
    window.addEventListener('resize', handleNavPosition);
    setInterval(handleNavPosition, 200);
    handleNavPosition();

}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

