# 🎩 AlfredBridge

AlfredBridge agit comme votre majordome digital, gérant élégamment les interactions entre Facebook et vos APIs.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FRadouaneElarfaoui%2FAlfredBridge)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📑 Table des Matières
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Documentation API](#-documentation-api)
- [Exemples d'Intégration](#-exemples-dintégration)
- [Contribution](#-contribution)
- [Licence](#-licence)
- [Contact](#-contact)

## 🌟 Fonctionnalités

- 🤖 Gestion automatisée des webhooks Facebook
- 🔐 Encodage/décodage sécurisé en base64
- 🧪 Interface de test interactive
- 📡 Relais intelligent des messages
- ⚡ Déploiement facile sur Vercel

## 🚀 Installation

### Prérequis
- Python 3.9+
- Un compte Facebook Developer
- Un compte Vercel (pour le déploiement)

### Installation Locale
```bash
git clone https://github.com/RadouaneElarfaoui/AlfredBridge.git
pip install -r requirements.txt
vercel dev
```

## ⚙️ Configuration

1. Configurez votre webhook Facebook avec l'URL de votre application
2. Modifiez `api/config.py` avec vos identifiants Facebook

## 📖 Documentation API

### Endpoints Disponibles
- `GET /webhook` : Validation du webhook Facebook
- `POST /webhook` : Réception des événements Facebook
- `GET /test` : Interface de test
- `GET /webhook/history` : Historique des webhooks reçus

### Processus de Fonctionnement

1. **Envoi Initial (Utilisateur)**
   - Préparation de la requête API en JSON
   - Encodage en base64 de la requête
   - Envoi du message encodé via Facebook API
   - Publication sur la page Facebook

2. **Réception Webhook**
   - Réception sur `/webhook`
   - Vérification signature Facebook
   - Stockage dans l'historique
   - Détection du type de changement (post/comment)

3. **Traitement du Message**
   - Décodage base64 du message
   - Validation de la structure JSON
   - Extraction des paramètres de requête
   - Vérification des permissions

4. **Exécution de la Requête**
   - Envoi vers l'API cible
   - Gestion des timeouts et erreurs
   - Collecte de la réponse
   - Formatage du résultat

5. **Réponse et Mise à Jour**
   - Encodage base64 de la réponse
   - Mise à jour du post Facebook original
   - Stockage dans l'historique
   - Notification de complétion

### Exemple de Flux Complet

1. **Message Initial (Utilisateur → Facebook)**
```json
{
    "message": "eyJyZXF1ZXN0Ijp7Im1ldGhvZCI6IkdFVCIsInVybCI6Imh0dHBzOi8vYXBpLmV4YW1wbGUuY29tIn19"
}
```

2. **Réponse Finale (AlfredBridge → Facebook)**
```json
{
    "message": "eyJyZXNwb25zZSI6eyJzdGF0dXMiOjIwMCwiZGF0YSI6eyJyZXN1bHQiOiJzdWNjZXNzIn19fQ=="
}
```

## 🔌 Exemples d'Intégration

### APIs Populaires

#### Wikipedia
```json
{
    "request": {
        "method": "GET",
        "url": "https://fr.wikipedia.org/w/api.php",
        "params": {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "titles": "Paris",
            "exintro": true
        }
    }
}
```

#### Google Search
```json
{
    "request": {
        "method": "GET",
        "url": "https://www.googleapis.com/customsearch/v1",
        "params": {
            "key": "YOUR_API_KEY",
            "cx": "YOUR_SEARCH_ENGINE_ID",
            "q": "recherche"
        }
    }
}
```

[Plus d'exemples dans la documentation complète](docs/API-EXAMPLES.md)

### 🔑 Configuration des APIs

1. **Google APIs**
   - [Console Google Cloud](https://console.cloud.google.com/)
   - Activer APIs nécessaires
   - Créer identifiants

2. **Autres Services**
   - [OpenWeatherMap](https://openweathermap.org/api)
   - [News API](https://newsapi.org/)
   - [Documentation complète](docs/API-KEYS.md)

## 🛠️ Technologies

- Flask 3.0.3
- Python 3.9+
- Vercel Serverless

## 🤝 Contribution

1. Fork
2. Créer branche (`feature/NewFeature`)
3. Commit (`git commit -m 'Add NewFeature'`)
4. Push (`git push origin feature/NewFeature`)
5. Pull Request

## 📝 Licence

MIT License - [LICENSE](LICENSE)

## 📫 Contact

[Votre Nom](https://twitter.com/votre_twitter)

---
[Documentation Complète](docs/README.md) | [Exemples](docs/EXAMPLES.md) | [Guide API](docs/API.md)

Lien du projet: [https://github.com/RadouaneElarfaoui/AlfredBridge](https://github.com/RadouaneElarfaoui/AlfredBridge)