# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from crypto import load_private_key, decrypt_seed
from totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()
DATA_PATH = "/data/seed.txt"

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: DecryptRequest):
    try:
        priv = load_private_key("student_private.pem")
        seed = decrypt_seed(req.encrypted_seed, priv)
        os.makedirs("/data", exist_ok=True)
        with open(DATA_PATH, "w") as f:
            f.write(seed)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Decryption failed"})

@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    with open(DATA_PATH) as f:
        hex_seed = f.read().strip()
    try:
        code, valid_for = generate_totp_code(hex_seed)
        return {"code": code, "valid_for": valid_for}
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Failed to generate code"})

@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail={"error": "Missing code"})
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    with open(DATA_PATH) as f:
        hex_seed = f.read().strip()
    valid = verify_totp_code(hex_seed, req.code, valid_window=1)
    return {"valid": bool(valid)}
