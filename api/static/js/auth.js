async function handleRegister(event) {
    event.preventDefault();
    console.log("Formulaire soumis"); // Debug

    const nameInput = document.getElementById('registerName');
    const emailInput = document.getElementById('registerEmail');
    const passwordInput = document.getElementById('registerPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const errorDiv = document.getElementById('registerError');
    const submitButton = document.getElementById('registerSubmit');

    // Réinitialisation des erreurs
    errorDiv.textContent = '';
    errorDiv.style.display = 'none';

    // Validation des mots de passe
    if (passwordInput.value !== confirmPasswordInput.value) {
        showError("Les mots de passe ne correspondent pas");
        return;
    }

    // Désactiver le bouton
    submitButton.disabled = true;
    submitButton.textContent = 'Inscription en cours...';

    try {
        console.log("Envoi de la requête..."); // Debug
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: nameInput.value.trim(),
                email: emailInput.value.trim(),
                password: passwordInput.value
            }),
        });

        console.log("Réponse reçue:", response.status); // Debug
        const data = await response.json();

        if (response.ok) {
            showSuccess("Inscription réussie! Redirection vers la connexion...");
            setTimeout(() => {
                closeModal('registerModal');
                showLoginModal();
            }, 2000);
        } else {
            showError(data.message || "Erreur lors de l'inscription");
        }
    } catch (error) {
        console.error("Erreur:", error); // Debug
        showError("Erreur de connexion au serveur");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "S'inscrire";
    }
}

function showError(message) {
    const errorDiv = document.getElementById('registerError');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.backgroundColor = '#f8d7da';
    errorDiv.style.padding = '10px';
    errorDiv.style.borderRadius = '4px';
    errorDiv.style.marginBottom = '10px';
}

function showSuccess(message) {
    const errorDiv = document.getElementById('registerError');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.style.color = '#28a745';
    errorDiv.style.backgroundColor = '#d4edda';
    errorDiv.style.padding = '10px';
    errorDiv.style.borderRadius = '4px';
    errorDiv.style.marginBottom = '10px';
}

function switchToLogin() {
    closeModal('registerModal');
    showLoginModal();
}

// Ajout des validations en temps réel
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, initialisation des validations..."); // Debug
    const passwordInput = document.getElementById('registerPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            if (this.value !== passwordInput.value) {
                this.setCustomValidity('Les mots de passe ne correspondent pas');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});

// Validation du mot de passe
function validatePassword(password) {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    
    const errors = [];
    if (password.length < minLength) {
        errors.push(`Le mot de passe doit contenir au moins ${minLength} caractères`);
    }
    if (!hasUpperCase) {
        errors.push("Le mot de passe doit contenir au moins une majuscule");
    }
    if (!hasLowerCase) {
        errors.push("Le mot de passe doit contenir au moins une minuscule");
    }
    if (!hasNumbers) {
        errors.push("Le mot de passe doit contenir au moins un chiffre");
    }
    
    return errors;
}

async function handleLogin(event) {
    event.preventDefault();
    const emailInput = document.getElementById('loginEmail');
    const passwordInput = document.getElementById('loginPassword');
    const errorDiv = document.getElementById('loginError');
    const submitButton = document.getElementById('loginSubmit');

    // Réinitialisation des erreurs
    errorDiv.textContent = '';
    errorDiv.style.display = 'none';

    // Désactiver le bouton
    submitButton.disabled = true;
    submitButton.textContent = 'Connexion en cours...';

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: emailInput.value.trim(),
                password: passwordInput.value
            }),
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            showSuccess("Connexion réussie! Redirection...");
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showError(data.message || "Erreur lors de la connexion");
        }
    } catch (error) {
        showError("Erreur de connexion au serveur");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Se connecter";
    }
} 