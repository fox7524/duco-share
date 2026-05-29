password = 42
class Decryption:
    def __init__(self, password):
        self.password = password

    def decrypt(self, encryipted_message):
        return "".join([chr(ord(c) ^ self.password) for c in encryipted_message])

# Kullanım
decryption = Decryption(password)
encryipted_message = input("Şifreli mesajı girin: ")
decryipted_message = decryption.decrypt(encryipted_message)
print(f"Çözülmüş hali: {decryipted_message}")