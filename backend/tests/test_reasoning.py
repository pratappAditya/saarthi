import pytest
import sqlite3
import os
from app.models.ollama import clean_reasoning
from app.memory.sqlite import SQLiteMemoryProvider

# --- 1. Test clean_reasoning function ---
def test_clean_reasoning_with_tags():
    # Response with <think>...</think>
    assert clean_reasoning("<think>We should greet the user.</think>Hello there!") == "Hello there!"
    # Response with <thinking>...</thinking>
    assert clean_reasoning("<thinking>r1</thinking>Hi!") == "Hi!"

def test_clean_reasoning_without_reasoning():
    # Response without reasoning
    assert clean_reasoning("Just a normal text response.") == "Just a normal text response."

def test_clean_reasoning_multiple_blocks():
    # Response containing multiple reasoning blocks
    text = "<think>r1</think>Hello <think>r2</think>world!"
    assert clean_reasoning(text) == "Hello world!"
    
    text_mix = "Thinking... r1 ...done thinking. Hello! Thinking... r2 ...done thinking. How can I help?"
    assert clean_reasoning(text_mix) == "Hello!  How can I help?"

def test_clean_reasoning_only_reasoning():
    # Response containing only reasoning
    assert clean_reasoning("<think>only reasoning here</think>") == ""
    assert clean_reasoning("Thinking...\ninternal monologue\n...done thinking.") == ""

def test_clean_reasoning_word_thinking():
    # Normal text containing the word "thinking" but not a reasoning block
    assert clean_reasoning("I am thinking about your request.") == "I am thinking about your request."
    assert clean_reasoning("This is thinking of a fast approach.") == "This is thinking of a fast approach."

def test_clean_reasoning_unclosed_tags():
    # Unclosed tag at the end
    assert clean_reasoning("<think>reasoning without end tag") == ""
    assert clean_reasoning("Hello! <think>thinking forever") == "Hello!"
    assert clean_reasoning("<thinking>unclosed thinking tag") == ""

def test_clean_reasoning_thinking_done_thinking():
    # Standard format from live test
    text = "Thinking...\nWe need to respond. The user says \"hello\". So we respond politely.\n...done thinking.\n\nHello! How can I help you today?"
    assert clean_reasoning(text) == "Hello! How can I help you today?"


# --- 2. Test SQLite chronological get_messages ---
@pytest.mark.anyio
async def test_sqlite_get_messages_chronological(tmp_path):
    db_file = os.path.join(tmp_path, "test_history.db")
    provider = SQLiteMemoryProvider(db_file)
    
    session_id = "test_seq_session"
    
    # Add 12 messages to verify that it limits correctly and retains correct chronological order
    # (Since settings.MAX_HISTORY_MESSAGES is 8, or limit is specified, let's use limit=8)
    for i in range(12):
        sender = "user" if i % 2 == 0 else "assistant"
        message = f"Msg {i}"
        await provider.add_message(session_id, sender, message)
        
    # Get messages with limit of 8
    history = await provider.get_messages(session_id, limit=8)
    
    assert len(history) == 8
    # The returned messages should be the LATEST 8 (messages 4 to 11), in CHRONOLOGICAL order
    # chronological means Msg 4 should be first, and Msg 11 should be last
    assert history[0]["message"] == "Msg 4"
    assert history[-1]["message"] == "Msg 11"
    assert history[0]["sender"] == "user"
    assert history[1]["sender"] == "assistant"
