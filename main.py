import threading
import sys
import socket
from decryption import Decryption
from encryption import Encryption
from protocols import SEND
from protocols import RECEIVE


ahmet = "100.78.253.13"
fox = "100.72.83.78"
UDP_IP = fox
# MESSAGE = b"kayrayi seviyorum"
password = 42
channel = input("kanal seçiminizi yapın amk: ")
UDP_PORT = int(channel)

# print(SEND(UDP_IP, UDP_PORT, MESSAGE))
# print(RECEIVE(UDP_IP, UDP_PORT, MESSAGE))

if input("s mi r mi: ") == "s":
    while 1:
        ip = input("ahmet mi kayra mı \n")
        UDP_IP = ahmet if ip == "ahmet" else fox
        input_ = input("söyle hacı \n")
        MESSAGE = input_.encode()
        print(SEND().send(UDP_IP, UDP_PORT, MESSAGE))
else:
    ip = input("ahmet mi kayra mı \n")
    UDP_IP = ahmet if ip == "ahmet" else fox
    while 1:
        print(RECEIVE().rec(UDP_IP, UDP_PORT))
