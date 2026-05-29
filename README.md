# duco-share (DUCOFEX P2P Terminal Chat)

Tailscale (MagicDNS) üstünde, UDP ile basit bir terminal sohbeti.

## Gereksinimler

- Her iki cihaz da aynı Tailnet içinde olmalı
- Tailscale açık olmalı ve **MagicDNS** etkin olmalı (peer isimleri DNS ile çözülecek)
- Python 3

## Kurulum / Peer listesi

`peers.json` dosyasında konuşacağınız cihazların MagicDNS host adlarını listeleyin:

```json
{
  "peers": [
    { "name": "balikesir", "host": "balikesir-pc" },
    { "name": "umraniye", "host": "umraniye-pc" }
  ]
}
```

> Not: `host` alanı IP değil, Tailscale MagicDNS adı olmalı (örn. `umraniye-pc`).

## Çalıştırma

Her iki tarafta da aynı adımları uygulayın:

1) Uygulamayı başlatın:

```bash
python main.py
```

2) İstendiğinde girin:
- `nick`: ekranda görünecek isminiz
- `kanal`: sayısal bir değer. UDP port kuralı: **kanal=5000+kanal** (ör. kanal `5` → port `5005`)
- `sifre`: iki tarafta da aynı olmalı

3) Mesaj yazıp Enter’a basın; mesaj, `peers.json` içindeki tüm peer’lara gider.

Çıkmak için:

```
/quit
```
