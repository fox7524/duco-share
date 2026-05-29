import threading
import sys
import socket
from decryption import Decryption
from encryption import Encryption
from protocols import SEND
from protocols import RECEIVE

UDP_IP = "100.78.253.13"
# MESSAGE = b"kayrayi seviyorum"
password = 42
channel = input("kanal seçiminizi yapın amk: ")
UDP_PORT = int(channel)

# print(SEND(UDP_IP, UDP_PORT, MESSAGE))
# print(RECEIVE(UDP_IP, UDP_PORT, MESSAGE))

if input("s mi r mi: ") == "s":
    while 1:
        input_ = input("söyle hacı \n")
        MESSAGE = input_.encode()
        print(SEND().send(UDP_IP, UDP_PORT, MESSAGE))
else:
    while 1:
        print(RECEIVE().rec(UDP_IP, UDP_PORT))
