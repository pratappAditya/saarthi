"""
Check Ollama Local Model Tag List for Approved Nemotron Models.
"""

import httpx
from app.config.settings import settings
from app.models.nemotron_catalog import NemotronModelCatalog

def main():
    base_url = settings.OLLAMA_BASE_URL.rstrip('/')
    print("=== OLLAMA LOCAL TAGS AUDIT ===")
    try:
        resp = httpx.get(f"{base_url}/api/tags", timeout=3.0)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            print("Installed Models in Ollama:")
            for m in models:
                print(f" - Name: {m.get('name')}, Size: {round(m.get('size', 0)/(1024**3), 2)} GB")
        else:
            print(f"Ollama returned HTTP status {resp.status_code}")
    except Exception as e:
        print(f"Failed to query Ollama tags: {e}")

if __name__ == "__main__":
    main()
