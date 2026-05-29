# DUCOFEX Secure Terminal (P2P) — Tasarım Dokümanı

Tarih: 2026-05-29  
Hedef: Tailscale (MagicDNS) üstünde iki bilgisayarın, merkezi sunucu olmadan, terminal üzerinden WhatsApp gibi mesajlaşması.  
Kısıt: Dış kütüphane yok (sadece Python stdlib). Kod stili repo’daki gibi sade/direkt olacak.

## 0) Kapsam / Kapsam dışı

### Kapsam
- 2 peer arasında P2P UDP tabanlı sohbet
- “Kanal” = port seçimi (örn. kanal 5 -> port 5005)
- Mesaj gizliliği: XOR
- Mesaj bütünlüğü/kimlik doğrulama: HMAC-SHA256
- Asenkron kullanım: bir thread dinlerken ana thread input alır
- Peer adresleme: Tailscale **MagicDNS** (isim -> IP çözümleme OS DNS ile)

### Kapsam dışı
- Gerçek UDP broadcast’ın tailnet geneline yayılması (Tailscale L3 olduğu için garanti değil)
- NAT traversal / internet üstünde “her koşulda UDP ulaşır” garantisi
- İleri seviye kripto (AES/GCM vb.) ve anahtar değişimi (Diffie-Hellman)
- Grup sohbeti / oda keşfi (discovery) (ileride eklenebilir)

## 1) Ağ modeli (Tailscale + Raspberry Pi)
- Raspberry Pi ofis LAN’ını tailnet’e “subnet router” olarak route ediyor.
- Bu proje **tailnet üstünden** peer’lara ulaşır: `peer.magicdns-name` + UDP port.
- Gerçek “broadcast” yerine: **uygulama katmanı broadcast** kullanılır: `peers.json` içindeki tüm peer’lara aynı paketi gönder.

## 2) Dosya/mimari önerisi

Repo tarzını bozmadan 3 ana modül:

1. `main.py`
   - kullanıcıdan: nick, kanal, şifre, peer listesi seçimi/okuma
   - listener thread başlatır
   - input loop: yaz -> paketle -> tüm peer’lara yolla

2. `udp.py` (veya mevcut `protocols.py` sadeleştirilir)
   - UDP socket açma, bind, recvfrom
   - `send_to(host, port, data_bytes)`
   - `listen(bind_ip, port, on_packet)` (sonsuz döngü)

3. `crypto.py` (mevcut encryption/decryption yaklaşımına benzer)
   - `derive_key(passphrase) -> bytes`
   - `xor_bytes(data, key) -> bytes`
   - `sign_hmac(key, body_bytes) -> hexstr`
   - `verify_hmac(key, body_bytes, sig_hex) -> bool`

Ek dosya:
- `peers.json`: peer listesi (MagicDNS isimleri)

## 3) Port/Kanal kuralı
- `BASE_PORT = 5000`
- `port = BASE_PORT + int(kanal)`
- Her iki taraf aynı kanalı seçerse aynı portta konuşur.

Not: UDP port çakışmalarını önlemek için kanal aralığı dokümante edilecek (örn. 1-999).

## 4) Paket formatı (wire format)

UDP payload = UTF-8 encoded JSON (debug kolaylığı için).

Örnek şema:
```json
{
  "v": 1,
  "sender": "umraniye",
  "ts": 1710000000,
  "nonce": "base64...",
  "ciphertext": "base64...",
  "hmac": "hex..."
}
```

### Body/HMAC kapsamı
- HMAC hesaplanan veri: `v|sender|ts|nonce|ciphertext` alanlarının JSON’dan bağımsız deterministik birleştirilmiş hali.
- Basit yaklaşım: HMAC için ayrı bir `body_bytes = sender + b"|" + ts + b"|" + nonce + b"|" + ciphertext` kurgusu.

## 5) Kripto tasarımı (stdlib, “challenge stili ama daha sağlam”)

### Anahtar türetme
- `key = sha256(passphrase.encode("utf-8")).digest()`

### XOR şifreleme
- `ciphertext = plaintext XOR keystream`
- `keystream` = `key` tekrar edilerek uzatılır (repo stiline yakın; hızlı ve kısa)

### HMAC bütünlük ve kimlik doğrulama
- `h = hmac.new(key, body_bytes, hashlib.sha256).hexdigest()`
- Alıcı taraf:
  - önce HMAC verify
  - geçerse decrypt
  - değilse paketi drop + ekrana “wrong key / tampered packet” benzeri uyarı

## 6) Asenkron çalışma (threading)

### Thread 1 (listener)
- `sock.bind(("0.0.0.0", port))`
- sonsuz döngü: `data, addr = recvfrom(65535)`
- JSON parse -> HMAC verify -> decrypt -> ekrana bas

### Thread 2 (main/input)
- `while True: msg = input()`
- msg -> bytes -> encrypt/sign -> `for peer in peers: send_to(peer, port, payload)`

## 7) Hata yönetimi / davranışlar
- Bozuk JSON: drop
- HMAC fail: drop
- Yanlış kanal/port: mesaj ulaşmaz (kullanıcıya ipucu)
- Peer çözümlenemiyor (DNS): o peer’ı atla ve uyarı bas

## 8) Çalıştırma akışı (kullanıcı açısından)
1) `peers.json` dosyasına iki cihazın MagicDNS adları yazılır.
2) Her iki tarafta: `python main.py`
3) Aynı kanal seçilir.
4) Şifre aynı girilir.
5) Yazılan mesajlar karşı tarafın terminalinde görünür.

## 9) Güvenlik notu (dürüst uyarı)
- XOR gizlilik sağlar ama modern “secure messenger” seviyesi değildir.
- HMAC, paket manipülasyonunu ve yanlış şifreyi yakalamaya yarar.
- Bu proje “kütüphanesiz, hızlı, anlaşılır” hedefi için tasarlanmıştır.

