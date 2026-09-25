# RepoPilot AI - REST API Documentation

Base URL: `http://localhost:8000/api/v1`

## Endpoints

### 1. Health Check
- **`GET /health`**
- Response:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-09-17T14:25:00Z",
    "database": "connected"
  }
  ```

### 2. Analyze Repository Metadata
- **`POST /repos/analyze`**
- Body:
  ```json
  {
    "github_url": "https://github.com/fastapi/fastapi"
  }
  ```
- Response (200 OK):
  ```json
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "github_url": "https://github.com/fastapi/fastapi",
    "owner": "fastapi",
    "name": "fastapi",
    "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production",
    "stars": 75000,
    "forks": 6200,
    "open_issues": 120,
    "default_branch": "master",
    "primary_language": "Python",
    "languages": {"Python": 98.5, "HTML": 1.5},
    "topics": ["fastapi", "python", "asyncio", "pydantic"],
    "created_at": "2018-12-05T00:00:00Z",
    "updated_at": "2026-09-17T00:00:00Z",
    "analyzed_at": "2026-09-17T14:25:00Z"
  }
  ```

### 3. Get Repository Details
- **`GET /repos/{repo_id}`**
- Returns stored metadata for the analyzed repository by ID.
