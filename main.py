import json
import threading
import time
import os
import datetime
from udp import listen, send_to, broadcast_discovery
from crypto import pack_message, unpack_message
from bluetooth_core import BluetoothManager

# Renk Kodları (UX)
C_BLUE = '\033[94m'
C_GREEN = '\033[92m'
C_CYAN = '\033[96m'
C_YELLOW = '\033[93m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

UDP_BIND = "0.0.0.0"
BASE_PORT = 5000
DISCOVERY_PORT = 5001
dynamic_peers = {} # Ağda bulduğumuz kişileri burada tutacağız

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_logo():
    logo = f"""{C_CYAN}{C_BOLD}
  _____  _    _  _____  ____  ______ _______  __
 |  __ \| |  | |/ ____|/ __ \|  ____|  ____|\ \/ /
 | |  | | |  | | |    | |  | | |__  | |__    \  / 
 | |  | | |  | | |    | |  | |  __| |  __|   /  \ 
 | |__| | |__| | |____| |__| | |    | |____ / /\ \\
 |_____/ \____/ \_____|\____/|_|    |______/_/  \_\\
{C_RESET}
    """
    print(logo)

def get_timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def listener_thread(port: int, passphrase: str):
    def on_packet(data, addr):
        try:
            sender, pt = unpack_message(data, passphrase)
            msg = pt.decode("utf-8", errors="replace")
            ts = get_timestamp()
            # \r ile mevcut satırı (prompt'u) silip, mesajı yazıp, yeni prompt ekliyoruz
            # Terminaldeki ">" işaretinin çift basılmaması için "\033[2K" (satırı temizle) kullanıyoruz
            print(f"\033[2K\r{C_YELLOW}[{ts}]{C_RESET} {C_BLUE}{C_BOLD}{sender}:{C_RESET} {msg}")
            # print(f"{C_GREEN}>{C_RESET} ", end="", flush=True) # <-- BU SATIRI DA KALDIRDIK
        except Exception:
            return

    listen(UDP_BIND, port, on_packet)

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
                        print(f"\r{C_GREEN}[+] Yeni biri katildi: {peer_nick} (IP: {ip_address}, Kanal: {peer_kanal}){C_RESET}")
                        # print(f"{C_GREEN}>{C_RESET} ", end="", flush=True)  # <-- BU SATIRI KALDIRDIK
        except Exception:
            pass

    listen("0.0.0.0", DISCOVERY_PORT, on_discovery)

def heartbeat_thread(nick: str, kanal: str):
    # Sorunu çözen kısım: Her 3 saniyede bir ağa kendimizi hatırlatıyoruz
    discovery_msg = f"DISCOVER:{nick}:{kanal}".encode("utf-8")
    while True:
        try:
            broadcast_discovery(DISCOVERY_PORT, discovery_msg)
        except Exception:
            pass
        time.sleep(3)

def main():
    clear_screen()
    print_logo()
    
    print(f"{C_YELLOW}DUCOFEX P2P Terminal Chat'e Hos Geldiniz!{C_RESET}\n")
    
    nick = input(f"{C_GREEN}nick:{C_RESET} ").strip()
    if not nick:
        nick = "anon"

    kanal = input(f"{C_GREEN}kanal:{C_RESET} ").strip()
    if not kanal.isdigit():
        print(f"{C_YELLOW}kanal sayi olmali{C_RESET}")
        return

    port = BASE_PORT + int(kanal)
    passphrase = input(f"{C_GREEN}sifre:{C_RESET} ").strip()
    if not passphrase:
        print(f"{C_YELLOW}sifre bos olamaz{C_RESET}")
        return

    # 1. Başkalarını duymak için Discovery Listener'ı başlatıyoruz
    dt = threading.Thread(target=discovery_listener_thread, daemon=True)
    dt.start()

    # 2. Kendimizi periyodik olarak ağa duyuruyoruz (Heartbeat)
    ht = threading.Thread(target=heartbeat_thread, args=(nick, kanal), daemon=True)
    ht.start()

    # BLE Entegrasyonu
    # Gelen BLE mesajlarını UDP'deki on_packet gibi işleyebilmesi için callback oluşturuyoruz
    def ble_on_packet_wrapper(data, addr):
        try:
            sender, pt = unpack_message(data, passphrase)
            msg = pt.decode("utf-8", errors="replace")
            ts = get_timestamp()
            print(f"\033[2K\r{C_YELLOW}[{ts}]{C_RESET} {C_BLUE}{C_BOLD}{sender} (BLE):{C_RESET} {msg}")
            print(f"{C_GREEN}>{C_RESET} ", end="", flush=True)
        except Exception:
            return

    ble_manager = BluetoothManager(nick, kanal, dynamic_peers, ble_on_packet_wrapper)
    ble_manager.start()

    # 3. Mesaj dinleyici thread'i başlatıyoruz
    t = threading.Thread(target=listener_thread, args=(port, passphrase), daemon=True)
    t.start()

    print(f"\n{C_CYAN}dinleniyor: {UDP_BIND}:{port}{C_RESET}")
    print(f"{C_CYAN}cikmak icin: /quit{C_RESET}\n")

    while True:
        msg = input(f"{C_GREEN}>{C_RESET} ")
        if msg.strip() == "/quit":
            return
        if not msg.strip():
            continue

        payload = pack_message(nick, msg.encode("utf-8"), passphrase)
        
        # dynamic_peers sözlüğündeki IP/MAC adreslerine gönderiyoruz
        for peer_id, peer_info in dynamic_peers.items():
            try:
                if peer_info.get("type") == "ble":
                    # Bluetooth üzerinden gönder (Asenkron köprü üzerinden)
                    ble_manager.send_message(peer_id, payload)
                else:
                    # UDP üzerinden gönder
                    target_port = BASE_PORT + int(peer_info["kanal"])
                    send_to(peer_id, target_port, payload)
            except Exception:
                continue

        time.sleep(0.01)

if __name__ == "__main__":
    main()
