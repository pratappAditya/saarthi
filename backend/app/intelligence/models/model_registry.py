"""Re-export unified ModelRegistry and catalogue for app.intelligence compatibility."""
from app.models.schema import ModelDescriptor
from app.models.registry import ModelRegistry, GLOBAL_MODEL_CATALOG

MODEL_CATALOG = GLOBAL_MODEL_CATALOG

__all__ = ["ModelDescriptor", "ModelRegistry", "MODEL_CATALOG", "GLOBAL_MODEL_CATALOG"]
