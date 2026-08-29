# base44.py
import math
from typing import Tuple

# ----------------------------------------------------------------------
# 1️⃣  Alphabet (44 printable, URL‑safe characters)
# ----------------------------------------------------------------------
# Digits 0‑9, uppercase A‑Z (omitting I, O, L), and a few symbols.
# The escape character is "~"; the 12 “extra” symbols follow it.
ALPHABET = (
    "0123456789"          # 0‑9  → indices 0‑9
    "ABCDEFGHJKMNPQRSTUVWX"  # A‑Z without I, L, O, Y, Z → indices 10‑31
    "-_!~*#@%"           # extra symbols (indices 32‑43)
)

# Build lookup tables
INDEX = {ch: i for i, ch in enumerate(ALPHABET)}
ESCAPE = "~"                     # chosen escape prefix
EXTRA_SYMBOLS = ALPHABET[32:]    # the 12 symbols after the first 32

# ----------------------------------------------------------------------
# 2️⃣  Helper: split a bit‑string into 5‑bit groups
# ----------------------------------------------------------------------
def _bits_from_bytes(data: bytes) -> str:
    """Return a string of bits (e.g. '11001001...') from the input bytes."""
    return "".join(f"{b:08b}" for b in data)

def _group_bits(bits: str, size: int = 5) -> Tuple[str, int]:
    """
    Split ``bits`` into ``size``‑bit chunks, padding the last chunk with zeros.
    Returns the concatenated groups and the number of padding bits added.
    """
    pad_len = (size - len(bits) % size) % size
    bits_padded = bits + "0" * pad_len
    groups = [bits_padded[i:i+size] for i in range(0, len(bits_padded), size)]
    return groups, pad_len

# ----------------------------------------------------------------------
# 3️⃣  Encode
# ----------------------------------------------------------------------
def encode(data: bytes) -> str:
    """
    Encode ``data`` (bytes) to a Base44 string.
    The first two characters store the original byte length (0‑65535) in big‑endian.
    """
    # Store length so the decoder knows how many padding bits to drop
    if len(data) > 0xFFFF:
        raise ValueError("Data too long for this simple length header")
    length_header = f"{len(data):04x}"   # 4‑hex‑digit length (2 bytes)

    bits = _bits_from_bytes(data)
    groups, pad_len = _group_bits(bits, 5)

    out = []
    for grp in groups:
        val = int(grp, 2)          # 0‑31
        if val < 32:
            out.append(ALPHABET[val])
        else:
            # Should never happen because groups are 5 bits → max 31
            # (kept for completeness if we ever change group size)
            out.append(ESCAPE + EXTRA_SYMBOLS[val - 32])

    # Encode any values that need the extra symbols (val 32‑43) using the escape
    # In the current 5‑bit grouping this case never occurs, but we keep the logic
    # for potential future variants.
    encoded = "".join(out)
    return length_header + encoded

# ----------------------------------------------------------------------
# 4️⃣  Decode
# ----------------------------------------------------------------------
def decode(s: str) -> bytes:
    """
    Decode a Base44 string produced by ``encode``.
    The first 4 hex digits represent the original byte length.
    """
    # Extract length header
    length_hex = s[:4]
    orig_len = int(length_hex, 16)
    payload = s[4:]

    bits = []
    i = 0
    while i < len(payload):
        ch = payload[i]
        if ch == ESCAPE:
            # Next char gives a value 32‑43
            i += 1
            if i >= len(payload):
                raise ValueError("Invalid escape sequence at end of string")
            extra = payload[i]
            val = 32 + EXTRA_SYMBOLS.index(extra)
        else:
            val = INDEX[ch]
        # Convert value to 5‑bit binary
        bits.append(f"{val:05b}")
        i += 1

    bit_str = "".join(bits)
    # Remove the padding bits that were added during encoding
    total_bits = orig_len * 8
    bit_str = bit_str[:total_bits]   # discard any extra padding bits

    # Convert back to bytes
    out = bytearray()
    for i in range(0, len(bit_str), 8):
        byte = int(bit_str[i:i+8], 2)
        out.append(byte)
    return bytes(out)


# ----------------------------------------------------------------------
# 5️⃣  Demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sample = b"Hello, Base44!"
    enc = encode(sample)
    dec = decode(enc)

    print("original :", sample)
    print("encoded  :", enc)
    print("decoded  :", dec)
    print("match?   :", sample == dec)
  
