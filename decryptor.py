import base64

def decrypt_bytes(data: bytes, key: list[int], base64_mode=False) -> bytes:
    data = base64.b64decode(data) if base64_mode else data
    key_bytes = bytes(key[i % len(data)] for i in range(len(data)))
    decrypted = bytes([b ^ k for b, k in zip(data, key_bytes)])
    return decrypted
