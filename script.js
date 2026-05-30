/* ========================================
   Carzo — JavaScript
   ======================================== */


// Migrate existing local storage data to support four images
(function() {
    try {
        let cars = localStorage.getItem('Carzo_cars');
        if (cars) {
            let parsed = JSON.parse(cars);
            let updated = false;
            if (Array.isArray(parsed)) {
                parsed.forEach(c => {
                    if (!c.hasOwnProperty('image2')) { c.image2 = ''; updated = true; }
                    if (!c.hasOwnProperty('image3')) { c.image3 = ''; updated = true; }
                    if (!c.hasOwnProperty('image4')) { c.image4 = ''; updated = true; }
                });
                if (updated) {
                    localStorage.setItem('Carzo_cars', JSON.stringify(parsed));
                }
            }
        }
    } catch(e) {
        console.error("Migration error:", e);
    }
})();

document.addEventListener('DOMContentLoaded', () => {

    // -------- Dynamic Navbar Logo and Admin Link Update --------
    const logoEl = document.getElementById('logo');
    if (logoEl) {
        const isAdminPage = window.location.pathname.includes('admin.html');
        logoEl.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; width: 42px; height: 42px; border-radius: 8px; overflow: hidden; flex-shrink: 0;">
                <img src="logo.png" alt="Carzo" style="max-width: 100%; max-height: 100%; object-fit: contain;">
            </div>
            <span class="navbar__logo-text" style="font-weight: 800; font-size: 1.4rem; letter-spacing: -0.02em; display: inline-flex; align-items: center; text-decoration: none;">
                Carzo
                ${isAdminPage ? '<span style="font-size:0.75rem; font-weight:700; background:rgba(0,0,0,0.06); padding:2px 8px; border-radius:100px; margin-left:8px; vertical-align:middle; color:var(--color-primary)">Admin</span>' : ''}
            </span>
        `;
        logoEl.style.display = 'flex';
        logoEl.style.alignItems = 'center';
        logoEl.style.gap = '8px';
        logoEl.style.textDecoration = 'none';
    }

    const profileMenu = document.getElementById('profile-menu');
    if (profileMenu && !profileMenu.querySelector('a[href="admin.html"]')) {
        const divider = profileMenu.querySelector('.navbar__profile-divider');
        if (divider) {
            const adminLink = document.createElement('a');
            adminLink.href = 'admin.html';
            adminLink.className = 'navbar__profile-item';
            adminLink.style.color = 'var(--color-primary)';
            adminLink.style.fontWeight = '700';
            adminLink.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                </svg>
                Admin Panel
            `;
            divider.parentNode.insertBefore(adminLink, divider.nextSibling);
        }
    }

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

    // -------- Location pills toggle --------
    const pills = document.querySelectorAll('.hero__pill');
    const whereInput = document.getElementById('where-input');

    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('hero__pill--active'));
            pill.classList.add('hero__pill--active');

            // Update destination input value based on clicked pill
            if (whereInput) {
                whereInput.value = pill.textContent.trim();
            }
        });
    });

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

    // -------- Booking bar date-time selection automation --------
    const datetimeFields = document.querySelectorAll('.booking-bar__field');
    datetimeFields.forEach(field => {
        const dateInput = field.querySelector('.booking-bar__input--date');
        const timeInput = field.querySelector('.booking-bar__input--time');
        
        if (dateInput) {
            // Clicking the field wrapper or its icons/labels triggers the date picker
            field.addEventListener('click', (e) => {
                // Ignore clicks directly inside date/time inputs to allow normal default interactions
                if (e.target === dateInput || e.target === timeInput) {
                    return;
                }
                
                e.stopPropagation();
                try {
                    if (typeof dateInput.showPicker === 'function') {
                        dateInput.showPicker();
                    } else {
                        dateInput.focus();
                    }
                } catch (err) {
                    console.error("Failed to show date picker:", err);
                    dateInput.focus();
                }
            });

            // Automatically trigger the time picker once the date value is selected
            if (timeInput) {
                dateInput.addEventListener('change', () => {
                    if (dateInput.value) {
                        setTimeout(() => {
                            try {
                                if (typeof timeInput.showPicker === 'function') {
                                    timeInput.showPicker();
                                } else {
                                    timeInput.focus();
                                }
                            } catch (err) {
                                console.error("Failed to show time picker:", err);
                                timeInput.focus();
                            }
                        }, 250); // 250ms delay for seamless transitions after the calendar drawer closes
                    }
                });
            }
        }
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

    // -------- Mobile hamburger (sidebar panel) --------
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');

    // Create backdrop overlay dynamically
    let overlay = document.getElementById('navbar-overlay');
    if (navLinks && !overlay) {
        overlay = document.createElement('div');
        overlay.id = 'navbar-overlay';
        overlay.className = 'navbar__overlay';
        document.body.appendChild(overlay);
    }

    function closeNav() {
        if (!navLinks || !hamburger) return;
        navLinks.classList.remove('navbar__links--open');
        hamburger.classList.remove('navbar__hamburger--active');
        if (overlay) overlay.classList.remove('navbar__overlay--open');
        document.body.classList.remove('nav-open');
    }

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = navLinks.classList.toggle('navbar__links--open');
            hamburger.classList.toggle('navbar__hamburger--active', isOpen);
            if (overlay) overlay.classList.toggle('navbar__overlay--open', isOpen);
            document.body.classList.toggle('nav-open', isOpen);
        });

        navLinks.querySelectorAll('.navbar__link').forEach(link => {
            link.addEventListener('click', closeNav);
        });

        if (overlay) {
            overlay.addEventListener('click', closeNav);
        }

        document.addEventListener('click', (e) => {
            if (navLinks.classList.contains('navbar__links--open') &&
                !navLinks.contains(e.target) && !hamburger.contains(e.target)) {
                closeNav();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeNav();
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
    // Seeding mock databases in localStorage if not present
    if (!localStorage.getItem('Carzo_cars')) {
        const defaultCars = [
            {
                id: "mitsubishi_white",
                name: "Mitsubishi Lancer",
                carName: "Mitsubishi",
                priceDay: 3000,
                priceMonth: 75000,
                passengers: 4,
                mileage: "12 km/l",
                fuelType: "Petrol",
                category: "Luxury",
                subcategory: "Sports Sedan",
                ownerName: "Rohan Pune-Owner",
                ownerPhone: "+91 90110 12345",
                available: true,
                image: "mitsubishi_white.png",
                image2: "mitsubishi_red.png",
                image3: "mitsubishi_white.png",
                image4: "mitsubishi_red.png",
                isPlaceholder: false
            },
            {
                id: "mitsubishi_red",
                name: "Mitsubishi Lancer Sport",
                carName: "Mitsubishi",
                priceDay: 5000,
                priceMonth: 95000,
                passengers: 4,
                mileage: "11 km/l",
                fuelType: "CNG",
                category: "Luxury",
                subcategory: "Premium Coupe",
                ownerName: "Aditya Shah",
                ownerPhone: "+91 98224 87654",
                available: true,
                image: "mitsubishi_red.png",
                image2: "mitsubishi_white.png",
                image3: "mitsubishi_red.png",
                image4: "mitsubishi_white.png",
                isPlaceholder: false
            },
            {
                id: "jeep_gray",
                name: "Jeep Wrangler",
                carName: "Jeep",
                priceDay: 2500,
                priceMonth: 65000,
                passengers: 4,
                mileage: "8 km/l",
                fuelType: "Diesel",
                category: "SUV",
                subcategory: "Offroad SUV",
                ownerName: "Vikram Kothrud-Owner",
                ownerPhone: "+91 94220 98765",
                available: true,
                image: "jeep_gray.png",
                image2: "jeep_gray.png",
                image3: "jeep_gray.png",
                image4: "jeep_gray.png",
                isPlaceholder: false
            },
            {
                id: "rangerover_black",
                name: "Range Rover Sport",
                carName: "Range Rover",
                priceDay: 4500,
                priceMonth: 120000,
                passengers: 5,
                mileage: "7 km/l",
                fuelType: "Petrol",
                category: "SUV",
                subcategory: "Premium SUV",
                ownerName: "Sanjay Hadapsar-Owner",
                ownerPhone: "+91 98810 54321",
                available: true,
                image: "rangerover_black.png",
                image2: "rangerover_black.png",
                image3: "rangerover_black.png",
                image4: "rangerover_black.png",
                isPlaceholder: false
            },
            {
                id: "tesla_blue",
                name: "Tesla Model Y",
                carName: "Tesla",
                priceDay: 3500,
                priceMonth: 90000,
                passengers: 5,
                mileage: "450 km range",
                fuelType: "Electric",
                category: "Electric",
                subcategory: "Electric SUV",
                ownerName: "Amit Viman-Owner",
                ownerPhone: "+91 90112 34567",
                available: true,
                image: "tesla_blue.png",
                image2: "tesla_blue.png",
                image3: "tesla_blue.png",
                image4: "tesla_blue.png",
                isPlaceholder: false
            },
            {
                id: "mustang_yellow",
                name: "Ford Mustang GT",
                carName: "Mustang",
                priceDay: 4000,
                priceMonth: 110000,
                passengers: 4,
                mileage: "6 km/l",
                fuelType: "Petrol",
                category: "Luxury",
                subcategory: "Premium Coupe",
                ownerName: "Nisha Baner-Owner",
                ownerPhone: "+91 98901 12345",
                available: true,
                image: "mustang_yellow.png",
                image2: "mustang_yellow.png",
                image3: "mustang_yellow.png",
                image4: "mustang_yellow.png",
                isPlaceholder: false
            },
            {
                id: "subaru_forester",
                name: "Subaru Forester Premium",
                carName: "Subaru",
                priceDay: 4000,
                priceMonth: 90000,
                passengers: 5,
                mileage: "10 km/l",
                fuelType: "Petrol",
                category: "SUV",
                subcategory: "Premium SUV",
                ownerName: "Vijay Kalyani-Owner",
                ownerPhone: "+91 99234 56789",
                available: true,
                image: "",
                image2: "",
                image3: "",
                image4: "",
                colorCode: "#2c3e50",
                isPlaceholder: true
            }
        ];
        localStorage.setItem('Carzo_cars', JSON.stringify(defaultCars));
    }

    if (!localStorage.getItem('Carzo_categories')) {
        const defaultCategories = [
            { name: "Luxury", subcategories: ["Sports Sedan", "Premium Coupe"] },
            { name: "SUV", subcategories: ["Offroad SUV", "Premium SUV"] },
            { name: "Electric", subcategories: ["Electric Sedan", "Electric SUV"] },
            { name: "Economy", subcategories: ["Daily Commuter", "Compact Hatchback"] }
        ];
        localStorage.setItem('Carzo_categories', JSON.stringify(defaultCategories));
    }

    if (!localStorage.getItem('Carzo_admins')) {
        const defaultAdmins = [
            { name: "Mayan Sharma", email: "mayan@example.com", phone: "+91 98765 43210", role: "Super Admin", access: "Full Control" },
            { name: "Pranav Patil", email: "pranav@example.com", phone: "+91 98234 11223", role: "Fleet Manager", access: "Edit Fleet" },
            { name: "Riya Deshmukh", email: "riya@example.com", phone: "+91 90112 23344", role: "Support Admin", access: "Bookings Only" }
        ];
        localStorage.setItem('Carzo_admins', JSON.stringify(defaultAdmins));
    }

    if (!localStorage.getItem('Carzo_customers')) {
        const defaultCustomers = [
            { name: "Mayan Sharma", email: "mayan@example.com", phone: "+91 98765 43210", location: "Pune", recentLogin: "26 May 2026, 02:15 AM" },
            { name: "Priya Patel", email: "priya@example.com", phone: "+91 98123 45678", location: "Mumbai", recentLogin: "25 May 2026, 09:30 PM" },
            { name: "Rohan Gupta", email: "rohan@example.com", phone: "+91 98234 56789", location: "Pune", recentLogin: "26 May 2026, 01:10 AM" },
            { name: "Amit Shah", email: "amit@example.com", phone: "+91 98901 23456", location: "Pune", recentLogin: "24 May 2026, 03:45 PM" },
            { name: "Sunita Rao", email: "sunita@example.com", phone: "+91 98765 12345", location: "Bangalore", recentLogin: "25 May 2026, 11:20 AM" }
        ];
        localStorage.setItem('Carzo_customers', JSON.stringify(defaultCustomers));
    }

    if (!localStorage.getItem('Carzo_owners')) {
        const defaultOwners = [
            { id: "owner_rohan", name: "Rohan Pune-Owner", phone: "+91 90110 12345", email: "rohan@example.com", location: "Koregaon Park, Pune" },
            { id: "owner_aditya", name: "Aditya Shah", phone: "+91 98224 87654", email: "aditya@example.com", location: "Baner, Pune" },
            { id: "owner_vikram", name: "Vikram Kothrud-Owner", phone: "+91 94220 98765", email: "vikram@example.com", location: "Kothrud, Pune" },
            { id: "owner_sanjay", name: "Sanjay Hadapsar-Owner", phone: "+91 98810 54321", email: "sanjay@example.com", location: "Hadapsar, Pune" },
            { id: "owner_amit", name: "Amit Viman-Owner", phone: "+91 90112 34567", email: "amit@example.com", location: "Viman Nagar, Pune" },
            { id: "owner_nisha", name: "Nisha Baner-Owner", phone: "+91 98901 12345", email: "nisha@example.com", location: "Baner, Pune" },
            { id: "owner_vijay", name: "Vijay Kalyani-Owner", phone: "+91 99234 56789", email: "vijay@example.com", location: "Kalyani Nagar, Pune" }
        ];
        localStorage.setItem('Carzo_owners', JSON.stringify(defaultOwners));
    }

    if (!localStorage.getItem('Carzo_bookings')) {
        const defaultBookings = [
            {
                id: "BD-409182",
                carId: "rangerover_black",
                carName: "Range Rover Sport",
                carImage: "rangerover_black.png",
                isPlaceholder: false,
                pickupLoc: "Koregaon Park, Pune",
                pickupDate: "2026-05-20",
                pickupTime: "10:00",
                dropDate: "2026-05-24",
                dropTime: "18:00",
                totalDays: 4,
                totalCost: 18000,
                status: "Delivered",
                dateCreated: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
                custName: "Rohan Gupta",
                custPhone: "+91 98234 56789",
                custEmail: "rohan@example.com"
            },
            {
                id: "BD-889104",
                carId: "mitsubishi_white",
                carName: "Mitsubishi Lancer",
                carImage: "mitsubishi_white.png",
                isPlaceholder: false,
                pickupLoc: "Baner, Pune",
                pickupDate: "2026-05-24",
                pickupTime: "09:00",
                dropDate: "2026-05-26",
                dropTime: "09:00",
                totalDays: 2,
                totalCost: 6000,
                status: "Confirmed",
                dateCreated: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                custName: "Mayan Sharma",
                custPhone: "+91 98765 43210",
                custEmail: "mayan@example.com"
            },
            {
                id: "BD-120938",
                carId: "tesla_blue",
                carName: "Tesla Model Y",
                carImage: "tesla_blue.png",
                isPlaceholder: false,
                pickupLoc: "Viman Nagar, Pune",
                pickupDate: "2026-05-28",
                pickupTime: "14:00",
                dropDate: "2026-05-31",
                dropTime: "14:00",
                totalDays: 3,
                totalCost: 10500,
                status: "Confirmed",
                dateCreated: new Date().toISOString(),
                custName: "Amit Shah",
                custPhone: "+91 98901 23456",
                custEmail: "amit@example.com"
            }
        ];
        localStorage.setItem('Carzo_bookings', JSON.stringify(defaultBookings));
    }

    // Check if user is logged in
    // First time visiting: default is logged in as Mayan Sharma (mock login/signup logic)
    if (localStorage.getItem('Carzo_logged_in') === null) {
        localStorage.setItem('Carzo_logged_in', 'true');
    }

    const isLoggedIn = localStorage.getItem('Carzo_logged_in') === 'true';

    // Route guard for protected dashboard / profile / booking pages
    const currentPage = window.location.pathname.split('/').pop().toLowerCase();
    const protectedPages = ['dashboard.html', 'profile.html', 'booking-management.html', 'admin.html', 'booking.html'];
    if (!isLoggedIn && protectedPages.includes(currentPage)) {
        window.location.href = 'login.html';
        return;
    }

    let activeUser = null;
    if (isLoggedIn) {
        try {
            activeUser = JSON.parse(localStorage.getItem('Carzo_user_profile'));
        } catch (e) {
            console.error("Failed to parse user profile", e);
        }

        if (!activeUser) {
            activeUser = {
                name: "Mayan Sharma",
                email: "mayan@example.com",
                phone: "+91 98765 43210",
                avatar: ""
            };
            localStorage.setItem('Carzo_user_profile', JSON.stringify(activeUser));
        }

        // Sync active logged in user to Carzo_customers
        let customers = JSON.parse(localStorage.getItem('Carzo_customers')) || [];
        let existingCust = customers.find(c => c.email.toLowerCase() === activeUser.email.toLowerCase());
        if (!existingCust) {
            const now = new Date();
            const day = now.getDate();
            const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const month = monthNames[now.getMonth()];
            const year = now.getFullYear();
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            const timeStr = `${String(hours).padStart(2, '0')}:${minutes} ${ampm}`;
            const loginDateStr = `${day} ${month} ${year}, ${timeStr}`;

            customers.push({
                name: activeUser.name,
                email: activeUser.email,
                phone: activeUser.phone,
                location: "Pune",
                recentLogin: loginDateStr
            });
            localStorage.setItem('Carzo_customers', JSON.stringify(customers));
        } else if (!existingCust.recentLogin || existingCust.recentLogin === 'First Login') {
            const now = new Date();
            const day = now.getDate();
            const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const month = monthNames[now.getMonth()];
            const year = now.getFullYear();
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            const timeStr = `${String(hours).padStart(2, '0')}:${minutes} ${ampm}`;
            const loginDateStr = `${day} ${month} ${year}, ${timeStr}`;

            existingCust.recentLogin = loginDateStr;
            localStorage.setItem('Carzo_customers', JSON.stringify(customers));
        }
    }

    const navbarAuth = document.getElementById('navbar-auth');
    const profileDropdown = document.getElementById('profile-dropdown');

    // Show/hide profile dropdown and auth buttons depending on login state
    if (isLoggedIn) {
        if (navbarAuth) navbarAuth.style.display = 'none';
        if (profileDropdown) profileDropdown.style.display = 'inline-block';
    } else {
        if (navbarAuth) navbarAuth.style.display = 'flex';
        if (profileDropdown) profileDropdown.style.display = 'none';
    }

    // Calculate user initials safely
    const userName = (activeUser && typeof activeUser.name === 'string') ? activeUser.name : "Mayan Sharma";
    const nameParts = userName.trim().split(/\s+/).filter(Boolean);
    const initials = nameParts.map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'MS';

    // Update avatar image or initials in navbar
    const navAvatar = document.getElementById('navbar-avatar');
    if (navAvatar) {
        if (activeUser && activeUser.avatar) {
            navAvatar.innerHTML = `<img src="${activeUser.avatar}" alt="Avatar" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
        } else {
            navAvatar.innerHTML = initials;
        }
    }

    // Update sidebar avatar and name in dashboards (if they exist)
    const sidebarAvatar = document.getElementById('nav-avatar');
    const sidebarName = document.getElementById('nav-name');
    if (sidebarAvatar) {
        if (activeUser && activeUser.avatar) {
            sidebarAvatar.innerHTML = `<img src="${activeUser.avatar}" alt="Avatar" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
        } else {
            sidebarAvatar.textContent = initials;
        }
    }
    if (sidebarName && activeUser) {
        sidebarName.textContent = activeUser.name || '';
    }

    // Update profile info inside dropdown
    const navProfileName = document.getElementById('navbar-profile-name');
    const navProfileEmail = document.getElementById('navbar-profile-email');
    if (navProfileName && activeUser) navProfileName.textContent = activeUser.name || '';
    if (navProfileEmail && activeUser) navProfileEmail.textContent = activeUser.email || '';

    // Toggle dropdown menu
    const profileBtn = document.getElementById('profile-btn');
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

    // Logout button handler logic
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.setItem('Carzo_logged_in', 'false');
            localStorage.removeItem('Carzo_user_profile');
            window.location.href = 'index.html';
        });
    }

    // -------- Daily Price Slider Interaction --------
    const priceSlider = document.querySelector('.price-slider');
    const priceSliderCurrent = document.querySelector('.price-slider__current');
    if (priceSlider && priceSliderCurrent) {
        priceSlider.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            // Translate slider values (e.g. 50-600) to INR (e.g. 500-6000)
            const inrVal = val * 10;
            priceSliderCurrent.textContent = `max. ₹${inrVal.toLocaleString('en-IN')}`;
        });
    }

});

