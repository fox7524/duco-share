password = 42
class Decryption:
    def __init__(self, password):
        self.password = password

    def decrypt(self, encryipted_message):
        return "".join([chr(ord(c) ^ self.password) for c in encryipted_message])

