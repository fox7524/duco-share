import threading
import sys
import socket
from decryption import Decryption
from encryption import Encryption
from protocols import SEND
from protocols import RECEIVE

UDP_IP = "127.0.0.1"
MESSAGE = b"kayrayi seviyorum"
password = 42
channel = input("kanal seçiminizi yapın amk: ")
UDP_PORT = int(channel)

# print(SEND(UDP_IP, UDP_PORT, MESSAGE))
# print(RECEIVE(UDP_IP, UDP_PORT, MESSAGE))

if input("s mi r mi: ") == "s":
    print(SEND(UDP_IP, UDP_PORT, MESSAGE))
else:
    print(RECEIVE(UDP_IP, UDP_port, MESSAGE))
