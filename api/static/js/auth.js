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

function validateEmailFormat(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

document.getElementById('loginEmail').addEventListener('input', function() {
    const emailInput = this;
    const isValid = validateEmailFormat(emailInput.value);
    emailInput.classList.toggle('invalid', !isValid);
    
    if (!isValid) {
        showFieldError(emailInput, 'Format d\'email invalide');
    } else {
        clearFieldError(emailInput);
    }
}); 

function updatePasswordStrength(password) {
    const strength = {
        0: "Très faible",
        1: "Faible",
        2: "Moyen",
        3: "Fort",
        4: "Très fort"
    };
    
    let score = 0;
    if (password.length > 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    return {
        score: score,
        text: strength[score]
    };
}

function handleRememberMe(token) {
    if (document.getElementById('rememberMe').checked) {
        const tokenData = {
            value: token,
            expiry: new Date().getTime() + (30 * 24 * 60 * 60 * 1000) // 30 jours
        };
        localStorage.setItem('rememberedToken', JSON.stringify(tokenData));
    }
}

const errorMessages = {
    'invalid_credentials': 'Email ou mot de passe incorrect',
    'account_locked': 'Compte temporairement bloqué. Veuillez réessayer dans quelques minutes',
    'network_error': 'Problème de connexion. Veuillez vérifier votre connexion internet'
};

function showFormattedError(errorCode) {
    const message = errorMessages[errorCode] || 'Une erreur est survenue';
    showError(message);
}

// Ajouter ces fonctions avant l'event listener de l'email
function showFieldError(inputElement, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    // Supprimer l'ancien message d'erreur s'il existe
    clearFieldError(inputElement);
    
    // Ajouter le nouveau message d'erreur après l'input
    inputElement.parentNode.insertBefore(errorDiv, inputElement.nextSibling);
    inputElement.classList.add('invalid');
}

function clearFieldError(inputElement) {
    const existingError = inputElement.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    inputElement.classList.remove('invalid');
}

// Ajouter ces styles CSS
const style = document.createElement('style');
style.textContent = `
    .field-error {
        color: #dc3545;
        font-size: 0.875em;
        margin-top: 0.25rem;
    }
    
    .invalid {
        border-color: #dc3545 !important;
        background-color: #fff8f8;
    }
`;
document.head.appendChild(style);

// Fonction pour générer une couleur aléatoire cohérente basée sur le nom
function stringToColor(string) {
    let hash = 0;
    for (let i = 0; i < string.length; i++) {
        hash = string.charCodeAt(i) + ((hash << 5) - hash);
    }
    const color = '#' + ('00000' + (hash & 0xFFFFFF).toString(16)).slice(-6);
    return color;
}

// Fonction pour obtenir les initiales
function getInitials(name) {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
}

// Mise à jour de la fonction updateUIForLoggedInUser
function updateUIForLoggedInUser(userData) {
    const authButtons = document.querySelector('.auth-buttons');
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');
    const userAvatar = document.getElementById('userAvatar');

    if (!authButtons || !userMenu || !userName || !userAvatar) {
        console.error('Éléments DOM manquants');
        return;
    }

    if (userData) {
        authButtons.style.display = 'none';
        userMenu.style.display = 'flex';
        userName.textContent = userData.name;
        
        const initials = getInitials(userData.name);
        const backgroundColor = stringToColor(userData.name);
        userAvatar.innerHTML = initials;
        userAvatar.style.backgroundColor = backgroundColor;
        
        userMenu.style.opacity = '0';
        userMenu.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            userMenu.style.opacity = '1';
            userMenu.style.transform = 'translateY(0)';
        }, 50);
    } else {
        authButtons.style.display = 'flex';
        userMenu.style.display = 'none';
    }
}

async function checkAuthStatus() {
    const token = localStorage.getItem('token');
    if (token) {
        try {
            const response = await fetch('/auth/verify', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const userData = await response.json();
                updateUIForLoggedInUser(userData);
                return true;
            } else {
                localStorage.removeItem('token');
                updateUIForLoggedInUser(null);
                return false;
            }
        } catch (error) {
            console.error('Erreur de vérification:', error);
            localStorage.removeItem('token');
            updateUIForLoggedInUser(null);
            return false;
        }
    }
    updateUIForLoggedInUser(null);
    return false;
}

async function handleLogout() {
    try {
        const token = localStorage.getItem('token');
        await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        localStorage.removeItem('token');
        updateUIForLoggedInUser(null);
        window.location.reload();
    } catch (error) {
        console.error('Erreur de déconnexion:', error);
    }
}

// Appeler checkAuthStatus au chargement de la page
document.addEventListener('DOMContentLoaded', checkAuthStatus);

document.addEventListener('DOMContentLoaded', function() {
    const userAvatar = document.getElementById('userAvatar');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    if (userAvatar) {
        userAvatar.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });
        
        // Fermer le menu au clic en dehors
        document.addEventListener('click', function(e) {
            if (!dropdownMenu.contains(e.target) && !userAvatar.contains(e.target)) {
                dropdownMenu.classList.remove('show');
            }
        });
    }
});
