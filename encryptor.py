import base64

def encrypt_bytes(data: bytes, key: list[int], base64_mode=False) -> bytes:
    key_bytes = bytes(key[i % len(key)] for i in range(len(data)))
    encrypted = bytes([b ^ k for b, k in zip(data, key_bytes)])
    return base64.b64encode(encrypted) if base64_mode else encrypted
