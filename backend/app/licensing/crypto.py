import base64
import json
from typing import Tuple, Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Embedded default client public key (used if no custom public key file is provided)
DEFAULT_VENDOR_PUBLIC_KEY_PEM = (
    "-----BEGIN PUBLIC KEY-----\n"
    "MCowBQYDK2VwAyEA9468oQG5xV3B2n40k0Nl5f9/Q4d0eK9gR8wZ9m2u1j0=\n"
    "-----END PUBLIC KEY-----\n"
)

def generate_keypair() -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return priv, pub

def private_key_to_pem(private_key: ed25519.Ed25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def private_key_from_pem(pem_bytes: bytes) -> ed25519.Ed25519PrivateKey:
    return serialization.load_pem_private_key(pem_bytes, password=None)

def public_key_to_pem(public_key: ed25519.Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def public_key_from_pem(pem_bytes: bytes) -> ed25519.Ed25519PublicKey:
    return serialization.load_pem_public_key(pem_bytes)

def canonical_json_bytes(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')

def sign_payload(payload: Dict[str, Any], private_key: ed25519.Ed25519PrivateKey) -> str:
    payload_bytes = canonical_json_bytes(payload)
    sig_bytes = private_key.sign(payload_bytes)
    
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')
    sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode('utf-8').rstrip('=')
    
    return f"{payload_b64}.{sig_b64}"

def _b64_decode_padded(s: str) -> bytes:
    padding = len(s) % 4
    if padding != 0:
        s += '=' * (4 - padding)
    return base64.urlsafe_b64decode(s)

def verify_token(token: str, public_key: ed25519.Ed25519PublicKey) -> Dict[str, Any]:
    parts = token.split('.')
    if len(parts) != 2:
        raise ValueError("Invalid token format: expected header.signature")
    
    payload_b64, sig_b64 = parts[0], parts[1]
    
    try:
        payload_bytes = _b64_decode_padded(payload_b64)
        sig_bytes = _b64_decode_padded(sig_b64)
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {str(e)}")
    
    try:
        public_key.verify(sig_bytes, payload_bytes)
    except InvalidSignature:
        raise ValueError("Cryptographic signature verification failed: signature is invalid or tampered")
    
    try:
        payload = json.loads(payload_bytes.decode('utf-8'))
    except Exception as e:
        raise ValueError(f"Failed to parse payload JSON: {str(e)}")
    
    return payload
