// about.js - JavaScript для страницы "О ресторане"

document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления элементов при скролле
    initScrollAnimations();

    // Инициализация счетчиков статистики
    initCounters();

    // Инициализация галереи
    initGallery();

    // Параллакс эффект для mission section
    initParallax();
});

// Анимация появления элементов
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.timeline-item, .team-card, .value-card, .award-card');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// Анимация счетчиков
function initCounters() {
    const counters = document.querySelectorAll('.stat-number');
    const speed = 200;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                counters.forEach(counter => {
                    const target = +counter.getAttribute('data-target');
                    const count = +counter.innerText;

                    if (count < target) {
                        const inc = target / speed;
                        if (count + inc > target) {
                            counter.innerText = target;
                        } else {
                            counter.innerText = Math.ceil(count + inc);
                            setTimeout(() => updateCounter(counter, target, speed), 1);
                        }
                    }
                });
            }
        });
    }, { threshold: 0.5 });

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        observer.observe(statsSection);
    }
}

function updateCounter(counter, target, speed) {
    const count = +counter.innerText;
    const inc = target / speed;

    if (count < target) {
        counter.innerText = Math.ceil(count + inc);
        setTimeout(() => updateCounter(counter, target, speed), 1);
    } else {
        counter.innerText = target;
    }
}

// Простая галерея
function initGallery() {
    const galleryItems = document.querySelectorAll('.gallery-item');

    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            const imgSrc = this.querySelector('img').src;
            openLightbox(imgSrc);
        });
    });

    // Создаем lightbox
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.9);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        cursor: pointer;
    `;

    const lightboxImg = document.createElement('img');
    lightboxImg.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
    `;

    lightbox.appendChild(lightboxImg);
    document.body.appendChild(lightbox);

    lightbox.addEventListener('click', function() {
        this.style.display = 'none';
    });

    window.openLightbox = function(src) {
        lightboxImg.src = src;
        lightbox.style.display = 'flex';
    };
}

// Параллакс эффект
function initParallax() {
    const missionSection = document.querySelector('.mission-section');

    if (missionSection) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            missionSection.style.transform = `translateY(${rate}px)`;
        });
    }
}

// Анимация хлебных крошек
function initBreadcrumbsAnimation() {
    const breadcrumbs = document.querySelector('.breadcrumb');
    if (breadcrumbs) {
        breadcrumbs.style.opacity = '0';
        breadcrumbs.style.transform = 'translateX(-20px)';

        setTimeout(() => {
            breadcrumbs.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            breadcrumbs.style.opacity = '1';
            breadcrumbs.style.transform = 'translateX(0)';
        }, 300);
    }
}

// Инициализация всех функций
initBreadcrumbsAnimation();