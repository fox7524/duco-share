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
