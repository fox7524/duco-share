# DUCOFEX P2P Terminal Chat Implementation Plan

> **For agentic workers:** Bu plan adım adım checkbox (`- [ ]`) ile uygulanacak. İstersen her “Task” için ayrı bir subagent koşturup (Task tool) ilerleriz.

**Goal:** Tailscale (MagicDNS) üstünde iki bilgisayarın, merkezi sunucu olmadan, UDP + kanal(port) + XOR+HMAC + threading ile terminalden sohbet etmesi.

**Architecture:** `main.py` iki thread çalıştırır: biri sürekli UDP dinler, diğeri `input()` ile mesaj alıp tüm peer’lara yollar. Mesajlar `crypto.py` ile XOR şifrelenir ve `hmac/sha256` ile doğrulanır. Peer’lar MagicDNS host adlarıyla `peers.json` içinden okunur (uygulama-katmanı “broadcast” = listedeki herkese yolla).

**Tech Stack:** Python 3 (stdlib: `socket`, `threading`, `json`, `base64`, `hashlib`, `hmac`, `time`, `os`, `unittest`)

---

## 0) Dosya yapısı (oluşturulacak/değiştirilecek)

**Create:**
- `crypto.py` — anahtar türetme + XOR + HMAC sign/verify + paket encode/decode yardımcıları
- `udp.py` — UDP send/listen yardımcıları (ince bir wrapper)
- `peers.json` — örnek peer listesi (MagicDNS)
- `tests/test_crypto.py` — XOR/HMAC ve paket doğrulama testleri
- `tests/test_packet_roundtrip.py` — encode/decode roundtrip testleri

**Modify:**
- `main.py` — gerçek chat orchestrator (threading + udp + crypto + peers)
- `README.md` — çalıştırma talimatı (tailscale/magicdns/kanal/peers)
- `.gitignore` — `__pycache__/` ignore (venv zaten var)

**Leave as-is (şimdilik):**
- `udp_send.py`, `udp_rec.py`, `protocols.py`, `encryption.py`, `decryption.py` (geriye dönük referans / eski denemeler)

---

## Task 1: `crypto.py` (XOR + HMAC + paket formatı)

**Files:**
- Create: `crypto.py`
- Test: `tests/test_crypto.py`

- [ ] **Step 1: Failing test yaz (`tests/test_crypto.py`)**

```python
import unittest

from crypto import (
    derive_key,
    xor_bytes,
    sign_hmac_hex,
    verify_hmac_hex,
)


class TestCrypto(unittest.TestCase):
    def test_xor_roundtrip(self):
        key = derive_key("pass")
        pt = b"selam"
        ct = xor_bytes(pt, key)
        rt = xor_bytes(ct, key)
        self.assertEqual(rt, pt)

    def test_hmac_verify_ok(self):
        key = derive_key("pass")
        body = b"hello|world"
        sig = sign_hmac_hex(key, body)
        self.assertTrue(verify_hmac_hex(key, body, sig))

    def test_hmac_verify_fail_on_change(self):
        key = derive_key("pass")
        body = b"hello|world"
        sig = sign_hmac_hex(key, body)
        self.assertFalse(verify_hmac_hex(key, b"hello|WORLD", sig))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Testi çalıştır, fail bekle**

Run:
```bash
python -m unittest -v tests/test_crypto.py
```
Expected: `ModuleNotFoundError: No module named 'crypto'` veya import hatası.

- [ ] **Step 3: Minimal implementasyon (`crypto.py`)**

```python
import hashlib
import hmac


def derive_key(passphrase: str) -> bytes:
    return hashlib.sha256(passphrase.encode("utf-8")).digest()


def xor_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("key boş olamaz")
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % len(key)])
    return bytes(out)


def sign_hmac_hex(key: bytes, body: bytes) -> str:
    return hmac.new(key, body, hashlib.sha256).hexdigest()


def verify_hmac_hex(key: bytes, body: bytes, sig_hex: str) -> bool:
    expected = sign_hmac_hex(key, body)
    return hmac.compare_digest(expected, sig_hex)
