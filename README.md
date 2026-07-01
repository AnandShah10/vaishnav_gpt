<p align="center">
  <span style="font-size: 64px;">🙏</span>
</p>

<h1 align="center">Vaishnav GPT</h1>

<p align="center">
  <strong>Divine Wisdom & Pure Bhakti — An AI-powered scholarly oracle of Vaishnava theology, philosophy, history & ritual practice.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/Azure_OpenAI-GPT--4o--mini-0078D4?style=flat-square&logo=microsoftazure" alt="Azure OpenAI">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-Private-lightgrey?style=flat-square" alt="License">
</p>

---

## 🕉️ Overview

**Vaishnav GPT** is an AI chatbot built on Django and Azure OpenAI that serves as an authoritative, devotional guide to Vaishnava theology. It adapts its responses based on the user's chosen tradition (Sampradaya), providing contextually accurate answers grounded in scriptures like the Bhagavad Gita, Srimad Bhagavatam, and tradition-specific texts.

### ✨ Key Features

- **10 Learning Paths** — Universal Bhakti, Krishna Bhakti, Rama Bhakti, Pushtimarg, Nimbarka, **Bhagavad Gita**, **Srimad Bhagavatam**, **Upanishads & Vedanta**, **Vishnu Puran**, and **Vaishnav Panchang**
- **Email OTP Authentication** — Passwordless login via email OTP with JWT token issuance for mobile API support
- **Multi-Language Support** — Full interface and greetings in **English**, **Hindi** (हिन्दी), and **Gujarati** (ગુજરાતી)
- **Learning Progress Persistence** — Authenticated users' chat history is saved per tradition and restored on return
- **Streaming Responses** — Real-time token-by-token bot replies with typing animation
- **Sampradaya-Adaptive Responses** — Tailors philosophical vocabulary, scriptural citations, and ritual guidance per tradition
- **Feedback System** — Auto-triggers after 3 messages; email field auto-filled for logged-in users. Exposes `X-Show-Feedback` HTTP header for mobile clients
- **Real-Time Panchang** — Vaishnav Panchang path auto-sends today's panchang query on selection
- **Rich Markdown Rendering** — Bot responses rendered with headings, lists, bold text, and code blocks
- **Conversation Logging** — All messages stored in the database for analytics

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6.0 (WSGI) |
| **AI Engine** | Azure OpenAI — GPT-4o-mini |
| **Auth** | Email OTP + Django Sessions + JWT (SimpleJWT) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Fonts** | Inter, Cinzel (Google Fonts) |
| **Deployment** | Azure App Service / Gunicorn |

---

## 📂 Project Structure

```
vaishnav_gpt/
├ bot/
│   ├ models.py            # Message, UserFeedback, LearningProgress, OTP models
│   ├ views.py             # Chat API, OTP auth, history, feedback endpoints
│   ├ urls.py              # Route definitions
│   └ templates/
│       └ viashnav_bot.html # Single-page chat UI
├ vaishnav_chatbot/
│   ├ settings.py          # Django settings (email, auth, DB)
│   ├ urls.py              # Root URL config
│   └ wsgi.py              # WSGI entry point
├ static/
│   ├ KB.txt               # Knowledge Base — system prompt & guardrails
│   ├ morpankh.svg         # Logo icon
│   └ morpankh.png         # Hero image
├ .env                     # Environment variables (not committed)
├ Procfile                 # Gunicorn deployment config
├ requirements.txt         # Python dependencies
└ manage.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Azure OpenAI API access (API key + endpoint)
- Gmail account with App Password (for OTP emails)

### 1. Clone & Install

```bash
git clone https://github.com/AnandShah10/vaishnav_gpt.git
cd vaishnav_gpt

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_azure_openai_api_key
ENDPOINT_URL=https://your-resource.openai.azure.com/
SECRET_KEY=your_django_secret_key
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

