import re
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_provider
from app.rag.vector_store import VectorStoreService


class CodeReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_provider = get_ai_provider()
        self.vector_store = VectorStoreService(db)

    @staticmethod
    def parse_diff_modified_files(git_diff: str) -> List[str]:
        """
        Extracts modified file paths from git diff header lines (e.g. diff --git a/file b/file).
        """
        matches = re.findall(r"diff --git a/(.*?) b/(.*?)$", git_diff, re.MULTILINE)
        if matches:
            return list(set([m[1] for m in matches]))
        
        # Fallback simple line scan for +++ b/filepath
        plus_matches = re.findall(r"^\+\+\+ b/(.*?)$", git_diff, re.MULTILINE)
        return list(set(plus_matches))

    async def review_git_diff(
        self,
        repository_id: str,
        git_diff: str,
        issue_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Performs comprehensive AI Code Review over a git diff payload.
        Categorizes findings into 'error', 'warning', and 'info' severities.
        """
        modified_files = self.parse_diff_modified_files(git_diff)

        # Context retrieval for modified files
        context_chunks = await self.vector_store.search_relevant_chunks(
            repository_id=repository_id,
            query=f"code review diff {' '.join(modified_files)}",
            top_k=4
        )
        context_str = "\n".join([f"[{c.file_path}]: {c.content[:200]}" for c in context_chunks])

        prompt = (
            f"Git Diff to Review:\n"
            f"```diff\n{git_diff[:4000]}\n```\n\n"
            f"Repository Context:\n{context_str}\n\n"
            f"Perform a strict, expert software engineering code review on this git diff for:\n"
            f"1. Correctness & potential bugs\n"
            f"2. Security vulnerabilities\n"
            f"3. Performance & memory considerations\n"
            f"4. Error handling & edge cases\n"
            f"5. Project consistency & maintainability\n\n"
            f"Return structured JSON format with:\n"
            f"- 'score': integer from 0 to 100\n"
            f"- 'summary': overall summary string\n"
            f"- 'findings': array of objects containing:\n"
            f"  - 'severity': 'error' | 'warning' | 'info'\n"
            f"  - 'file_path': file path string\n"
            f"  - 'line_number': line number integer (or null)\n"
            f"  - 'explanation': explanation string\n"
            f"  - 'suggested_fix': code fix replacement snippet\n"
        )

        ai_response = await self.ai_provider.generate_text(
            prompt=prompt,
            system_prompt="You are a principal software engineer performing an automated code review. Respond accurately and identify real issues.",
            temperature=0.1,
            max_tokens=1500
        )

        # Try parsing JSON response from AI
        try:
            # Extract JSON block if wrapped in markdown code fence
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", ai_response, re.DOTALL)
            raw_json = json_match.group(1) if json_match else ai_response
            data = json.loads(raw_json.strip())
            return {
                "score": data.get("score", 85),
                "summary": data.get("summary", "Code review completed successfully."),
                "findings": data.get("findings", [])
            }
        except Exception:
            # Fallback formatted review if model returned prose instead of raw JSON
            return {
                "score": 85,
                "summary": "AI Code Review completed.",
                "findings": [
                    {
                        "severity": "info",
                        "file_path": modified_files[0] if modified_files else "Diff File",
                        "line_number": 1,
                        "explanation": ai_response[:300],
                        "suggested_fix": "// Verify error handling and unit test coverage"
                    }
                ]
            }
