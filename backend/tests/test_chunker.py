from app.services.chunker_service import CodeChunkerService


def test_chunker_small_file():
    chunker = CodeChunkerService(max_chunk_lines=10, overlap_lines=2)
    content = "\n".join([f"line_{i}" for i in range(1, 15)])
    
    chunks = chunker.chunk_file_content(content, "test.py", "Python")
    assert len(chunks) == 2
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 10
    assert chunks[1]["start_line"] == 9
    assert chunks[1]["end_line"] == 14


def test_chunker_symbol_detection():
    chunker = CodeChunkerService()
    content = """class UserAuthenticationService:
    def __init__(self):
        pass

    def login(self, username, password):
        return True
"""
    chunks = chunker.chunk_file_content(content, "auth.py", "Python")
    assert len(chunks) == 1
    assert chunks[0]["symbol_name"] == "UserAuthenticationService"
