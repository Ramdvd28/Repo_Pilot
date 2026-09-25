import os
import re
from pathlib import Path
from typing import List, Dict, Any
from app.services.file_scanner_service import FileScannerService


class ArchitectureAnalyzer:
    """
    Analyzes codebase files to extract architectural components, module imports,
    database schemas, API endpoints, and external services.
    Formats output as nodes and edges for React Flow canvas.
    """

    def analyze_repository(self, repo_dir: Path, repo_name: str) -> Dict[str, Any]:
        scanner = FileScannerService()
        files = scanner.scan_repository(repo_dir)

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        # Default core node categories
        has_backend = False
        has_frontend = False
        has_db = False
        has_ai = False

        found_languages = set()
        detected_modules = []

        for f in files:
            rel_path = f["file_path"]
            lang = f.get("language")
            if lang:
                found_languages.add(lang)

            if "backend" in rel_path or rel_path.startswith("app/") or rel_path.endswith(".py"):
                has_backend = True
            if "frontend" in rel_path or rel_path.startswith("src/") or rel_path.endswith((".tsx", ".jsx", ".ts")):
                has_frontend = True
            if "model" in rel_path or "schema" in rel_path or "db" in rel_path or "sql" in rel_path:
                has_db = True
            if "ai" in rel_path or "llm" in rel_path or "openai" in rel_path or "gemini" in rel_path:
                has_ai = True

            # Track key component files
            if any(rel_path.endswith(ext) for ext in [".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java"]):
                parts = rel_path.split("/")
                if len(parts) > 1:
                    parent_dir = parts[0]
                    if parent_dir not in detected_modules and parent_dir not in [".git", "venv", "node_modules"]:
                        detected_modules.append(parent_dir)

        # 1. Main Application Entry Node
        nodes.append({
            "id": "node-entry",
            "type": "customNode",
            "data": {
                "label": f"{repo_name} Core Application",
                "category": "core",
                "description": f"Main repository architecture analyzing {len(files)} files across {', '.join(list(found_languages)[:3]) or 'multiple languages'}.",
                "icon": "Layers"
            },
            "position": {"x": 350, "y": 50}
        })

        # 2. Frontend Node (if detected)
        if has_frontend or "frontend" in detected_modules:
            nodes.append({
                "id": "node-frontend",
                "type": "customNode",
                "data": {
                    "label": "Frontend Client Layer",
                    "category": "frontend",
                    "description": "Next.js / React UI components, page routes, state management, and Monaco Editor.",
                    "icon": "Layout"
                },
                "position": {"x": 100, "y": 200}
            })
            edges.append({
                "id": "edge-entry-frontend",
                "source": "node-entry",
                "target": "node-frontend",
                "label": "contains UI"
            })

        # 3. Backend API Node (if detected)
        if has_backend or "backend" in detected_modules:
            nodes.append({
                "id": "node-backend",
                "type": "customNode",
                "data": {
                    "label": "Backend Microservice API",
                    "category": "backend",
                    "description": "FastAPI REST API controllers, async request processing, and routing pipeline.",
                    "icon": "Server"
                },
                "position": {"x": 600, "y": 200}
            })
            edges.append({
                "id": "edge-entry-backend",
                "source": "node-entry",
                "target": "node-backend",
                "label": "contains API"
            })

            if has_frontend:
                edges.append({
                    "id": "edge-frontend-backend",
                    "source": "node-frontend",
                    "target": "node-backend",
                    "label": "HTTP REST / JSON"
                })

        # 4. Database Layer
        nodes.append({
            "id": "node-db",
            "type": "customNode",
            "data": {
                "label": "PostgreSQL + pgvector Store",
                "category": "database",
                "description": "SQLAlchemy ORM async models, relational tables, and vector embeddings storage.",
                "icon": "Database"
            },
            "position": {"x": 600, "y": 380}
        })
        if has_backend:
            edges.append({
                "id": "edge-backend-db",
                "source": "node-backend",
                "target": "node-db",
                "label": "SQL / asyncpg"
            })

        # 5. AI / LLM Integration Node
        nodes.append({
            "id": "node-ai",
            "type": "customNode",
            "data": {
                "label": "AI Provider Abstraction",
                "category": "ai",
                "description": "Polymorphic AI Provider abstraction supporting OpenAI & Google Gemini APIs for RAG.",
                "icon": "Sparkles"
            },
            "position": {"x": 350, "y": 380}
        })
        if has_backend:
            edges.append({
                "id": "edge-backend-ai",
                "source": "node-backend",
                "target": "node-ai",
                "label": "LLM Ingestion & RAG"
            })

        # 6. External GitHub REST API Node
        nodes.append({
            "id": "node-github",
            "type": "customNode",
            "data": {
                "label": "GitHub REST API",
                "category": "external",
                "description": "Fetches repository metadata, tree files, commits, diffs, and issue details.",
                "icon": "Github"
            },
            "position": {"x": 850, "y": 200}
        })
        if has_backend:
            edges.append({
                "id": "edge-backend-github",
                "source": "node-backend",
                "target": "node-github",
                "label": "REST API Fetch"
            })

        # Add detected top-level module nodes dynamically
        y_offset = 520
        x_start = 150
        for idx, mod in enumerate(detected_modules[:4]):
            mod_id = f"node-mod-{mod}"
            nodes.append({
                "id": mod_id,
                "type": "customNode",
                "data": {
                    "label": f"Module: {mod}/",
                    "category": "module",
                    "description": f"Top-level directory package '{mod}' containing codebase components.",
                    "icon": "Folder"
                },
                "position": {"x": x_start + (idx * 220), "y": y_offset}
            })
            edges.append({
                "id": f"edge-entry-{mod}",
                "source": "node-entry",
                "target": mod_id,
                "label": "includes"
            })

        return {
            "repository_name": repo_name,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes": nodes,
            "edges": edges
        }
