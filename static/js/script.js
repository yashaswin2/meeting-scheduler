document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date for meeting creation to today
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        dateInput.value = today;
    }

    // Set default time to next hour
    const timeInput = document.getElementById('time');
    if (timeInput) {
        const now = new Date();
        now.setHours(now.getHours() + 1);
        now.setMinutes(0);
        timeInput.value = now.toTimeString().slice(0, 5);
    }

    // Smooth scroll to form when there's an error
    const firstError = document.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Add loading state to buttons
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const button = this.querySelector('button[type="submit"]');
            if (button && !this.classList.contains('was-validated') || this.checkValidity()) {
                const originalText = button.innerHTML;
                button.disabled = true;
                button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...`;
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = originalText;
                }, 2000);
            }
        });
    });

    // Auto-resize textarea
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Smooth alert dismissal
    document.querySelectorAll('.alert').forEach(alert => {
        alert.addEventListener('close.bs.alert', function() {
            this.style.height = this.offsetHeight + 'px';
            this.style.opacity = '1';
            setTimeout(() => {
                this.style.height = '0';
                this.style.opacity = '0';
                this.style.margin = '0';
                this.style.padding = '0';
            }, 10);
        });
    });

    // Add hover effect to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 12px 20px rgba(0,0,0,0.1)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
        });
    });
});

