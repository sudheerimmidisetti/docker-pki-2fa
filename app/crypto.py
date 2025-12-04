# app/crypto.py
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key(path="student_private.pem"):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    # 1. base64 decode
    ct = base64.b64decode(encrypted_seed_b64)
    # 2. RSA/OAEP decrypt with SHA-256, MGF1(SHA-256)
    pt = private_key.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    seed = pt.decode("utf-8").strip()
    # 3. validate 64-char hex
    if len(seed) != 64 or any(c not in "0123456789abcdef" for c in seed):
        raise ValueError("Decrypted seed invalid")
    return seed

def sign_commit_hash(commit_hash: str, private_key) -> bytes:
    # commit_hash must be ASCII hex string (40 chars)
    sig = private_key.sign(
        commit_hash.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return sig

def encrypt_with_pubkey(data: bytes, pubkey_path="instructor_public.pem") -> bytes:
    with open(pubkey_path, "rb") as f:
        pub = serialization.load_pem_public_key(f.read())
    ct = pub.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ct
