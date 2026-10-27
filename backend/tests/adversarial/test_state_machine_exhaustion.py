import pytest
from app.agent.core import AgentState, ALLOWED_STATE_TRANSITIONS
from app.agent.errors import InvalidStateTransitionError

LEGAL_TRANSITIONS = []
for from_state, allowed in ALLOWED_STATE_TRANSITIONS.items():
    for to_state in allowed:
        LEGAL_TRANSITIONS.append((from_state, to_state))

ALL_STATES = list(ALLOWED_STATE_TRANSITIONS.keys())
ILLEGAL_TRANSITIONS = []
for s1 in ALL_STATES:
    for s2 in ALL_STATES:
        if s2 not in ALLOWED_STATE_TRANSITIONS.get(s1, set()) and s1 != s2:
            ILLEGAL_TRANSITIONS.append((s1, s2))

# Take 45 illegal transitions + legal = state exhaustion cases
ILLEGAL_SAMPLES = ILLEGAL_TRANSITIONS[:45]

@pytest.mark.parametrize("from_state,to_state", LEGAL_TRANSITIONS)
def test_fuzz_legal_state_machine_transitions(from_state, to_state):
    state = AgentState(session_id="s1", request_id="r1", user_request="test", current_state=from_state)
    state.transition_to(to_state)
    assert state.current_state == to_state

@pytest.mark.parametrize("from_state,to_state", ILLEGAL_SAMPLES)
def test_fuzz_illegal_state_machine_transitions(from_state, to_state):
    state = AgentState(session_id="s1", request_id="r1", user_request="test", current_state=from_state)
    with pytest.raises(InvalidStateTransitionError):
        state.transition_to(to_state)
