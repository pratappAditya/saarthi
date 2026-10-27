import pytest
import time
from app.agent.core import AgentState
from app.agent.errors import InvalidStateTransitionError

def test_agent_state_initialization():
    state = AgentState(
        session_id="sess-1",
        request_id="req-1",
        user_request="Hello"
    )
    assert state.current_state == "IDLE"
    assert len(state.state_history) == 1
    assert state.state_history[0]["state"] == "IDLE"
    assert state.created_at is not None
    assert state.updated_at is not None

def test_valid_state_transitions():
    state = AgentState(
        session_id="sess-1",
        request_id="req-1",
        user_request="Hello"
    )
    state.transition_to("RUNNING")
    assert state.current_state == "RUNNING"

    state.transition_to("WAITING_MODEL")
    assert state.current_state == "WAITING_MODEL"

    state.transition_to("WAITING_TOOL")
    assert state.current_state == "WAITING_TOOL"

    state.transition_to("EXECUTING_TOOL")
    assert state.current_state == "EXECUTING_TOOL"

    state.transition_to("RUNNING")
    assert state.current_state == "RUNNING"

    state.transition_to("WAITING_MODEL")
    state.transition_to("COMPLETED")
    assert state.current_state == "COMPLETED"
    assert state.completion_state == "success"

def test_idempotent_transitions():
    state = AgentState(
        session_id="sess-1",
        request_id="req-1",
        user_request="Hello"
    )
    state.transition_to("RUNNING")
    hist_len = len(state.state_history)
    # Repeating transition to current state is a safe no-op
    state.transition_to("RUNNING")
    assert len(state.state_history) == hist_len

def test_invalid_state_transitions_raise_error():
    state = AgentState(
        session_id="sess-1",
        request_id="req-1",
        user_request="Hello"
    )
    # Direct transition from IDLE to EXECUTING_TOOL is invalid
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        state.transition_to("EXECUTING_TOOL")
    assert exc_info.value.current_state == "IDLE"
    assert exc_info.value.target_state == "EXECUTING_TOOL"
