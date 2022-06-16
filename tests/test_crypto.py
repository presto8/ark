from src import crypto
import helpers


def test_blake2():
    # https://datatracker.ietf.org/doc/html/rfc7693#appendix-A
    assert crypto.blake2b(b"abc") == bytes.fromhex("""
BA 80 A5 3F 98 1C 4D 0D 6A 27 97 B6 9F 12 F6 E9
4C 21 2F 14 68 5A C4 B7 4B 12 BB 6F DB FF A2 D1
7D 87 C5 39 2A AB 79 2D C2 52 D5 DE 45 33 CC 95
18 D3 8A A8 DB F1 92 5A B9 23 86 ED D4 00 99 23
""")


def test_phf1():
    pk = b"38DB2C2847539F57AB46D3D09A3EC46F571E3B9F"
    h = crypto.phf1(pk, b"")
    assert len(h) == 32
    assert h.startswith(b'\x01')
    assert h[1:] == crypto.blake2b(pk)[:31]

    assert helpers.phf1(b"") == h
