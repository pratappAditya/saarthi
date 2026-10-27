import pytest
from app.agent.errors import SaarthiError, ErrorCategory, InvalidStateTransitionError

def test_saarthi_error_sanitization():
    err = SaarthiError(
        category=ErrorCategory.MODEL_TIMEOUT,
        message="Internal timeout connection at 127.0.0.1:11434 with traceback..."
    )
    assert err.category == ErrorCategory.MODEL_TIMEOUT
    # User message must be sanitized
    assert err.user_message == "The request timed out while communicating with the local AI model."
    assert "127.0.0.1" not in err.user_message
    assert "traceback" not in err.user_message

    as_dict = err.to_dict()
    assert as_dict["code"] == "MODEL_TIMEOUT"
    assert as_dict["message"] == "The request timed out while communicating with the local AI model."

def test_invalid_state_transition_error():
    err = InvalidStateTransitionError("IDLE", "EXECUTING_TOOL")
    assert err.category == ErrorCategory.INTERNAL_ERROR
    assert err.current_state == "IDLE"
    assert err.target_state == "EXECUTING_TOOL"
    assert "Invalid state transition" in err.message
