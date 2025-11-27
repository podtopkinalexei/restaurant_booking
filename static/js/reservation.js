document.addEventListener('DOMContentLoaded', function() {
    console.log('=== RESERVATION SCRIPT LOADED ===');

    const tableCards = document.querySelectorAll('.table-card');
    const tableInput = document.getElementById('selected-table');
    const bookButton = document.getElementById('book-button');
    const checkButton = document.querySelector('button[name="check_availability"]');

    // 1. Обработка выбора столика
    if (tableCards.length > 0 && tableInput) {
        tableCards.forEach(card => {
            card.addEventListener('click', function() {
                tableCards.forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                tableInput.value = this.getAttribute('data-table-id');
            });
        });

        // Автовыбор первого столика
        if (!tableInput.value && tableCards.length > 0) {
            tableCards[0].click();
        }
    }

    // 2. Обработка кнопки бронирования - ТОЛЬКО визуальные эффекты
    // ЗАМЕНИТЕ текущий обработчик на этот:
    if (bookButton && reservationForm) {
        bookButton.addEventListener('click', function(e) {
            // Проверяем выбран ли столик
            if (!tableInput || !tableInput.value) {
                e.preventDefault();
                alert('Пожалуйста, выберите столик');
                return false;
            }

            // Меняем текст кнопки только если валидация прошла
            this.innerHTML = '<i class="bi bi-hourglass-split me-2"></i> Бронируем...';
            this.disabled = true;
        });
    }

    // 3. Скрываем кнопку проверки доступности
    if (checkButton) {
        checkButton.addEventListener('click', function() {
            setTimeout(() => {
                this.style.display = 'none';
            }, 100);
        });
    }
});