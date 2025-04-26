// Common JavaScript functionality for AI Fashion Advisor

// Function to show a toast/alert message
function showToast(message, type = 'info') {
    // This will be implemented with a proper toast component in Phase 2
    alert(message);
}

// Function to create a Bootstrap alert
function createAlert(message, type = 'info', dismissible = true) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} ${dismissible ? 'alert-dismissible fade show' : ''}`;
    alertDiv.setAttribute('role', 'alert');
    
    alertDiv.innerHTML = message;
    
    if (dismissible) {
        alertDiv.innerHTML += `
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    }
    
    return alertDiv;
}

// Function to confirm deletion
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Function to handle image preview
function setupImagePreview(inputId, previewId, placeholderId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    const placeholder = document.getElementById(placeholderId);
    
    if (input && preview) {
        input.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    preview.src = event.target.result;
                    preview.classList.remove('d-none');
                    if (placeholder) {
                        placeholder.classList.add('d-none');
                    }
                };
                
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Global initialization code can go here
    console.log('AI Fashion Advisor initialized');
});