```

- [ ] **Step 4: Testi tekrar çalıştır, pass bekle**

Run:
```bash
python -m unittest -v tests/test_crypto.py
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add crypto.py tests/test_crypto.py
git commit -m "feat: add xor+hmac crypto helpers"
```

---

## Task 2: Paket encode/decode (JSON + base64) ve roundtrip testi

**Files:**
- Modify: `crypto.py`
- Create: `tests/test_packet_roundtrip.py`

Paket şekli (UDP payload):
```json
{
  "v": 1,
  "sender": "fox",
  "ts": 1710000000,
  "nonce": "base64...",
  "ciphertext": "base64...",
  "hmac": "hex..."
}
```

- [ ] **Step 1: Failing test yaz (`tests/test_packet_roundtrip.py`)**

```python
import unittest

from crypto import pack_message, unpack_message


class TestPacketRoundtrip(unittest.TestCase):
    def test_pack_unpack_ok(self):
        passphrase = "42"
        sender = "umraniye"
        pt = b"Selam"

        payload = pack_message(sender, pt, passphrase)
        got_sender, got_pt = unpack_message(payload, passphrase)

        self.assertEqual(got_sender, sender)
        self.assertEqual(got_pt, pt)

    def test_unpack_wrong_key_fails(self):
        payload = pack_message("a", b"hi", "key1")
        with self.assertRaises(ValueError):
            unpack_message(payload, "key2")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Testi çalıştır, fail bekle**

Run:
```bash
python -m unittest -v tests/test_packet_roundtrip.py
```
Expected: `ImportError: cannot import name 'pack_message'` vb.

- [ ] **Step 3: `crypto.py` içine paket fonksiyonlarını ekle**

`crypto.py` sonuna ekle:

```python
import base64
import json
import os
import time


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def _body_bytes(v: int, sender: str, ts: int, nonce_b64: str, ciphertext_b64: str) -> bytes:
    # JSON sırası değişse bile HMAC stabil kalsın diye ayrı body kurgusu.
    return f"{v}|{sender}|{ts}|{nonce_b64}|{ciphertext_b64}".encode("utf-8")


def pack_message(sender: str, plaintext: bytes, passphrase: str) -> bytes:
    v = 1
    ts = int(time.time())
    key = derive_key(passphrase)
    nonce = os.urandom(16)

    ct = xor_bytes(plaintext, key)
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

    ct = _b64d(ct_b64)
    pt = xor_bytes(ct, key)
    return sender, pt
```

- [ ] **Step 4: Testleri çalıştır, pass bekle**

Run:
```bash
python -m unittest -v tests/test_packet_roundtrip.py
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add crypto.py tests/test_packet_roundtrip.py
git commit -m "feat: add packet pack/unpack with hmac verify"
```

---

## Task 3: `udp.py` (send + listen helper)

**Files:**
- Create: `udp.py`

- [ ] **Step 1: `udp.py` oluştur**

```python
import socket


def send_to(host: str, port: int, payload: bytes) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(payload, (host, port))
    finally:
        sock.close()


def listen(bind_ip: str, port: int, on_packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, port))
    while True:
        data, addr = sock.recvfrom(65535)
        on_packet(data, addr)
```

- [ ] **Step 2: Hızlı smoke**

Run (syntax check):
```bash
python -m py_compile udp.py
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add udp.py
git commit -m "feat: add udp send/listen helpers"
```

---

## Task 4: `peers.json` örneği

**Files:**
- Create: `peers.json`

- [ ] **Step 1: `peers.json` ekle**

```json
{
  "peers": [
    { "name": "balikesir", "host": "balikesir-pc" },
    { "name": "umraniye", "host": "umraniye-pc" }
  ]
}
```

Not: `host` alanı MagicDNS adı veya `100.x.y.z` IP olabilir.

- [ ] **Step 2: Commit**

```bash
git add peers.json
git commit -m "chore: add peers.json example"
```

---

## Task 5: `main.py` (threading + chat)

**Files:**
- Modify: `main.py`

Hedef davranış:
- Program açılınca: nick + kanal + şifre ister
- `0.0.0.0:port` üzerinden arka planda dinler
- Yazdığın her mesajı `peers.json` içindeki tüm peer’lara gönderir
- Gelen mesajları `sender: mesaj` olarak basar

- [ ] **Step 1: `main.py` mevcut içeriğini değiştir**

Yeni `main.py`:

