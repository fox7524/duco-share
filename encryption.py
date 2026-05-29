password = 42
message = input("Şifrelenecek mesajı girin: ")

# Şifreleme (Tek Satır)
encryipted_message = "".join([chr(ord(c) ^ password) for c in message])

print(f"Şifreli hali: {encryipted_message}")

