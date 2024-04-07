$(document).ready(function() {
    const modalStack = [];
    let lastModal;

    $('#patientModal, #requestModal').on('show.bs.modal', function () {
        const modalId = $(this).data('modal-id');
        if (lastModal !== undefined && modalId !== lastModal.data('modal-id')) {
            lastModal.modal('hide');
            modalStack.push(lastModal);
        }
      
        lastModal = $(this);
    })

    $('#patientModal, #requestModal').on('hidden.bs.modal', function () {
        const modalId = $(this).data('modal-id');
        if (modalId === lastModal.data('modal-id')) {
            lastModal = modalStack.pop();
            if (lastModal) {
                lastModal.modal('show');
            }
        }
    })
})

export function showError(message) {
    var errorAlert = new bootstrap.Toast(document.getElementById('error-alert'));
    $('#error-message').text(message);
    errorAlert.show();
}