```python
import json
import threading
import time

from crypto import pack_message, unpack_message
from udp import send_to, listen


UDP_BIND = "0.0.0.0"
BASE_PORT = 5000


def load_peers(path: str = "peers.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    peers = data.get("peers", [])
    out = []
    for p in peers:
        name = str(p.get("name", "")).strip()
        host = str(p.get("host", "")).strip()
        if name and host:
            out.append({"name": name, "host": host})
    return out


def listener_thread(port: int, passphrase: str):
    def on_packet(data, addr):
        try:
            sender, pt = unpack_message(data, passphrase)
            try:
                msg = pt.decode("utf-8", errors="replace")
            except Exception:
                msg = str(pt)
            print(f"\n{sender}: {msg}")
        except Exception:
            # sessiz drop (istersen debug print açarız)
            return

    listen(UDP_BIND, port, on_packet)


def main():
    nick = input("nick: ").strip()
    if not nick:
        nick = "anon"

    kanal = input("kanal: ").strip()
    if not kanal.isdigit():
        print("kanal sayi olmali")
        return

    port = BASE_PORT + int(kanal)
    passphrase = input("sifre: ").strip()
    if not passphrase:
        print("sifre bos olamaz")
        return

    peers = load_peers("peers.json")
    # kendine yollamayı istemiyorsan: host/name match ile filtreleriz (şimdilik yolluyoruz)

    t = threading.Thread(target=listener_thread, args=(port, passphrase), daemon=True)
    t.start()

    print(f"dinleniyor: {UDP_BIND}:{port}")
    print("cikmak icin: /quit")

    while True:
        msg = input("> ")
        if msg.strip() == "/quit":
            return
        if not msg.strip():
            continue

        payload = pack_message(nick, msg.encode("utf-8"), passphrase)
        for p in peers:
            try:
                send_to(p["host"], port, payload)
            except Exception:
                # peer ulaşılamıyorsa sessiz geç (istersen debug)
                continue

        # küçük gecikme: print karışmasın diye (opsiyonel)
        time.sleep(0.01)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax check**

Run:
```bash
python -m py_compile main.py
```
Expected: no output.

- [ ] **Step 3: Manual run talimatı (iki terminal)**

Terminal A:
```bash
python main.py
```
nick: `a`, kanal: `5`, sifre: `pw`

Terminal B:
```bash
python main.py
```
nick: `b`, kanal: `5`, sifre: `pw`

Beklenen: A yazınca B’de `a: ...`, B yazınca A’da `b: ...` görünür.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: p2p terminal chat main loop (threads + udp + crypto)"
```

---

## Task 6: README + .gitignore (minimum dokümantasyon)

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`

- [ ] **Step 1: `.gitignore` güncelle**

Şunları ekle:
```
__pycache__/
*.pyc
```

- [ ] **Step 2: README doldur**

`README.md` öneri:

```md
# duco-share (DUCOFEX Secure Terminal)

Tailscale (MagicDNS) üstünde, iki bilgisayarın UDP ile (kanal=port) terminalden sohbet etmesi.

## Gereksinimler
- Python 3
- Tailscale açık ve iki cihaz aynı tailnet’te
- (Öneri) MagicDNS açık

## peers.json
`peers.json` içine konuşacağın cihazların MagicDNS host adlarını yaz.

## Çalıştırma
```bash
python main.py
```

1) nick gir  
2) kanal gir (örn 5 -> port 5005)  
3) sifre gir (iki tarafta aynı olmalı)  

Çıkmak için: `/quit`
```

- [ ] **Step 3: Commit**

```bash
git add README.md .gitignore
git commit -m "docs: add run instructions and ignore pycache"
```

---

## Plan Self-Review (benim kontrolüm)

- Spec kapsamı:
  - MagicDNS + peer listesi ✅ (Task 4/5)
  - UDP + kanal(port) ✅ (Task 3/5)
  - XOR + HMAC ✅ (Task 1/2)
  - Threading ✅ (Task 5)
  - Dış kütüphane yok ✅ (stdlib)
- Placeholder taraması: “TODO/TBD” yok ✅
- İsim/tip tutarlılığı:
  - `pack_message/unpack_message` Task 2’de tanımlanıyor, Task 5’te kullanılıyor ✅

---

## Execution Handoff

Plan hazır: `docs/superpowers/plans/2026-05-29-ducofex-p2p-terminal-chat.md`

İki seçenek:
1) **Subagent-Driven (önerilen)**: Her Task için ayrı bir subagent koştururum, senin “uzun sürüyorsa arkaplanda” isteğine uyuyor.
2) **Inline Execution**: Bu oturumda adım adım uygularım.

Hangisini istiyorsun?

