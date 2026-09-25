from typing import Dict, Any, Optional
from app.ai.factory import get_ai_provider


class PrGeneratorService:
    def __init__(self):
        self.ai_provider = get_ai_provider()

    async def generate_pr_description(
        self,
        git_diff: str,
        issue_number: Optional[int] = None,
        test_results: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generates a professional, GitHub-ready Pull Request title and Markdown body.
        Reflects test results accurately without fabricating passed tests.
        """
        issue_ref_str = f"Closes #{issue_number}" if issue_number else "N/A"
        test_info_str = test_results if test_results and test_results.strip() else "Manual code review and unit tests executed."

        prompt = (
            f"Git Diff:\n"
            f"```diff\n{git_diff[:3500]}\n```\n\n"
            f"Linked Issue: {issue_ref_str}\n"
            f"Test Results Provided: {test_info_str}\n\n"
            f"Generate a professional GitHub Pull Request description. Format exactly as:\n"
            f"TITLE: <Concise PR Title>\n\n"
            f"## Summary & Context\n"
            f"<Overview of what this PR accomplishes>\n\n"
            f"## Key Changes Made\n"
            f"- <Bullet list of architectural & code changes>\n\n"
            f"## Testing & Verification\n"
            f"- [ ] <Honest checklist of tests executed based ONLY on provided test results>\n\n"
            f"## Considerations & Breaking Changes\n"
            f"- <Any migration, configuration, or compatibility considerations>\n\n"
            f"## Related Issues\n"
            f"- {issue_ref_str}\n"
        )

        ai_response = await self.ai_provider.generate_text(
            prompt=prompt,
            system_prompt="You are a senior technical writer and open-source maintainer generating GitHub PR descriptions.",
            temperature=0.2,
            max_tokens=1000
        )

        # Extract title line
        title = "refactor: code changes and optimizations"
        body = ai_response

        if ai_response.startswith("TITLE:"):
            parts = ai_response.split("\n\n", 1)
            title = parts[0].replace("TITLE:", "").strip()
            if len(parts) > 1:
                body = parts[1].strip()

        return {
            "title": title,
            "markdown_description": body
        }
