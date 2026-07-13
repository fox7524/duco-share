import json
import threading
import time
from udp import listen, send_to, broadcast_discovery
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

DISCOVERY_PORT = 5001
dynamic_peers = {} # Ağda bulduğumuz kişileri burada tutacağız: { "192.168.1.15": {"nick": "fox", "kanal": 5} }

def discovery_listener_thread():
    def on_discovery(data, addr):
        try:
            # Gelen veri: "DISCOVER:fox:5" formatında olacak
            msg = data.decode("utf-8")
            if msg.startswith("DISCOVER:"):
                parts = msg.split(":")
                if len(parts) == 3:
                    _, peer_nick, peer_kanal = parts
                    ip_address = addr[0]
                    
                    # Eğer bu IP bizde yoksa listeye ekle ve ekrana yaz!
                    if ip_address not in dynamic_peers:
                        dynamic_peers[ip_address] = {"nick": peer_nick, "kanal": peer_kanal}
                        print(f"\n[+] Yeni biri katildi: {peer_nick} (IP: {ip_address}, Kanal: {peer_kanal})")
                        print("> ", end="", flush=True) # prompt'u düzeltmek için
        except Exception:
            pass

    # 5001 portundan tüm gelen keşif mesajlarını dinle
    listen("0.0.0.0", DISCOVERY_PORT, on_discovery)

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

        # 1. Başkalarını duymak için Discovery Listener'ı başlatıyoruz
    dt = threading.Thread(target=discovery_listener_thread, daemon=True)
    dt.start()

    # 2. Kendimizi ağa duyuruyoruz (Örn: "DISCOVER:fox:5")
    # Bunu uygulamanın başında 1 kez yapıyoruz
    discovery_msg = f"DISCOVER:{nick}:{kanal}".encode("utf-8")
    try:
        broadcast_discovery(DISCOVERY_PORT, discovery_msg)
    except Exception as e:
        print(f"Broadcast yapilamadi: {e}")

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
                # dynamic_peers sözlüğündeki IP adreslerine gönderiyoruz
        for ip, peer_info in dynamic_peers.items():
            try:
                # peer_info["kanal"] değerini int'e çevirip BASE_PORT'a ekliyoruz
                target_port = BASE_PORT + int(peer_info["kanal"])
                send_to(ip, target_port, payload)
            except Exception:
                continue

        time.sleep(0.01)


if __name__ == "__main__":
    main()
