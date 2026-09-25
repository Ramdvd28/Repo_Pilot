# RepoPilot AI - Local Development Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ and `npm`
- Docker and Docker Compose
- Git

## Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/RepoPilot-AI.git
   cd RepoPilot-AI
   ```

2. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```

3. **Start PostgreSQL Vector Database**
   ```bash
   docker-compose up -d db
   ```

4. **Run Backend Service**
   ```bash
   cd backend
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Unix: source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

5. **Run Frontend App**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. Open `http://localhost:3000` in your browser.
