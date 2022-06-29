import base64
import hashlib


def blake2b(data: bytes) -> bytes:
    return hashlib.blake2b(data).digest()


def phf1(pk: bytes, data: bytes) -> bytes:
    result = b'\x01' + blake2b(pk + data)
    return result[:32]


def b64e(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data, altchars=b"+-").decode()


def b64d(data):
    return base64.b64decode(data, altchars=b"+-")
