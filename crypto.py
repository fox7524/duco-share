"""
Minimal kripto yardımcıları (Task 1).

Not: Bu modül "gerçek" bir şifreleme kütüphanesi değildir; plan kapsamında
basit XOR (anahtar tekrar ederek) ve HMAC-SHA256 imzalama/doğrulama sağlar.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time


def derive_key(passphrase: str) -> bytes:
    """Passphrase -> 32-byte anahtar (SHA-256 digest)."""
    return hashlib.sha256(passphrase.encode("utf-8")).digest()


def xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR (key tekrarı) ile byte dizisini dönüştür."""
    if not key:
        raise ValueError("key boş olamaz")
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % len(key)])
    return bytes(out)


def sign_hmac_hex(key: bytes, body: bytes) -> str:
    """HMAC-SHA256(body) -> hex string."""
    return hmac.new(key, body, hashlib.sha256).hexdigest()


def verify_hmac_hex(key: bytes, body: bytes, sig_hex: str) -> bool:
    """Verilen hex imzayı, timing-safe şekilde doğrula."""
    expected = sign_hmac_hex(key, body)
    return hmac.compare_digest(expected, sig_hex)


def _b64e(b: bytes) -> str:
    """Bytes -> base64 (ASCII str)."""
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    """Base64 (ASCII str) -> bytes."""
    return base64.b64decode(s.encode("ascii"))


def _body_bytes(v: int, sender: str, ts: int, nonce_b64: str, ciphertext_b64: str) -> bytes:
    """
    JSON alanlarının sırası değişse bile HMAC stabil kalsın diye ayrı body kurgusu.
    """
    return f"{v}|{sender}|{ts}|{nonce_b64}|{ciphertext_b64}".encode("utf-8")


def pack_message(sender: str, plaintext: bytes, passphrase: str) -> bytes:
    """
    UDP payload olarak gönderilecek paketi üret.

    Paket:
      {
        "v": 1,
        "sender": "...",
        "ts": <int>,
        "nonce": "<base64>",
        "ciphertext": "<base64>",
        "hmac": "<hex>"
      }
    """
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError("plaintext bytes olmalı")
    if not sender:
        raise ValueError("sender boş olamaz")

    v = 1
    ts = int(time.time())
    key = derive_key(passphrase)
    nonce = os.urandom(16)

    ct = xor_bytes(bytes(plaintext), key)
    nonce_b64 = _b64e(nonce)
    ct_b64 = _b64e(ct)

    body = _body_bytes(v, sender, ts, nonce_b64, ct_b64)
    sig = sign_hmac_hex(key, body)

    pkt = {
        "v": v,
        "sender": sender,
        "ts": ts,
        "nonce": nonce_b64,
        "ciphertext": ct_b64,
        "hmac": sig,
    }
    return json.dumps(pkt, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def unpack_message(payload: bytes, passphrase: str) -> tuple[str, bytes]:
    """pack_message ile oluşturulmuş payload'u doğrula + çöz: (sender, plaintext)."""
    try:
        pkt = json.loads(payload.decode("utf-8"))
    except Exception as e:
        raise ValueError("bad json") from e

    v = int(pkt.get("v", 0))
    sender = str(pkt.get("sender", ""))
    ts = int(pkt.get("ts", 0))
    nonce_b64 = str(pkt.get("nonce", ""))
    ct_b64 = str(pkt.get("ciphertext", ""))
    sig = str(pkt.get("hmac", ""))

    if v != 1 or not sender or not nonce_b64 or not ct_b64 or not sig:
        raise ValueError("bad packet")

    key = derive_key(passphrase)
    body = _body_bytes(v, sender, ts, nonce_b64, ct_b64)
    if not verify_hmac_hex(key, body, sig):
        raise ValueError("hmac fail")

    try:
        ct = _b64d(ct_b64)
    except Exception as e:
        raise ValueError("bad ciphertext b64") from e

    pt = xor_bytes(ct, key)
    return sender, pt
