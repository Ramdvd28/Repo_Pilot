import pytest
from app.services.code_review_service import CodeReviewService


def test_parse_diff_modified_files():
    sample_diff = """diff --git a/app/main.py b/app/main.py
index 12345..67890 100644
--- a/app/main.py
+++ b/app/main.py
@@ -10,6 +10,7 @@
+print("debug log")
"""
    files = CodeReviewService.parse_diff_modified_files(sample_diff)
    assert len(files) == 1
    assert files[0] == "app/main.py"


@pytest.mark.asyncio
async def test_code_review_git_diff(db_session):
    reviewer = CodeReviewService(db_session)
    diff = """diff --git a/backend/app/auth.py b/backend/app/auth.py
--- a/backend/app/auth.py
+++ b/backend/app/auth.py
@@ -5,2 +5,2 @@
-if password == "admin":
+if password == user_provided_password:
"""
    review = await reviewer.review_git_diff("repo-123", diff)
    assert "score" in review
    assert "findings" in review
    assert isinstance(review["findings"], list)
