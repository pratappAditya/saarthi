import os
import zipfile
import xml.etree.ElementTree as ET
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MSIX_PATH = PROJECT_ROOT / "release" / "windows" / "Saarthi-v1.0.0-Store.msix"

def test_msix_package_exists():
    assert MSIX_PATH.exists(), f"MSIX package not found at {MSIX_PATH}"
    assert MSIX_PATH.stat().st_size > 50 * 1024 * 1024, "MSIX package is unexpectedly small"

def test_msix_manifest_structure():
    with zipfile.ZipFile(MSIX_PATH, "r") as z:
        assert "AppxManifest.xml" in z.namelist()
        manifest_data = z.read("AppxManifest.xml")
        root = ET.fromstring(manifest_data)
        
        # Check Identity
        ns = "{http://schemas.microsoft.com/appx/manifest/foundation/windows10}"
        identity = root.find(f"{ns}Identity")
        assert identity is not None
        assert identity.attrib.get("Name") == "TrovaneTechnologies.SaarthiAICompanion"
        assert identity.attrib.get("ProcessorArchitecture") == "x64"
        
        # Check Capabilities (runFullTrust)
        rescap_ns = "{http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities}"
        caps = root.find(f"{ns}Capabilities")
        assert caps is not None
        full_trust = caps.find(f"{rescap_ns}Capability[@Name='runFullTrust']")
        assert full_trust is not None, "Missing runFullTrust restricted capability required for desktop Win32 app"

def test_msix_block_map_and_content_types():
    with zipfile.ZipFile(MSIX_PATH, "r") as z:
        names = z.namelist()
        assert "[Content_Types].xml" in names
        assert "AppxBlockMap.xml" in names
        
        # Parse block map
        blockmap_data = z.read("AppxBlockMap.xml")
        bm_root = ET.fromstring(blockmap_data)
        assert bm_root.tag == "{http://schemas.microsoft.com/appx/2010/blockmap}BlockMap"
        files = bm_root.findall("{http://schemas.microsoft.com/appx/2010/blockmap}File")
        assert len(files) > 500, "BlockMap does not index all packaged files"

def test_msix_store_assets():
    with zipfile.ZipFile(MSIX_PATH, "r") as z:
        names = z.namelist()
        required_assets = [
            "Assets/Square44x44Logo.png",
            "Assets/Square150x150Logo.png",
            "Assets/StoreLogo.png",
            "Assets/Wide310x150Logo.png",
            "Assets/SplashScreen.png"
        ]
        for asset in required_assets:
            assert asset in names, f"Missing required store asset: {asset}"

def test_msix_excludes_llm_model_weights():
    with zipfile.ZipFile(MSIX_PATH, "r") as z:
        for name in z.namelist():
            lower = name.lower()
            assert not lower.endswith((".gguf", ".safetensors", ".onnx")), f"Found model weights embedded in base MSIX: {name}"
            if lower.endswith((".bin", ".pt")):
                assert z.getinfo(name).file_size < 50 * 1024 * 1024, f"Found large binary weight in base MSIX: {name}"
