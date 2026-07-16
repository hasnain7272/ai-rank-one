import sys, json, hmac, hashlib, base64, time

# The known-good anon payload (decoded from your existing .env key).
# We keep the SAME payload and just re-sign it with the real JWT secret.
PAYLOAD = {
    "iss": "supabase",
    "ref": "qezitivobatbayifkmsk",
    "role": "anon",
    "iat": 1784186964,
    "exp": 2099762964,
}

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

secret = sys.argv[1].strip()
header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
payload = b64url(json.dumps(PAYLOAD, separators=(",", ":")).encode())
signing_input = f"{header}.{payload}".encode()
sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
token = f"{header}.{payload}.{b64url(sig)}"
print(token)
print(f"TOTAL_LEN={len(token)} SIG_LEN={len(token.split('.')[2])}", file=sys.stderr)
