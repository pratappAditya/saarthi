"""
Ollama Installation & Nemotron Lifecycle Manager.
Handles Ollama runtime detection, user-consented setup, model pulling,
verification, health testing, safe model switching, and automatic rollback.
"""

import httpx
import logging
import json
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from app.config.settings import settings
from app.config.nemotron_config import NemotronConfig
from app.models.nemotron_catalog import NemotronModelCatalog
from app.models.nemotron_service import NemotronService, NemotronModelNotApprovedException

logger = logging.getLogger("app.models.installer")

class NemotronLifecycleManager:
    @staticmethod
    async def check_ollama_status() -> Dict[str, Any]:
        """
        Checks if local Ollama daemon is running and reachable on 127.0.0.1:11434.
        """
        base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        try:
            timeout = httpx.Timeout(3.0, connect=2.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(f"{base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return {
                        "installed": True,
                        "connected": True,
                        "base_url": base_url,
                        "models": models,
                        "status_code": "OLLAMA_READY",
                        "message": "Ollama service is connected and operational."
                    }
                else:
                    return {
                        "installed": True,
                        "connected": False,
                        "base_url": base_url,
                        "models": [],
                        "status_code": "OLLAMA_OFFLINE",
                        "message": f"Ollama returned HTTP status {resp.status_code}."
                    }
        except httpx.ConnectError:
            return {
                "installed": False,
                "connected": False,
                "base_url": base_url,
                "models": [],
                "status_code": "OLLAMA_NOT_INSTALLED",
                "message": "Cannot connect to Ollama daemon on 127.0.0.1:11434."
            }
        except Exception as e:
            return {
                "installed": False,
                "connected": False,
                "base_url": base_url,
                "models": [],
                "status_code": "OLLAMA_OFFLINE",
                "message": str(e)
            }

    @classmethod
    async def pull_model_stream(cls, model_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams model download/pull progress from Ollama API.
        Enforces that ONLY approved Nemotron models can be pulled.
        """
        if not NemotronService.is_approved_nemotron_model(model_id):
            raise NemotronModelNotApprovedException(requested_model=model_id)

        base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        url = f"{base_url}/api/pull"
        payload = {"name": model_id, "stream": True}

        timeout = httpx.Timeout(600.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", url, json=payload) as resp:
                if resp.status_code != 200:
                    yield {
                        "status": "error",
                        "message": f"Failed to initiate model pull (Status {resp.status_code})"
                    }
                    return

                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            yield data
                        except Exception:
                            yield {"status": line.strip()}

    @classmethod
    async def verify_and_health_check(cls, model_id: str) -> Dict[str, Any]:
        """
        Runs a minimal inference health test against the specified model.
        Returns result dict with status boolean and details.
        """
        if not NemotronService.is_approved_nemotron_model(model_id):
            return {
                "success": False,
                "code": "NEMOTRON_MODEL_NOT_APPROVED",
                "message": f"Model '{model_id}' is not an approved Nemotron model."
            }

        if settings.MODEL_PROVIDER.lower() == "mock":
            return {
                "success": True,
                "code": "NEMOTRON_READY",
                "message": f"Mock verification successful for '{model_id}'."
            }

        base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        url = f"{base_url}/api/chat"
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": "You are Saarthi local AI test."},
                {"role": "user", "content": "Hello Saarthi Nemotron test"}
            ],
            "stream": False,
            "options": {"num_predict": 10}
        }

        try:
            timeout = httpx.Timeout(30.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    res_data = resp.json()
                    content = res_data.get("message", {}).get("content", "")
                    if content or "thinking" in res_data.get("message", {}):
                        return {
                            "success": True,
                            "code": "NEMOTRON_READY",
                            "message": f"Health check verified for model '{model_id}'."
                        }
                    else:
                        return {
                            "success": False,
                            "code": "NEMOTRON_MODEL_CORRUPTED",
                            "message": f"Model '{model_id}' returned empty output during health check."
                        }
                else:
                    return {
                        "success": False,
                        "code": "NEMOTRON_INFERENCE_FAILURE",
                        "message": f"Ollama returned status {resp.status_code} for health test of '{model_id}'."
                    }
        except Exception as e:
            return {
                "success": False,
                "code": "NEMOTRON_INFERENCE_FAILURE",
                "message": f"Health check inference failed for '{model_id}': {str(e)}"
            }

    @classmethod
    async def switch_model_safely(cls, new_model_id: str) -> Dict[str, Any]:
        """
        Safely upgrades/switches active Nemotron model with automatic rollback.
        Sequence:
        1. Record current_model
        2. Validate new_model approval
        3. Verify health of new_model
        4. Switch settings.MODEL_NAME if successful
        5. If health check fails -> ROLLBACK to current_model!
        """
        current_model = settings.MODEL_NAME

        if not NemotronService.is_approved_nemotron_model(new_model_id):
            raise NemotronModelNotApprovedException(requested_model=new_model_id)

        logger.info(f"Attempting model switch from '{current_model}' to '{new_model_id}'...")

        # Step 1: Health test new model
        health_result = await cls.verify_and_health_check(new_model_id)

        if health_result["success"]:
            # Switch active model
            settings.MODEL_NAME = new_model_id
            NemotronConfig.EXACT_NEMOTRON_MODEL = new_model_id
            logger.info(f"Successfully switched active model to '{new_model_id}'.")
            return {
                "success": True,
                "previous_model": current_model,
                "current_model": new_model_id,
                "message": f"Successfully activated Nemotron model '{new_model_id}'."
            }
        else:
            # ROLLBACK!
            logger.warning(f"Health check failed for '{new_model_id}'. Rolling back to '{current_model}'! Reason: {health_result['message']}")
            settings.MODEL_NAME = current_model
            NemotronConfig.EXACT_NEMOTRON_MODEL = current_model
            return {
                "success": False,
                "rolled_back": True,
                "previous_model": current_model,
                "attempted_model": new_model_id,
                "current_model": current_model,
                "message": f"New model health check failed ({health_result['message']}). Automatically rolled back to '{current_model}'."
            }

    @classmethod
    async def remove_model(cls, model_id: str) -> Dict[str, Any]:
        """
        Deletes an inactive Nemotron model from local Ollama storage.
        Rejects deletion if model_id is the currently active model.
        """
        if model_id.lower() == settings.MODEL_NAME.lower():
            return {
                "success": False,
                "message": f"Cannot delete active model '{model_id}'. Switch to another approved model first."
            }

        base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        url = f"{base_url}/api/delete"

        try:
            timeout = httpx.Timeout(10.0, connect=3.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.request("DELETE", url, json={"name": model_id})
                if resp.status_code in (200, 204):
                    return {
                        "success": True,
                        "message": f"Model '{model_id}' deleted from local storage."
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to delete model '{model_id}' (HTTP {resp.status_code})."
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting model '{model_id}': {str(e)}"
            }
