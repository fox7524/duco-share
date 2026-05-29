import socket
# UDP_IP = "127.0.0.1"
# UDP_PORT = 5005
# MESSAGE = b"kayrayi seviyorum"
# will be added to main.py

class SEND:
    def __init__(self, UDP_IP, UDP_PORT, MESSAGE): # sends the dedicated message to the dedicated ip and port
        # print("UDP target IP: %s" % UDP_IP)
        # print("UDP target port: %s" % UDP_PORT)
        # print("message: %s" % MESSAGE)
        
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

class RECEIVE:
    def __init__(self, UDP_IP, UDP_PORT, MESSAGE):
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))
        
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            return str(data)

if __name__ == "__main__":
    if input("s mi r mi \n") == "s":
        print(SEND(UDP_IP, UDP_PORT, MESSAGE))
    else:
        print(RECEIVE(UDP_IP, UDP_PORT, MESSAGE))
