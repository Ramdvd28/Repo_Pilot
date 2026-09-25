# Contributing to RepoPilot AI

Thank you for your interest in contributing to RepoPilot AI! We welcome contributions to help make open-source codebases more accessible and developer-friendly.

## Development Setup

1. **Fork & Clone**
   ```bash
   git clone https://github.com/your-username/RepoPilot-AI.git
   cd RepoPilot-AI
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```

3. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pytest
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Docker Compose Setup (Recommended)**
   ```bash
   docker-compose up --build
   ```

## Pull Request Guidelines

- Ensure tests pass before opening a PR.
- Follow existing code formatting conventions (Ruff/Black for Python, Prettier/ESLint for TypeScript).
- Keep PR descriptions clear and detailed.
