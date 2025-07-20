from qkd_qiskit import generate_key
from encryptor import encrypt_file
from decryptor import decrypt_file

print("🔐 Quantum Key Distribution Simulator (CLI)")
key = generate_key(num_bits=512)
print("Generated Key (first 64 bits):", key[:64])
encrypt_file("message.txt", "encrypted.bin", key)
print("✅ Encrypted to 'encrypted.bin'")
decrypt_file("encrypted.bin", "decrypted.txt", key)
print("✅ Decrypted to 'decrypted.txt'")