> **Note:** For Gmail, you need to generate an [App Password](https://support.google.com/accounts/answer/185833) (not your regular password). Enable 2-Step Verification first, then create an App Password under your Google Account security settings.

### 3. Run Migrations & Start

```bash
python manage.py migrate
python manage.py runserver 8001
```

Open **http://localhost:8001** in your browser.

---

## 🎨 UI Design

The interface follows a premium, light-themed aesthetic with glassmorphism:

- **Gradient background** with soft teal, green, and amber tones
- **Card-based learning path selector** with hover animations
- **Language toggle buttons** for English / Hindi / Gujarati
- **Localized greeting messages** per tradition and language
- **Two-step OTP login modal** (Email → OTP)
- **Pill-shaped suggestion chips** for quick prompts
- **Clean chat bubbles** with streaming animation and rich typography
- **Sticky top navbar** with tradition breadcrumb
- Fully **responsive** — works on desktop and mobile

---

## 📖 Supported Learning Paths

| Path | Focus |
|---|---|
| 🙏 **Universal Bhakti** | Core Vaishnava principles across all Sampradayas |
| 🪈 **Krishna Bhakti** | Radha-Krishna, Chaitanya, Gaudiya tradition |
| 🏹 **Rama Bhakti** | Lord Rama, Hanuman, Ramanandi tradition |
| 🎯 **Pushtimarg** | Shuddhadvaita, Shrinathji, Vallabhacharya |
| 🙏 **Nimbarka Bhakti** | Dvaitadvaita, Kumara Sampradaya |
| 📖 **Bhagavad Gita** | Chapter-by-chapter study of the Gita |
| 📚 **Srimad Bhagavatam** | Pastimes, philosophy, and devotional narratives |
| 🕉️ **Upanishads & Vedanta** | Brahman, Atman, and Vedantic philosophy |
| 🌐 **Vishnu Puran** | Cosmic cycles, avatars, and creation narratives |
| 📅 **Vaishnav Panchang** | Today's tithi, nakshatra, Ekadashi, festivals |

---

## 🔌 API Reference

### `POST /api/vaishnav-bot/`

Send a message to the bot. Supports streaming responses.

**Request Body:**
```json
{
  "message": "Explain Bhagavad Gita Chapter 2",
  "tradition": "gita",
  "language": "English"
}
```

**Response:** Streamed plain text (token by token). On the 3rd user message, the response includes the header `X-Show-Feedback: true` for mobile feedback trigger.

---

### `POST /api/send-otp/`

Send a one-time password to the user's email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "status": "success"
}
```

---

### `POST /api/verify-otp/`

Verify the OTP and receive a JWT token. Also creates a Django session.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi...",
  "username": "user@example.com"
}
```

---

### `GET /api/get-history/?tradition=gita`

Retrieve saved chat history for a specific tradition. Requires authenticated session.

**Response:**
```json
{
  "status": "success",
  "messages": [
    {"role": "user", "content": "What is Karma Yoga?"},
    {"role": "assistant", "content": "Karma Yoga is..."}
  ]
}
```

---

### `POST /api/submit-feedback/`

Submit user feedback with rating.

**Request Body:**
```json
{
  "name": "Anand",
  "phone": "9876543210",
  "email": "anand@example.com",
  "rating": 5
}
```

---

### `POST /api/logout/`

Ends the user's Django session.

---

## 📘 Knowledge Base

The bot's behavior is governed by `static/KB.txt`, which defines:

1. **Sampradaya Adaptability Protocol** — How to pivot responses per tradition
2. **Real-Time Ekadashi & Time Calculations** — Date-aware devotional guidance
3. **Scholarly Layer** — Philosophy (Gyan) and Rituals (Sadachara) expertise
4. **Behavioral Guardrails** — Accuracy-first policy with scriptural citations
5. **Panchang Protocol** — Traditional almanac responses that never refuse

---

## ☁️ Deployment (Azure)

The app is configured for Azure App Service via the `Procfile`:

```
web: gunicorn vaishnav_chatbot.wsgi --bind=0.0.0.0:$PORT
```

Static files are served via **WhiteNoise** middleware.

**Environment variables to set on the server:**
- `OPENAI_API_KEY`
- `ENDPOINT_URL`
- `SECRET_KEY`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

---

<p align="center">
  <em>Jai Shree Krishna! 🙏</em>
</p>
