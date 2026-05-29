"""
Minimal kripto yardımcıları (Task 1).

Not: Bu modül "gerçek" bir şifreleme kütüphanesi değildir; plan kapsamında
basit XOR (anahtar tekrar ederek) ve HMAC-SHA256 imzalama/doğrulama sağlar.
"""

from __future__ import annotations

import hashlib
import hmac


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

