import socket


def send_to(host: str, port: int, payload: bytes) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(payload, (host, port))
    finally:
        sock.close()

def broadcast_discovery(port: int, payload: bytes) -> None:
    # 1. UDP için standart bir IPv4 soketi oluşturuyoruz
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 2. ÖNEMLİ: Bu soketin ağa "yayın" (broadcast) yapabilmesi için işletim sisteminden özel izin alıyoruz.
    # 1 değeri "True/Aktif" anlamına gelir.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        # 3. '255.255.255.255' adresi, aynı yerel ağdaki HERKESE anlamına gelir. 
        # Paketi ağdaki herkese, belirlediğimiz port üzerinden yolluyoruz.
        sock.sendto(payload, ('255.255.255.255', port))
    finally:
        # 4. İşlem bitince soketi güvenli bir şekilde kapatıyoruz
        sock.close()
    

def listen(bind_ip: str, port: int, on_packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, port))
    while True:
        data, addr = sock.recvfrom(65535)
        on_packet(data, addr)
