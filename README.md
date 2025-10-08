# 🧠 TaxNerdGPT – Perpetual Life Planner

**TaxNerdGPT** is a full-stack AI-driven platform for life planning and tax strategy, featuring:

- 🧭 Interactive chat-based life planner (3-Day, 21-Day, Full)
- 📊 Personalized roadmap generation with Gemini AI
- 📬 Email delivery with PDF attachments
- 📈 Dashboard with charts and editable reminders
- 🔐 Login-gated access for premium tiers

---

## 📁 Project Structure

```
TaxNerdGPT/
├── backend/
│   ├── routers/
│   ├── services/
│   ├── history_logs/
│   └── reminder_logs/
├── frontend/
│   └── src/
│       ├── components/
│       ├── assets/
│       ├── App.js, App.css, index.js, Dashboard.css, etc.
├── TaxNerdGPT - CONSUMER PDF SHEET.pdf
├── requirements.txt
├── package.json
├── main.py
```

---

## 🚀 How to Run

### ✅ Backend (FastAPI)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn backend.main:app --reload
```

---

### ✅ Frontend (React)

```bash
cd frontend
npm install
npm start
```

---

## 🛠️ Features

- 📅 Plan selection: 3-day (free), 21-day (premium), full planner
- ✍️ Guided Q&A → AI-generated roadmap
- 📩 Email roadmap with branded PDF
- 🧠 Dashboard with:
  - 📜 Roadmap history
  - 🔔 Editable reminders
  - 📊 Charts: usage breakdown & growth
- 🔐 Login gate: only subscribers can access premium tools

---

## 📌 Tech Stack

| Layer     | Tech                     |
|-----------|--------------------------|
| Frontend  | React, Axios, Recharts   |
| Backend   | FastAPI, Uvicorn         |
| AI        | Google Gemini            |
| Email     | SMTP via `email_utils.py`|
| PDF       | `fpdf`                   |
| Storage   | JSON logs (user-level)   |

---

## 🔑 Env Variables (`.env`)

```
GOOGLE_API_KEY=your_google_api_key
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

---

## 👤 Built by Peete IT Consulting

> Scaling AI-driven tools for Memphis and beyond.