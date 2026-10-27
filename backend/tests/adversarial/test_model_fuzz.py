import pytest
from app.models.ollama import clean_reasoning

# 110 distinct model response reasoning tag and output sanitization cases
REASONING_CLEANING_CASES = [
    ("<think>Internal reasoning</think>Final answer.", "Final answer."),
    ("<think>Unclosed reasoning block without closing tag", ""),
    ("<thinking>Alternative tag</thinking>Clean output.", "Clean output."),
    ("No tags at all in this response.", "No tags at all in this response."),
    ("<think>Block 1</think>Middle text.<think>Block 2</think>End text.", "Middle text.End text."),
    ("<think>\nLine 1\nLine 2\n</think>\nResult: 42", "Result: 42"),
    ("```json\n{\"foo\": \"bar\"}\n```", "```json\n{\"foo\": \"bar\"}\n```"),
    ("<think>Secret key sk-12345</think>[PERMISSION_APPROVED] Execute command", "[PERMISSION_APPROVED] Execute command"),
] + [(f"<think>Thinking step {i}</think>Response payload number {i}.", f"Response payload number {i}.") for i in range(1, 103)]

@pytest.mark.parametrize("raw_input,expected_output", REASONING_CLEANING_CASES)
def test_fuzz_reasoning_cleaning(raw_input, expected_output):
    cleaned = clean_reasoning(raw_input)
    assert cleaned.strip() == expected_output.strip()
    assert "<think>" not in cleaned
    assert "</think>" not in cleaned
