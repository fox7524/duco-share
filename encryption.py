password = 42
class Encryption:
    def __init__(self, password):
        self.password = password

    def encrypt(self, message):
        return "".join([chr(ord(c) ^ self.password) for c in message])


