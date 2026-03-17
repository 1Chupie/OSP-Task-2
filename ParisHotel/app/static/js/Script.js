function submitBooking(event) {
    event.preventDefault();
    
    openPaymentModal();
}

function openPaymentModal(bookingId) {
    document.getElementById('paymentModal').style.display = 'block';
    if (bookingId) {
        document.getElementById('bookingId').value = bookingId;
    }
}

function closePaymentModal() {
    document.getElementById('paymentModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('paymentModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}