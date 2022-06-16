import hashlib


def blake2b(data: bytes) -> bytes:
    return hashlib.blake2b(data).digest()


def phf1(pk: bytes, data: bytes) -> bytes:
    result = b'\x01' + blake2b(pk + data)
    return result[:32]
