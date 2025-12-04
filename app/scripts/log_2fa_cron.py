#!/usr/bin/env python3
# app/scripts/log_2fa_cron.py
import os, sys
from datetime import datetime, timezone
from totp_utils import generate_totp_code

DATA_PATH = "/data/seed.txt"

def main():
    try:
        if not os.path.exists(DATA_PATH):
            print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - ERROR: seed not found", file=sys.stderr)
            return
        with open(DATA_PATH) as f:
            hex_seed = f.read().strip()
        code, _ = generate_totp_code(hex_seed)
        ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{ts} - 2FA Code: {code}")
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    main()
