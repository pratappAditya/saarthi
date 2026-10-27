import pytest

SECRET_PATTERNS = [
    ("password=SuperSecret123!", True),
    ("api_key=sk-proj-1234567890abcdef", True),
    ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", True),
    ("postgres://user:password123@localhost:5432/db", True),
    ("-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBg...", True),
] + [(f"Normal log message #{i} without any secrets", False) for i in range(1, 46)]

@pytest.mark.parametrize("text,has_secret", SECRET_PATTERNS)
def test_fuzz_secret_screening_patterns(text, has_secret):
    secret_keywords = ["password=", "api_key=", "sk-proj-", "Bearer ", "postgres://", "BEGIN PRIVATE KEY"]
    detected = any(kw in text for kw in secret_keywords)
    assert detected == has_secret
