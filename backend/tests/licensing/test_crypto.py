import pytest
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from app.licensing.crypto import (
    generate_keypair, private_key_to_pem, private_key_from_pem,
    public_key_to_pem, public_key_from_pem, canonical_json_bytes,
    sign_payload, verify_token
)

def test_generate_keypair():
    priv, pub = generate_keypair()
    assert isinstance(priv, ed25519.Ed25519PrivateKey)
    assert isinstance(pub, ed25519.Ed25519PublicKey)

def test_pem_serialization_roundtrip():
    priv, pub = generate_keypair()
    priv_pem = private_key_to_pem(priv)
    pub_pem = public_key_to_pem(pub)
    
    loaded_priv = private_key_from_pem(priv_pem)
    loaded_pub = public_key_from_pem(pub_pem)
    
    msg = b"test payload"
    sig = loaded_priv.sign(msg)
    loaded_pub.verify(sig, msg)

def test_canonical_json_ordering():
    d1 = {"b": 2, "a": 1, "c": {"z": 9, "y": 8}}
    d2 = {"a": 1, "c": {"y": 8, "z": 9}, "b": 2}
    assert canonical_json_bytes(d1) == canonical_json_bytes(d2)

def test_sign_and_verify_token_valid():
    priv, pub = generate_keypair()
    payload = {"license_id": "LIC-001", "plan": "MONTHLY", "nonce": "abc123"}
    token = sign_payload(payload, priv)
    
    assert "." in token
    verified = verify_token(token, pub)
    assert verified["license_id"] == "LIC-001"
    assert verified["plan"] == "MONTHLY"

def test_verify_token_invalid_signature():
    priv1, pub1 = generate_keypair()
    priv2, pub2 = generate_keypair()
    
    payload = {"license_id": "LIC-001", "plan": "MONTHLY"}
    token = sign_payload(payload, priv1)
    
    with pytest.raises(ValueError, match="signature verification failed"):
        verify_token(token, pub2)

def test_verify_token_tampered_payload():
    priv, pub = generate_keypair()
    payload = {"license_id": "LIC-001", "plan": "STUDENT"}
    token = sign_payload(payload, priv)
    
    parts = token.split(".")
    tampered_payload = {"license_id": "LIC-001", "plan": "YEARLY"}
    tampered_b64 = base64.urlsafe_b64encode(canonical_json_bytes(tampered_payload)).decode("utf-8").rstrip("=")
    tampered_token = f"{tampered_b64}.{parts[1]}"
    
    with pytest.raises(ValueError, match="signature verification failed"):
        verify_token(tampered_token, pub)

@pytest.mark.parametrize("invalid_token", [
    "",
    "not_a_valid_token",
    "header.signature.extra_part",
    "invalid_base64!@#.signature",
    "abc",
    "a.b.c.d",
    "part1.part2.part3",
    "badbase64!!!.sig"
])
def test_verify_token_malformed_token_formats(invalid_token):
    _, pub = generate_keypair()
    with pytest.raises(ValueError):
        verify_token(invalid_token, pub)

@pytest.mark.parametrize("field,value", [
    ("license_id", "LIC-TEST-100"),
    ("customer_id", "CUST-999"),
    ("plan", "STUDENT"),
    ("status", "ACTIVE"),
    ("device_fingerprint", "a3f89e1102948172635"),
    ("nonce", "nonce_12345"),
    ("issued_at", "2026-01-01T00:00:00Z"),
    ("expires_at", "2027-01-01T00:00:00Z"),
    ("grace_period_days", 7),
    ("max_devices", 5)
])
def test_sign_payload_fields_preservation(field, value):
    priv, pub = generate_keypair()
    payload = {field: value, "dummy_key": "dummy_val"}
    token = sign_payload(payload, priv)
    res = verify_token(token, pub)
    assert res[field] == value

def test_sign_payload_deterministic_output():
    priv, _ = generate_keypair()
    payload = {"k1": "v1", "k2": "v2"}
    token1 = sign_payload(payload, priv)
    token2 = sign_payload(payload, priv)
    assert token1 == token2

@pytest.mark.parametrize("i", range(1, 26))
def test_crypto_keypair_fuzzing(i):
    priv, pub = generate_keypair()
    payload = {"test_index": i, "nonce": f"nonce_{i}"}
    token = sign_payload(payload, priv)
    verified = verify_token(token, pub)
    assert verified["test_index"] == i
