import threading
import sys
import socket
from decryption import Decryption
from encryption import Encryption
<<<<<<< Updated upstream
from protocols import SEND
from protocols import RECEIVE

UDP_IP = "127.0.0.1"
MESSAGE = b"kayrayi seviyorum"
password = 42
channel = input("kanal seçiminizi yapın amk: ")
UDP_PORT = channel

