import json
import threading
import time

from crypto import pack_message, unpack_message
from udp import listen, send_to


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
            msg = pt.decode("utf-8", errors="replace")
            print(f"\n{sender}: {msg}")
        except Exception:
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

    try:
        peers = load_peers("peers.json")
    except Exception:
        print("peers.json okunamadi")
        return

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
                continue

        time.sleep(0.01)


if __name__ == "__main__":
    main()
