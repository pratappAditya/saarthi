import time
import threading
import logging
from typing import Callable, Any, Dict

logger = logging.getLogger("app.intelligence.circuit_breaker")

class CircuitBreakerOpenException(Exception):
    """Raised when an execution call is attempted while the circuit breaker is OPEN."""
    pass

class CircuitBreaker:
    """
    Circuit Breaker pattern for protecting AI Model Provider and External API calls.
    States: CLOSED (Normal), OPEN (Failing/Blocking Calls), HALF_OPEN (Testing Recovery).
    """
    def __init__(self, name: str, failure_threshold: int = 4, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"  # CLOSED | OPEN | HALF_OPEN
        self.failure_count = 0
        self.last_state_change = time.time()
        self._lock = threading.Lock()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.execute(func, *args, **kwargs)
        return wrapper

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            now = time.time()

            # Check if OPEN circuit should transition to HALF_OPEN
            if self.state == "OPEN":
                if now - self.last_state_change >= self.recovery_timeout:
                    logger.info(f"CircuitBreaker[{self.name}] transitioning from OPEN to HALF_OPEN")
                    self.state = "HALF_OPEN"
                    self.last_state_change = now
                else:
                    raise CircuitBreakerOpenException(
                        f"AI Service '{self.name}' is currently unavailable (Circuit Breaker OPEN). Try again shortly."
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure(exc)
            raise exc

    def _on_success(self):
        with self._lock:
            if self.state in ("OPEN", "HALF_OPEN"):
                logger.info(f"CircuitBreaker[{self.name}] recovered! Transitioning to CLOSED.")
            self.state = "CLOSED"
            self.failure_count = 0
            self.last_state_change = time.time()

    def _on_failure(self, exc: Exception):
        with self._lock:
            self.failure_count += 1
            logger.warning(f"CircuitBreaker[{self.name}] recorded failure #{self.failure_count}: {exc}")
            if self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    logger.error(f"CircuitBreaker[{self.name}] failure threshold reached. Opening circuit breaker for {self.recovery_timeout}s.")
                self.state = "OPEN"
                self.last_state_change = time.time()

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "name": self.name,
                "state": self.state,
                "failure_count": self.failure_count,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "last_state_change": self.last_state_change
            }

# Circuit breakers for primary AI services
ai_circuit_breaker = CircuitBreaker("Ollama_AI_Engine", failure_threshold=4, recovery_timeout=30.0)
