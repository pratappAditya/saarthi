import pytest
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from app.licensing.crypto import (
    generate_keypair, private_key_to_pem, private_key_from_pem,
    public_key_to_pem, public_key_from_pem, canonical_json_bytes,
    sign_payload, verify_token
)

@pytest.fixture
def keys():
    priv, pub = generate_keypair()
    return priv, pub

def test_valid_ed25519_signature(keys):
    priv, pub = keys
    payload = {"license_id": "LIC-100", "plan": "MONTHLY"}
    token = sign_payload(payload, priv)
    verified = verify_token(token, pub)
    assert verified["license_id"] == "LIC-100"

def test_modified_payload_fails(keys):
    priv, pub = keys
    token = sign_payload({"license_id": "LIC-100", "plan": "MONTHLY"}, priv)
    parts = token.split(".")
    mod_payload = base64.urlsafe_b64encode(canonical_json_bytes({"license_id": "LIC-100", "plan": "YEARLY"})).decode("utf-8").rstrip("=")
    with pytest.raises(ValueError, match="signature verification failed"):
        verify_token(f"{mod_payload}.{parts[1]}", pub)

def test_modified_signature_fails(keys):
    priv, pub = keys
    token = sign_payload({"license_id": "LIC-100"}, priv)
    parts = token.split(".")
    bad_sig = parts[1][:-2] + "AA"
    with pytest.raises(ValueError):
        verify_token(f"{parts[0]}.{bad_sig}", pub)

def test_truncated_signature_fails(keys):
    priv, pub = keys
    token = sign_payload({"license_id": "LIC-100"}, priv)
    parts = token.split(".")
    with pytest.raises(ValueError):
        verify_token(f"{parts[0]}.{parts[1][:10]}", pub)

def test_extended_signature_fails(keys):
    priv, pub = keys
    token = sign_payload({"license_id": "LIC-100"}, priv)
    parts = token.split(".")
    with pytest.raises(ValueError):
        verify_token(f"{parts[0]}.{parts[1]}FFFF", pub)

def test_wrong_public_key_fails(keys):
    priv1, pub1 = keys
    _, pub2 = generate_keypair()
    token = sign_payload({"license_id": "LIC-100"}, priv1)
    with pytest.raises(ValueError):
        verify_token(token, pub2)

def test_empty_payload_fails(keys):
    _, pub = keys
    with pytest.raises(ValueError):
        verify_token(".sig123", pub)

@pytest.mark.parametrize("bad_b64", [
    "!!!.sig",
    "part1.!!!",
    "===.===",
    "%%%%.%%%%"
])
def test_malformed_base64_fails(keys, bad_b64):
    _, pub = keys
    with pytest.raises(ValueError):
        verify_token(bad_b64, pub)

@pytest.mark.parametrize("field,orig_val,tampered_val", [
    ("customer_id", "CUST-1", "CUST-HACKER"),
    ("plan", "STUDENT", "YEARLY"),
    ("expires_at", "2026-01-01T00:00:00Z", "2099-01-01T00:00:00Z"),
    ("device_fingerprint", "fp_legit", "fp_stolen"),
    ("status", "SUSPENDED", "ACTIVE"),
    ("status", "REVOKED", "ACTIVE"),
    ("status", "CANCELLED", "ACTIVE"),
    ("issued_at", "2026-01-01T00:00:00Z", "2020-01-01T00:00:00Z"),
    ("license_id", "LIC-USER-1", "LIC-ADMIN-99"),
    ("grace_period_days", 7, 9999)
])
def test_tampered_payload_fields_fail(keys, field, orig_val, tampered_val):
    priv, pub = keys
    payload = {"license_id": "LIC-1", "customer_id": "CUST-1", "plan": "STUDENT", "status": "SUSPENDED", "expires_at": "2026-01-01T00:00:00Z", "device_fingerprint": "fp_legit", field: orig_val}
    token = sign_payload(payload, priv)
    parts = token.split(".")
    
    payload[field] = tampered_val
    tampered_b64 = base64.urlsafe_b64encode(canonical_json_bytes(payload)).decode("utf-8").rstrip("=")
    
    with pytest.raises(ValueError):
        verify_token(f"{tampered_b64}.{parts[1]}", pub)

@pytest.mark.parametrize("i", range(1, 101))
def test_crypto_fuzzing_matrix_100_cases(keys, i):
    priv, pub = keys
    payload = {
        "case_id": i,
        "license_id": f"LIC-FUZZ-{i}",
        "customer_id": f"CUST-{i*10}",
        "unicode_name": f"User_हिंदी_Saarthi_{i}",
        "nonce": f"nonce_val_{i}"
    }
    token = sign_payload(payload, priv)
    res = verify_token(token, pub)
    assert res["case_id"] == i
    assert res["unicode_name"] == f"User_हिंदी_Saarthi_{i}"
