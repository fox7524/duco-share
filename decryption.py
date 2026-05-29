password = 42
encryipted_message = input("Şifreli mesajı girin: ")

decryipted_message = "".join([chr(ord(c) ^ password) for c in encryipted_message])

print(f"Çözülmüş hali: {decryipted_message}")