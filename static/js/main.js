// main.js - Основные JavaScript функции

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Автоматическое скрытие alert сообщений
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Форматирование телефонов
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                value = '+7 (' + value;
                if (value.length > 7) {
                    value = value.slice(0, 7) + ') ' + value.slice(7);
                }
                if (value.length > 12) {
                    value = value.slice(0, 12) + '-' + value.slice(12);
                }
                if (value.length > 15) {
                    value = value.slice(0, 15) + '-' + value.slice(15);
                }
            }
            e.target.value = value;
        });
    });
});

// Функция для показа loading состояния
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="loading me-2"></span> Загрузка...';
    button.disabled = true;
    return originalText;
}

function hideLoading(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}

// Функция для AJAX запросов
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// Валидация форм
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}