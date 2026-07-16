# 🚀 AI Resume Screening System (ATS Resume Analyzer)

An AI-powered Applicant Tracking System (ATS) Resume Analyzer built with **FastAPI**, **PostgreSQL**, **Redis**, **Docker**, and **NLP** to automate resume screening, candidate ranking, and recruiter workflows.

---

## 📖 Overview

The AI Resume Screening System helps recruiters efficiently evaluate resumes by extracting skills, analyzing candidate profiles, calculating ATS scores, and ranking applicants based on job requirements.

The project is designed using modern backend development practices, including Docker containerization, REST APIs, structured logging, automated testing, and CI/CD.

---

# ✨ Features

### Resume Processing

* Upload resumes (PDF/DOCX)
* Extract resume text
* NLP-based skill extraction
* Resume parsing
* ATS score calculation
* Job description matching
* Candidate ranking

### Recruiter Dashboard

* Recruiter login
* Resume management
* Candidate ranking
* Search candidates
* Filter applicants
* Resume analysis reports

### Backend Features

* FastAPI REST API
* Interactive Swagger Documentation
* JWT Authentication
* PostgreSQL Database
* Redis Integration
* Docker & Docker Compose
* Nginx Reverse Proxy
* Structured Logging
* Health Monitoring
* System Monitoring
* Automated Testing
* GitHub Actions CI

---

# 🛠 Tech Stack

## Backend

* Python 3.13
* FastAPI
* Uvicorn

## Database

* PostgreSQL

## Cache

* Redis

## AI / NLP

* spaCy
* TF-IDF
* Cosine Similarity

## Authentication

* JWT

## DevOps

* Docker
* Docker Compose
* Nginx
* GitHub Actions

## Testing

* Pytest

---

# 📁 Project Structure

```text
AI-Resume-Screening-System/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── static/
│   ├── templates/
│   └── main.py
│
├── tests/
├── nginx/
├── logs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .github/
    └── workflows/
```

---

# ⚙️ Installation

## Clone the Repository

```bash
git clone https://github.com/sayan1929U/AI-Resume-Screening-System.git
```

```bash
cd AI-Resume-Screening-System
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

```bash
uvicorn app.main:app --reload
```

Application

```
http://localhost:8000
```

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# 🐳 Docker

Build and start services:

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

---

# 🔌 API Endpoints

| Method | Endpoint         | Description           |
| ------ | ---------------- | --------------------- |
| GET    | `/`              | Home Page             |
| GET    | `/docs`          | Swagger Documentation |
| GET    | `/health`        | Application Health    |
| GET    | `/system`        | System Metrics        |
| POST   | `/api/upload`    | Upload Resume         |
| POST   | `/api/login`     | User Login            |
| GET    | `/api/recruiter` | Recruiter Dashboard   |

---

# 📊 Monitoring

### Health Endpoint

```text
GET /health
```

Returns application status and version.

### System Monitoring

```text
GET /system
```

Displays:

* CPU Usage
* Memory Usage
* Disk Usage

### Logging

Application logs are stored in:

```text
logs/app.log
```

---

# 🧪 Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

Generate HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

---

# 🚀 CI/CD

GitHub Actions automatically runs the test suite on every push and pull request.

Workflow location:

```text
.github/workflows/tests.yml
```

---

# 🔒 Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=your_redis_url
```

Do **not** commit your `.env` file to GitHub.

---

# 📌 Future Improvements

* AWS S3 File Storage
* AWS EC2 Deployment
* Prometheus Metrics
* Grafana Dashboard
* Kubernetes Deployment
* Elasticsearch Integration
* Email Notifications
* AI-Based Resume Recommendations
* Admin Dashboard
* Role-Based Access Control (RBAC)

---

# 👨‍💻 Author

**Sayan Dey**

B.Tech CSE (AI & ML)

Brainware University

GitHub: https://github.com/sayan1929U

---

# ⭐ Support

If you found this project helpful, consider giving it a **⭐ Star** on GitHub.

It helps others discover the project and supports future development.
