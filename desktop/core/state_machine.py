"""
Desktop State Machine.
Maintains state for the floating companion interaction lifecycle:
IDLE -> READY -> LISTENING -> PROCESSING -> THINKING -> COMPLETED -> ERROR.
Ensures Phase 3 voice unavailability is clearly reflected in state metadata.
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any, List
import logging
import datetime

logger = logging.getLogger("SaarthiDesktop.StateMachine")


class DesktopInteractionState(str, Enum):
    IDLE = "IDLE"
    READY = "READY"
    LISTENING = "LISTENING"  # State exposed for Phase 2 voice; in Phase 3, flags voice as unavailable
    PROCESSING = "PROCESSING"
    THINKING = "THINKING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


VALID_TRANSITIONS = {
    DesktopInteractionState.IDLE: [
        DesktopInteractionState.READY,
        DesktopInteractionState.ERROR
    ],
    DesktopInteractionState.READY: [
        DesktopInteractionState.LISTENING,
        DesktopInteractionState.PROCESSING,
        DesktopInteractionState.THINKING,
        DesktopInteractionState.IDLE,
        DesktopInteractionState.ERROR
    ],
    DesktopInteractionState.LISTENING: [
        DesktopInteractionState.PROCESSING,
        DesktopInteractionState.READY,
        DesktopInteractionState.IDLE,
        DesktopInteractionState.ERROR
    ],
    DesktopInteractionState.PROCESSING: [
        DesktopInteractionState.THINKING,
        DesktopInteractionState.COMPLETED,
        DesktopInteractionState.ERROR,
        DesktopInteractionState.IDLE
    ],
    DesktopInteractionState.THINKING: [
        DesktopInteractionState.COMPLETED,
        DesktopInteractionState.ERROR,
        DesktopInteractionState.IDLE
    ],
    DesktopInteractionState.COMPLETED: [
        DesktopInteractionState.IDLE,
        DesktopInteractionState.READY
    ],
    DesktopInteractionState.ERROR: [
        DesktopInteractionState.IDLE,
        DesktopInteractionState.READY
    ]
}


class DesktopStateMachine:
    def __init__(self, initial_state: DesktopInteractionState = DesktopInteractionState.IDLE):
        self._current_state = initial_state
        self._previous_state: Optional[DesktopInteractionState] = None
        self._status_message: str = "Saarthi Desktop Ready"
        self._error_detail: Optional[str] = None
        self._listeners: List[Callable[[DesktopInteractionState, Dict[str, Any]], None]] = []
        self._state_data: Dict[str, Any] = {}
        self._last_transition_time = datetime.datetime.now(datetime.timezone.utc)

    @property
    def current_state(self) -> DesktopInteractionState:
        return self._current_state

    @property
    def status_message(self) -> str:
        return self._status_message

    @property
    def error_detail(self) -> Optional[str]:
        return self._error_detail

    def add_listener(self, callback: Callable[[DesktopInteractionState, Dict[str, Any]], None]):
        """Registers a callback for state change events."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[DesktopInteractionState, Dict[str, Any]], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def transition_to(
        self,
        new_state: DesktopInteractionState,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Executes a validated state transition and notifies all registered listeners.
        """
        if new_state == self._current_state:
            # Update data/message without full transition if state unchanged
            if message:
                self._status_message = message
            if data:
                self._state_data.update(data)
            return True

        allowed = VALID_TRANSITIONS.get(self._current_state, [])
        if new_state not in allowed:
            logger.warning(
                f"Invalid state transition attempted: {self._current_state} -> {new_state}. Allowed: {allowed}"
            )
            return False

        self._previous_state = self._current_state
        self._current_state = new_state
        self._last_transition_time = datetime.datetime.now(datetime.timezone.utc)

        # In Phase 3, if LISTENING is entered, explicitly annotate that voice engine is coming soon
        if new_state == DesktopInteractionState.LISTENING:
            self._status_message = message or "Voice Engine (Phase 2) coming soon. Ready for text interaction."
            if data is None:
                data = {}
            data["voice_engine_status"] = "COMING_SOON_PHASE_2"
            data["real_voice_connected"] = False
        else:
            self._status_message = message or f"State changed to {new_state.value}"

        self._error_detail = error
        if data:
            self._state_data = data
        else:
            self._state_data = {}

        payload = self.get_summary()
        for listener in self._listeners:
            try:
                listener(self._current_state, payload)
            except Exception as e:
                logger.error(f"Error in state transition listener callback: {e}", exc_info=True)

        return True

    def get_summary(self) -> Dict[str, Any]:
        return {
            "state": self._current_state.value,
            "previous_state": self._previous_state.value if self._previous_state else None,
            "message": self._status_message,
            "error": self._error_detail,
            "data": self._state_data,
            "timestamp": self._last_transition_time.isoformat(),
            "voice_phase_status": "PHASE_3_FOUNDATION_VOICE_COMING_IN_PHASE_2"
        }

    def reset(self):
        """Resets state to IDLE."""
        self.transition_to(DesktopInteractionState.IDLE, message="Ready")
