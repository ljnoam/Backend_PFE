# PromptOptim (Green IT & Souveraineté)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Green IT](https://img.shields.io/badge/Green%20IT-Eco%20Responsible-2ea44f?style=for-the-badge)

> **Optimisez vos prompts IA pour réduire leur empreinte carbone tout en protégeant vos données.**

PromptOptim est une API REST développée dans le cadre d'un PFE, visant à concilier performance IA, éco-responsabilité et souveraineté des données. Elle permet de reformuler des prompts pour qu'ils consomment moins de tokens (et donc moins d'énergie) tout en anonymisant les informations sensibles avant l'envoi aux LLM tiers.

---

## 🚀 Fonctionnalités Clés

- **Authentification Sécurisée** : Système complet d'inscription et de login via JWT (JSON Web Tokens).
- **Moteur IA Intelligent** : Reformulation automatique des prompts via Google Gemini pour cibler spécifiquement ChatGPT, Midjourney ou Mistral.
- **Calculateur Green IT** : Estimation en temps réel des tokens économisés et du CO2 évité pour chaque optimisation.
- **Anonymisation (PII)** : Détection et suppression automatique des données personnelles (noms, emails, etc.) avant traitement.
- **Historique & Statistiques** : Suivi détaillé des optimisations et tableau de bord de l'impact écologique personnel.

---

## 🏗️ Architecture

Le projet repose sur une architecture Cloud moderne et économe :

- **Backend** : [Python FastAPI](https://fastapi.tiangolo.com/) hébergé sur **Render** (déploiement continu).
- **Base de Données** : [PostgreSQL](https://www.postgresql.org/) géré par **Supabase**.
- **IA Engine** : API [Google Gemini](https://ai.google.dev/) (Modèle Flash pour la rapidité et l'efficacité).

---

## 🛠️ Installation Local (Dev)

Suivez ces étapes pour lancer le projet sur votre machine.

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/promptoptim-backend.git
cd promptoptim-backend
```

### 2. Installer les dépendances
Il est recommandé d'utiliser un environnement virtuel (venv).

```bash
pip install -r requirements.txt
```

### 3. Configuration du .env
Créez un fichier `.env` à la racine du projet et ajoutez les variables suivantes :

```ini
# Connexion Base de Données (Supabase)
DATABASE_URL="postgresql://user:password@host:port/dbname"

# Clé API Google Gemini (pour le moteur d'optimisation)
GOOGLE_API_KEY="votre_cle_api_gemini"
```

### 4. Lancement
Démarrez le serveur de développement avec Uvicorn (avec rechargement automatique) :

```bash
uvicorn app.main:app --reload
```

Le serveur sera accessible sur `http://127.0.0.1:8000`.

---

## 📚 Documentation API

La documentation interactive (Swagger UI) est générée automatiquement et accessible à l'adresse suivante une fois le serveur lancé :

👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Endpoints Principaux

| Méthode | Route | Description | Auth Requise |
| :--- | :--- | :--- | :---: |
| **POST** | `/api/generate` | Optimise un prompt, anonymise les données et calcule l'impact Green. | ✅ |
| **GET** | `/api/history` | Récupère l'historique des prompts optimisés de l'utilisateur. | ✅ |
| **GET** | `/api/stats` | Affiche les statistiques globales (CO2 économisé, modèles utilisés). | ✅ |
| **POST** | `/register` | Création d'un nouveau compte utilisateur. | ❌ |
| **POST** | `/token` | Authentification (Login) pour obtenir un Access Token. | ❌ |
| **DELETE** | `/users/me` | Suppression du compte utilisateur et de ses données. | ✅ |
| **GET** | `/health` | Vérification de l'état du serveur et de la connexion BDD. | ❌ |

---

## 🧪 Tests

Pour exécuter les tests (si disponibles) :
```bash
pytest
```

---

*Développé avec ❤️ pour un numérique plus responsable.*
