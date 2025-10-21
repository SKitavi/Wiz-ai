# 🧠 WizAI: Intelligent Academic Assistant

> **WizAI** is an intelligent backend system that goes beyond ChatGPT — designed to help students *organize, plan, and automate* their academic life through intelligent agents and seamless integrations.

---

## Project Overview

### Vision
WizAI is an intelligent backend system that goes beyond ChatGPT by actively organizing student life through:

- **📚 Portal Integration** — Auto-fetches assignments and deadlines from school portals  
- **🧾 Document Intelligence** — Extracts info from screenshots/PDFs to build actionable plans  
- **📅 Calendar Sync** — Bi-directional Google Calendar integration for seamless scheduling  
- **💬 Conversational Planning** — Natural language interface to view, edit, and manage schedules  
- **🤖 Multi-Agent Orchestration** — Specialized agents for planning, extraction, and assistance  
- **⚡ Proactive Automation** — Context-aware suggestions and intelligent workflow triggers  

---

## 💡 Problem Statement
Students struggle with fragmented information across multiple platforms (school portals, email, calendar, and documents).  
Manual organization is **time-consuming** and **error-prone**.  

**WizAI** solves this by creating an intelligent backend that automatically aggregates, processes, and organizes academic life through **AI-powered agents and automation**.  

---
## 🚀 Live Demo
- **Hosted on Streamlit Cloud**: https://wizai-version1.streamlit.app/

---

## 📸 Screenshots & Workflows

### 🖥️ Application Screens

<p align="center">
  <img src="./assets/homepage.png" alt="WizAI Homepage" width="800"/>
  <br/>
  <em>WizAI Home — Dashboard Overview</em>
</p>

<p align="center">
  <img src="./assets/task_manager.png" alt="Tasks Page" width="800"/>
  <br/>
  <em>Task Manager</em>
</p>

---

### ⚙️ n8n Workflows
<p align="center">
  <img src="./assets/daily_schedule_generation.png" alt="n8n Workflow - Generate daily schedule" width="800"/>
  <br/>
  <em>n8n Workflow 1 - Daily schedule generation </em>
</p>

<p align="center">
  <img src="./assets/deadline_reminder.png" alt="n8n Workflow - Deadline reminder" width="800"/>
  <br/>
  <em>n8n Workflow 2 — Deadline reminders</em>
</p>

<p align="center">
  <img src="./assets/new_task_notification.png" alt="n8n Workflow - New task notification" width="800"/>
  <br/>
  <em>n8n Workflow 3 — New task notifications</em>
</p>

## 🏗️ Tech Stack

| Layer | Tools / Libraries |
|-------|-------------------|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Database** | PostgreSQL + SQLAlchemy ORM |
| **Authentication** | JWT + OAuth2 (via `python-jose`, `passlib`) |
| **AI Integration** | OpenAI API, LangChain (planned) |
| **Environment Management** | Pydantic Settings + `.env` |
| **Logging** | Loguru |
| **Deployment (planned)** | Docker + Render / Railway / AWS |

---

## 📂 Project Structure
```python 
wizai/
├── backend/
│ └── app/
│ ├── main.py
│ ├── models/
│ ├── routers/
│ ├── schemas/
│ ├── core/
│ └── utils/
├── venv/
├── .env.example
├── .gitignore
└── README.md
```

---

### ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/Wiz-ai.git
cd Wiz-ai
```
### 2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Running the Application

### Start Backend:
```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (in separate terminal):
```bash
cd wiz-ai
source venv/bin/activate
streamlit run frontend/streamlit_app.py
```

### Access the Application:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 Future Enhancements
- Document OCR for automatic task extraction
- Google Calendar integration
- n8n workflow automation

## 🧍‍♀️ Author

**Sharon Kitavi**  
*Data Scientist · Community & Innovation Leader · Cofounder — Building Creative Solutions*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sharonkitavi)  

---

## 🪄 License

This project is licensed under the [MIT License](LICENSE).

---

> *“Intelligence is not just answering questions — it’s anticipating needs.”* ✨
