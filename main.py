from decryption import Decryption
from encryption import Encryption
from protocols import SEND
from protocols import RECEIVE

UDP_IP = "127.0.0.1"
MESSAGE = b"kayrayi seviyorum"
password = 42
channel = input("kanal seçiminizi yapın amk: ")
UDP_PORT = channel

# print(SEND(UDP_IP, UDP_PORT, MESSAGE))
# print(RECEIVE(UDP_IP, UDP_PORT, MESSAGE)) examples for sending and receiving data


