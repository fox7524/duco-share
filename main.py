from decryption import Decryption
from encryption import Encryption
from udp import SEND
from udp import RECEIVE
password = 42

if __name__ == "__main__":
    message = input("Şifrelenecek mesajı girin: ")
    encryption = Encryption(password)
    encryipted_message = encryption.encrypt(message)
    print(f"Şifreli hali: {encryipted_message}")
    decryption = Decryption(password)
    decryipted_message = decryption.decrypt(encryipted_message)
    print(f"Çözülmüş hali: {decryipted_message}")
    if input("s mi r mi \n") == "s":
        print(SEND)
    else:
        print(RECEIVE)
        