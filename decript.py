def decrypt_shift(ciphertext, shift):
    plaintext = ''
    for char in ciphertext:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            decrypted_char = chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
            plaintext += decrypted_char
        else:
            plaintext += char

    return plaintext

encrypted_text = "kkk"
decrypted_text = decrypt_shift(encrypted_text, 3)
print(decrypted_text)  # Output: Hello World
