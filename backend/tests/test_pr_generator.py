import pytest
from app.services.pr_generator_service import PrGeneratorService


@pytest.mark.asyncio
async def test_pr_generator_service():
    generator = PrGeneratorService()
    diff = """diff --git a/app/main.py b/app/main.py
+add_middleware(CORSMiddleware)
"""
    pr_data = await generator.generate_pr_description(
        git_diff=diff,
        issue_number=42,
        test_results="pytest 12 passed in 0.5s"
    )

    assert "title" in pr_data
    assert "markdown_description" in pr_data
    assert len(pr_data["markdown_description"]) > 20
