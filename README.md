<p align="center">
  <span style="font-size: 64px;">ॐ</span>
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

## 🌸 Overview

**Vaishnav GPT** is an AI chatbot built on Django and Azure OpenAI that serves as an authoritative, devotional guide to Vaishnava theology. It adapts its responses based on the user's chosen tradition (Sampradaya), providing contextually accurate answers grounded in scriptures like the Bhagavad Gita, Srimad Bhagavatam, and tradition-specific texts.

### ✨ Key Features

- **Sampradaya-Adaptive Responses** — Tailors philosophical vocabulary, scriptural citations, and ritual guidance to the user's selected tradition
- **5 Tradition Modes** — Universal Bhakti, Krishna Bhakti (Gaudiya), Rama Bhakti (Ramanandi), Pushtimarg (Vallabhacharya), and Nimbarka Bhakti
- **Rich Markdown Rendering** — Bot responses display with proper headings, bulleted/numbered lists, bold text, and paragraph spacing
- **Session-Based Chat History** — Maintains conversation context per tradition within a session
- **Conversation Logging** — All messages are stored in the database for analytics
- **Real-Time Panchang Awareness** — Provides date-contextual devotional guidance

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 6.0 (WSGI) |
| **AI Engine** | Azure OpenAI — GPT-4o-mini |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Fonts** | Inter, Playfair Display (Google Fonts) |
| **Deployment** | Azure App Service / Gunicorn |

---

## 📂 Project Structure

```
vaishnav_gpt/
├── bot/
│   ├── models.py            # Message model for conversation logging
│   ├── views.py             # API endpoint + markdown-to-HTML converter
│   ├── urls.py              # Route definitions
│   └── templates/
│       └── viashnav_bot.html  # Single-page chat UI
├── vaishnav_chatbot/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL config
│   └── wsgi.py              # WSGI entry point
├── static/
│   └── KB.txt               # Knowledge Base — system prompt & guardrails
├── .env                     # Environment variables (not committed)
├── Procfile                 # Gunicorn deployment config
├── requirements.txt         # Python dependencies
└── manage.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Azure OpenAI API access (API key + endpoint)

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
```

### 3. Run Migrations & Start

```bash
python manage.py migrate
python manage.py runserver
```

Open **http://localhost:8000** in your browser.

---

## 🎨 UI Design

The interface follows a warm, earthy aesthetic inspired by traditional Vaishnava art:

- **Warm beige gradient** background with brown accents
- **Card-based tradition selector** on the landing screen
- **Pill-shaped suggestion chips** for quick prompts
- **Clean chat bubbles** with rich typography (headings, lists, bold text)
- **Sticky top navbar** with tradition breadcrumb
- Fully **responsive** — works on desktop and mobile

---

## 🛕 Supported Traditions

| Tradition | Sampradaya | Focus |
|---|---|---|
| 🌍 **Universal Bhakti** | All four Sampradayas | Core Vaishnava principles |
| 🐄 **Krishna Bhakti** | Brahma (Gaudiya) | Radha-Krishna, Chaitanya, Bhagavatam |
| 🏹 **Rama Bhakti** | Sri (Ramanandi) | Lord Rama, Hanuman, Vishishtadvaita |
| 🌺 **Pushtimarg** | Rudra (Vallabhacharya) | Shuddhadvaita, Shrinathji Sewa |
| 🌼 **Nimbarka Bhakti** | Kumara (Nimbarka) | Dvaitadvaita, Radha-Krishna |

---

## 🔧 API Reference

### `POST /api/vaishnav-bot/`

Send a message to the bot.

**Request Body:**
```json
{
  "message": "Explain Bhagavad Gita Chapter 2",
  "tradition": "krishna"
}
```

**Response:**
```json
{
  "reply": "<h3>Sankhya Yoga</h3><p>Chapter 2 of the Bhagavad Gita...</p>",
  "tradition": "krishna"
}
```

### `GET /`

Serves the chat UI. Flushes the session to start a fresh conversation.

---

## 📜 Knowledge Base

The bot's behavior is governed by `static/KB.txt`, which defines:

1. **Sampradaya Adaptability Protocol** — How to pivot responses per tradition
2. **Real-Time Ekadashi & Time Calculations** — Date-aware devotional guidance
3. **Scholarly Layer** — Philosophy (Gyan) and Rituals (Sadachara) expertise
4. **Behavioral Guardrails** — Accuracy-first policy with scriptural citations
5. **Panchang Protocol** — Traditional almanac responses that never refuse

---

## 🚢 Deployment (Azure)

The app is configured for Azure App Service via the `Procfile`:

```
web: gunicorn vaishnav_chatbot.wsgi --bind=0.0.0.0:$PORT
```

Static files are served via **WhiteNoise** middleware.

---

<p align="center">
  <em>Jai Shree Krishna! 🙏</em>
</p>
