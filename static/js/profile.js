// profile.js - JavaScript для личного кабинета

class UserProfile {
    constructor() {
        this.currentSection = 'reservations';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadUserStats();
        this.initializeCalendar();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.profile-nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.showSection(section);
            });
        });

        // Reservation actions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('cancel-reservation')) {
                this.cancelReservation(e.target.dataset.reservationId);
            }
            if (e.target.classList.contains('edit-reservation')) {
                this.editReservation(e.target.dataset.reservationId);
            }
        });

        // Avatar upload
        const avatarInput = document.getElementById('avatarInput');
        if (avatarInput) {
            avatarInput.addEventListener('change', (e) => this.handleAvatarUpload(e));
        }

        // Form submissions
        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => this.handleProfileSubmit(e));
        }

        // Calendar navigation
        document.getElementById('prevMonth')?.addEventListener('click', () => this.changeMonth(-1));
        document.getElementById('nextMonth')?.addEventListener('click', () => this.changeMonth(1));
    }

    showSection(section) {
        // Update navigation
        document.querySelectorAll('.profile-nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.content-section').forEach(sectionEl => {
            sectionEl.classList.remove('active');
        });
        document.getElementById(`${section}Section`).classList.add('active');

        this.currentSection = section;

        // Load section-specific data
        if (section === 'calendar') {
            this.loadCalendarData();
        } else if (section === 'notifications') {
            this.loadNotifications();
        }
    }

    async loadUserStats() {
        try {
            // In a real app, this would be an API call
            const stats = {
                total_reservations: 12,
                upcoming_reservations: 2,
                completed_reservations: 8,
                cancelled_reservations: 2
            };

            this.updateStatsDisplay(stats);
        } catch (error) {
            console.error('Failed to load user stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        document.getElementById('totalReservations').textContent = stats.total_reservations;
        document.getElementById('upcomingReservations').textContent = stats.upcoming_reservations;
        document.getElementById('completedReservations').textContent = stats.completed_reservations;
        document.getElementById('cancelledReservations').textContent = stats.cancelled_reservations;
    }

    async cancelReservation(reservationId) {
        if (!confirm('Вы уверены, что хотите отменить это бронирование?')) {
            return;
        }

        const button = document.querySelector(`[data-reservation-id="${reservationId}"]`);
        const originalText = button.innerHTML;

        button.disabled = true;
        button.innerHTML = '<span class="loading me-2"></span> Отмена...';

        try {
            const response = await fetch(`/reservations/cancel/${reservationId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                this.showMessage('Бронирование успешно отменено', 'success');
                this.refreshReservationsList();
            } else {
                throw new Error('Ошибка при отмене бронирования');
            }

        } catch (error) {
            console.error('Cancel reservation failed:', error);
            this.showMessage('Ошибка при отмене бронирования', 'error');
        } finally {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    editReservation(reservationId) {
        window.location.href = `/reservations/edit/${reservationId}/`;
    }

    async refreshReservationsList() {
        // In a real app, this would reload the reservations via AJAX
        window.location.reload();
    }

    handleAvatarUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type and size
        if (!file.type.startsWith('image/')) {
            this.showMessage('Пожалуйста, выберите изображение', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB
            this.showMessage('Размер файла не должен превышать 5MB', 'error');
            return;
        }

        // Preview image
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('avatarPreview');
            if (preview) {
                preview.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);

        // Upload image
        this.uploadAvatar(file);
    }

    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);

        try {
            const response = await fetch('/users/profile/update-avatar/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });

            if (response.ok) {
                this.showMessage('Аватар успешно обновлен', 'success');
            } else {
                throw new Error('Ошибка при загрузке аватара');
            }

        } catch (error) {
            console.error('Avatar upload failed:', error);
            this.showMessage('Ошибка при загрузке аватара', 'error');
        }
    }

    async handleProfileSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading me-2"></span> Сохранение...';

        try {
            const formData = new FormData(form);

            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });

            if (response.ok) {
                this.showMessage('Профиль успешно обновлен', 'success');
            } else {
                throw new Error('Ошибка при обновлении профиля');
            }

        } catch (error) {
            console.error('Profile update failed:', error);
            this.showMessage('Ошибка при обновлении профиля', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }

    initializeCalendar() {
        this.currentDate = new Date();
        this.renderCalendar();
    }

    renderCalendar() {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl) return;

        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();

        // Update calendar header
        document.getElementById('currentMonth').textContent =
            this.currentDate.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' });

        // Get first day of month and number of days
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();

        // Create calendar grid
        let calendarHTML = '';

        // Add day headers
        const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
        dayNames.forEach(day => {
            calendarHTML += `<div class="calendar-header">${day}</div>`;
        });

        // Add empty cells for days before first day of month
        const startDay = firstDay.getDay() || 7; // Convert Sunday (0) to 7
        for (let i = 1; i < startDay; i++) {
            const prevDate = new Date(year, month, 1 - i);
            calendarHTML += this.createCalendarDay(prevDate, true);
        }

        // Add days of current month
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const isToday = date.toDateString() === today.toDateString();
            calendarHTML += this.createCalendarDay(date, false, isToday);
        }

        // Add empty cells for days after last day of month
        const totalCells = 42; // 6 weeks
        const filledCells = startDay - 1 + daysInMonth;
        for (let i = 1; i <= totalCells - filledCells; i++) {
            const nextDate = new Date(year, month + 1, i);
            calendarHTML += this.createCalendarDay(nextDate, true);
        }

        calendarEl.innerHTML = calendarHTML;

        // Add click handlers
        calendarEl.querySelectorAll('.calendar-day:not(.other-month)').forEach(day => {
            day.addEventListener('click', () => {
                const date = day.dataset.date;
                this.showReservationsForDate(date);
            });
        });
    }

    createCalendarDay(date, isOtherMonth, isToday = false) {
        const day = date.getDate();
        const dateString = date.toISOString().split('T')[0];

        let className = 'calendar-day';
        if (isOtherMonth) className += ' other-month';
        if (isToday) className += ' today';
        if (this.hasReservation(date)) className += ' has-reservation';

        return `
            <div class="${className}" data-date="${dateString}">
                <div class="day-number">${day}</div>
                ${this.getReservationBadges(date)}
            </div>
        `;
    }

    hasReservation(date) {
        // In a real app, this would check against user's reservations
        // For demo, we'll use random data
        return Math.random() > 0.7;
    }

    getReservationBadges(date) {
        // In a real app, this would show actual reservation counts
        const count = Math.floor(Math.random() * 3);
        return count > 0 ? `<span class="reservation-badge">${count}</span>` : '';
    }

    changeMonth(direction) {
        this.currentDate.setMonth(this.currentDate.getMonth() + direction);
        this.renderCalendar();
        this.loadCalendarData();
    }

    async loadCalendarData() {
        // In a real app, this would load reservations for the current month
        console.log('Loading calendar data for:', this.currentDate);
    }

    showReservationsForDate(date) {
        // In a real app, this would show a modal with reservations for that date
        alert(`Показать бронирования на ${date}`);
    }

    async loadNotifications() {
        // In a real app, this would load user notifications
        const notifications = [
            {
                id: 1,
                title: 'Бронирование подтверждено',
                message: 'Ваше бронирование на 15 декабря подтверждено',
                time: '2 часа назад',
                unread: true
            },
            {
                id: 2,
                title: 'Напоминание о бронировании',
                message: 'Напоминаем о вашем бронировании на завтра в 19:00',
                time: '1 день назад',
                unread: false
            }
        ];

        this.renderNotifications(notifications);
    }

    renderNotifications(notifications) {
        const container = document.getElementById('notificationsList');
        if (!container) return;

        if (notifications.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-bell"></i>
                    <h4>Нет уведомлений</h4>
                    <p>Здесь будут появляться ваши уведомления</p>
                </div>
            `;
            return;
        }

        container.innerHTML = notifications.map(notification => `
            <div class="notification-item ${notification.unread ? 'unread' : ''}">
                <h6 class="mb-1">${notification.title}</h6>
                <p class="mb-1">${notification.message}</p>
                <div class="notification-time">${notification.time}</div>
            </div>
        `).join('');
    }

    showMessage(message, type) {
        // Remove existing messages
        document.querySelectorAll('.alert').forEach(alert => alert.remove());

        // Create new message
        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertEl.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the content
        const content = document.querySelector('.profile-content');
        content.insertBefore(alertEl, content.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertEl.parentNode) {
                alertEl.remove();
            }
        }, 5000);
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize the profile when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.userProfile = new UserProfile();
});