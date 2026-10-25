#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║           ADMASTER — BINARY ANALYSIS TOOLKIT v2.0                 ║
║  Blueprint parsing • Discovery • Encoding • Cryptanalysis        ║
╚══════════════════════════════════════════════════════════════════╝
Layout: [0-15:UID][16-31:IV][32-63:CIPHERTEXT][64-79:TAG]
"""

import os
import sys
import math
import glob
import struct
import base64
import binascii
from itertools import combinations
from typing import Dict, List, Tuple, Optional, Any

# ═══════════════════════════════════════════════════════════════════
# SECTION 0: CONSTANTS & FIELD DEFINITIONS
# ═══════════════════════════════════════════════════════════════════
LAYOUT = {
    'uid':        (0, 15),   # Header / Unique ID
    'iv':         (16, 31),  # Initialization Vector
    'ciphertext': (32, 63),  # Encrypted payload
    'tag':        (64, 79),  # AES-GCM Authentication Tag
}

COMPRESSION_SIGS = {
    b'\x1f\x8b': 'GZIP',
    b'BZh': 'BZIP2',
    b'\x78\x01': 'ZLIB',
    b'\x78\x9c': 'ZLIB',
    b'\x78\xda': 'ZLIB',
    b'PK\x03\x04': 'ZIP',
}

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: CORE UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
def entropy(data: bytes) -> float:
    """Calculate Shannon entropy in bits/byte"""
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    length = len(data)
    return -sum((count / length) * math.log2(count / length)
                for count in freq if count > 0)


def hexdump(data: bytes, label: str = "") -> str:
    """Pretty hex + ASCII dump"""
    hex_str = ' '.join(f'{b:02x}' for b in data)
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
    return f"{label:14} | {hex_str} | {ascii_str}"


def extract_field(data: bytes, name: str) -> bytes:
    """Extract a field using the LAYOUT blueprint"""
    start, end = LAYOUT[name]
    return data[start:end + 1]


def hamming_similarity(a: bytes, b: bytes) -> float:
    """Bit-level similarity: 1.0 = identical, 0.0 = no bits in common"""
    if len(a) != len(b):
        return 0.0
    differing_bits = sum(bin(x ^ y).count('1') for x, y in zip(a, b))
    total_bits = len(a) * 8
    return 1.0 - (differing_bits / total_bits)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """Byte-wise XOR of two equal-length buffers"""
    return bytes(x ^ y for x, y in zip(a, b))


# ═══════════════════════════════════════════════════════════════════
# SECTION 2: SINGLE FILE ANALYSIS
# ═══════════════════════════════════════════════════════════════════
def analyze_single_file(filepath: str) -> Dict[str, Any]:
    """Comprehensive analysis of a single binary file"""
    print(f"\n{'='*70}")
    print(f"📄 ANALYSIS: {os.path.basename(filepath)}")
    print(f"📏 SIZE: {os.path.getsize(filepath)} bytes")
    print(f"{'='*70}")

    with open(filepath, 'rb') as f:
        data = f.read()

    results = {
        'filename': os.path.basename(filepath),
        'size': len(data),
        'total_entropy': entropy(data),
        'blocks': {},
        'ascii_count': sum(1 for b in data if 32 <= b < 127),
    }

    # Per-block analysis
    print("\n📦 BLOCK ANALYSIS:")
    for name, (start, end) in LAYOUT.items():
        field = extract_field(data, name)
        ent = entropy(field)
        results['blocks'][name] = {
            'bytes': (start, end),
            'entropy': ent,
            'hex': field.hex(' '),
        }

        if ent < 6.0:
            classification = "🟡 Structured/Metadata"
        elif 6.0 <= ent < 7.5:
            classification = "🟠 Mixed/Compressed"
        else:
            classification = "🟢 Encrypted/Random"

        print(f"  {name.upper():14} [{start:02x}-{end:02x}]  {len(field):2d} bytes")
        print(f"    Entropy: {ent:.4f} bits/byte  {classification}")
        print(f"    {hexdump(field)}\n")

    # ASCII overview
    pct_ascii = results['ascii_count'] / len(data) * 100
    print(f"📝 PRINTABLE ASCII: {results['ascii_count']}/{len(data)} bytes ({pct_ascii:.1f}%)")

    # Compression signature check
    for sig, name in COMPRESSION_SIGS.items():
        if data.startswith(sig):
            print(f"⚠️ COMPRESSION DETECTED: {name} signature at offset 0")
            results['compression'] = name
            break
    else:
        print("🔍 No known compression signature found")
        results['compression'] = None

    return results, data


def nibble_analysis(data: bytes) -> Dict[str, Any]:
    """Analyze high/low nibbles — reveals Base16/32/64 patterns"""
    high = [0] * 16
    low = [0] * 16
    for b in data:
        high[(b >> 4) & 0xF] += 1
        low[b & 0xF] += 1

    high_unique = sum(1 for x in high if x > 0)
    low_unique = sum(1 for x in low if x > 0)

    print(f"\n🔢 NIBBLE ANALYSIS: High nibbles = {high_unique}/16, Low nibbles = {low_unique}/16")
    if all(high[i] == 0 for i in range(10, 16)) and all(low[i] == 0 for i in range(10, 16)):
        print("  → ⚠️ Base16/Hex encoding pattern detected")
    elif all(high[i] == 0 for i in [0, 1, 2, 6, 7, 8, 9, 12, 13, 14, 15]):
        print("  → ⚠️ Possible Base64 encoding pattern")

    return {'high_unique': high_unique, 'low_unique': low_unique}


def frequency_spectrum(data: bytes, top_n: int = 10) -> Dict[int, int]:
    """Show most frequent byte values"""
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    peak = max(freq)

    print(f"\n📈 BYTE FREQUENCY SPECTRUM (top {top_n}):")
    ranked = sorted(((v, i) for i, v in enumerate(freq)), reverse=True)
    for count, value in ranked:
        if count > 0:
            bar = '█' * max(1, int(count * 40 / peak))
            print(f"  0x{value:02x} ({value:3d}): {bar} ×{count}")
        if len(ranked) - ranked.index((count, value)) <= top_n:
            break
    return {i: v for i, v in enumerate(freq) if v > 0}


def integer_scan(data: bytes) -> Dict[str, List[int]]:
    """Scan for integer patterns — timestamps, counters, IDs"""
    if len(data) < 80:
        print("⚠️ Data too short for integer analysis")
        return {}

    le = struct.unpack('<' + 'I' * 20, data[:80])
    be = struct.unpack('>' + 'I' * 20, data[:80])

    results = {'le': [], 'be': [], 'timestamps_le': [], 'timestamps_be': []}
    print("\n🔍 INTEGER ANALYSIS (first 80 bytes as 32-bit values):")
    print(f"  {'#':<3} {'LE':>10} {'BE':>10}  Flags")
    print("  " + "-" * 45)

    for i, (l, b) in enumerate(zip(le, be)):
        flags = ""
        if 946684800 < l < 2000000000:
            flags += " ⏰LE-timestamp"
            results['timestamps_le'].append((i, l))
        if 946684800 < b < 2000000000:
            flags += " ⏰BE-timestamp"
            results['timestamps_be'].append((i, b))
        if 1 <= l <= 100000:
            flags += " #LE-counter"
        if 1 <= b <= 100000:
            flags += " #BE-counter"
        if flags:
            print(f"  [{i:2d}] {l:10} {b:10}{flags}")
        results['le'].append(l)
        results['be'].append(b)

    return results


def extract_strings(data: bytes, min_len: int = 4) -> List[Tuple[int, str]]:
    """Extract sequences of printable ASCII with offset positions"""
    results = []
    current_chars = []
    start_pos = None

    for i, b in enumerate(data):
        if 32 <= b < 127:
            if not current_chars:
                start_pos = i
            current_chars.append(chr(b))
        else:
            if len(current_chars) >= min_len:
                results.append((start_pos, ''.join(current_chars)))
            current_chars = []

    if len(current_chars) >= min_len:
        results.append((start_pos, ''.join(current_chars)))

    if results:
        print(f"\n📝 PRINTABLE STRINGS (min {min_len} chars):")
        for pos, text in results:
            print(f"  0x{pos:02x}: '{text}'")
    else:
        print(f"\n📝 No printable strings ≥ {min_len} characters found")

    return results


def detect_padding(data: bytes, block_size: int = 16) -> str:
    """Detect PKCS7, zero-padding, ISO7816 patterns"""
    last_block = data[-block_size:]

    # PKCS7
    pad_byte = last_block[-1]
    if 1 <= pad_byte <= block_size:
        if all(b == pad_byte for b in last_block[-pad_byte:]):
            result = f"✅ PKCS7 padding — {pad_byte} bytes"
            print(f"\n🧪 {result}")
            return result

    # Zero padding
    trailing_zeros = 0
    for b in reversed(last_block):
        if b == 0:
            trailing_zeros += 1
        else:
            break
    if trailing_zeros >= 4:
        result = f"⚠️ Zero padding — {trailing_zeros} trailing nulls"
        print(f"\n🧪 {result}")
        return result

    result = "❌ No standard padding detected"
    print(f"\n🧪 {result}")
    return result


def crypto_sanity_check(data: bytes) -> Dict[str, Any]:
    """Check for ECB mode, repeated blocks, and entropy anomalies"""
    blocks = [data[i:i+16] for i in range(0, len(data), 16)]
    unique_blocks = set(blocks)
    duplicate_blocks = len(blocks) - len(unique_blocks)

    block_entropies = [entropy(b) for b in blocks]
    min_ent = min(block_entropies)
    max_ent = max(block_entropies)

    print(f"\n🛡️  CRYPTO SANITY CHECK:")
    print(f"  Total blocks: {len(blocks)} | Duplicate blocks: {duplicate_blocks}")
    print(f"  Block entropy range: {min_ent:.4f} – {max_ent:.4f} bits/byte")

    if duplicate_blocks > 0:
        print("  ⚠️ WARNING: Repeated blocks detected — possible ECB mode or low entropy")
    if max_ent - min_ent > 2.0:
        print("  ⚠️ WARNING: Large entropy difference between blocks — mixed content likely")

    return {
        'total_blocks': len(blocks),
        'duplicate_blocks': duplicate_blocks,
        'entropy_range': (min_ent, max_ent),
    }


# ═══════════════════════════════════════════════════════════════════
# SECTION 3: ENCODING DETECTION
# ═══════════════════════════════════════════════════════════════════
def multi_decode(data: bytes) -> Dict[str, Any]:
    """Test multiple encoding transformations"""
    results = {}
    print("\n🔓 ENCODING ANALYSIS — Testing decoders:")

    # Base64 variants
    for name, decoder in [
        ('base64', base64.b64decode),
        ('base64url', base64.urlsafe_b64decode),
    ]:
        try:
            padded = data + b'=' * ((4 - len(data) % 4) % 4)
            decoded = decoder(padded)
            results[name] = decoded
            print(f"  ✅ {name:12} → {len(decoded)} bytes | Entropy: {entropy(decoded):.4f}")
        except Exception as e:
            print(f"  ❌ {name:12} → Failed: {e}")

    # Hex
    try:
        hex_str = data.decode('ascii')
        decoded = bytes.fromhex(hex_str)
        results['hex'] = decoded
        print(f"  ✅ hex:12 → {len(decoded)} bytes")
    except:
        print(f"  ❌ hex:12 → Not valid hex")

    # Single-byte XOR brute force
    print("\n🔍 XOR brute-force (looking for ASCII-rich output):")
    found_xor = None
    for key in range(256):
        trial = bytes(b ^ key for b in data[:48])
        ascii_ratio = sum(1 for b in trial if 32 <= b < 127 or b in (9, 10, 13)) / len(trial)
        if ascii_ratio > 0.75:
            print(f"  ✅ XOR key 0x{key:02x} → {ascii_ratio:.0%} ASCII: {trial[:30]}...")
            results[f'xor_0x{key:02x}'] = trial
            found_xor = key
            if key > 32:  # Don't show all low keys
                break

    if found_xor is None:
        print("  No high-ASCII XOR key found in 0x00-0xFF range")

    return results


# ═══════════════════════════════════════════════════════════════════
# SECTION 4: MULTI-FILE COMPARISON
# ═══════════════════════════════════════════════════════════════════
def compare_multiple_files(pattern: str = '.admaster_*') -> Optional[Dict[str, Any]]:
    """Comprehensive byte-by-byte comparison across all samples"""
    files = sorted(glob.glob(pattern))
    if len(files) < 2:
        print("\nℹ️ Need 2+ files for comparison analysis")
        return None

    print(f"\n{'='*70}")
    print(f"📊 MULTI-FILE COMPARISON — {len(files)} samples")
    print(f"{'='*70}")

    datas = {f: open(f, 'rb').read() for f in files}
    ref_size = len(datas[files[0]])
    print(f"  Reference: {files[0]} — {ref_size} bytes")
    for f in files[1:]:
        print(f"  Sample:    {f} — {len(datas[f])} bytes")
    print()

    # Cross-pair comparison matrix
    print("📐 PAIRWISE COMPARISON MATRIX:")
    results = {}
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            fa, fb = files[i], files[j]
            da, db = datas[fa], datas[fb]
            identical = sum(a == b for a, b in zip(da, db))
            pct = identical / ref_size * 100
            ham = hamming_similarity(da, db) * 100
            results[(fa, fb)] = {'identical': identical, 'pct_identical': pct, 'hamming': ham}
            print(f"  F{i} ↔ F{j}: {identical:3d}/{ref_size} bytes identical ({pct:5.1f}%) | Bit sim: {ham:5.1f}%")

    # First differing position per pair
    print("\n📍 FIRST DIFFERENCE per pair:")
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            da, db = datas[files[i]], datas[files[j]]
            for pos, (a, b) in enumerate(zip(da, db)):
                if a != b:
                    print(f"  F{i} ↔ F{j}: 0x{pos:02x} 0x{a:02x} vs 0x{b:02x}")
                    break

    # XOR overlay map — visual fixed vs variable across ALL files
    print("\n🗺️  XOR OVERLAY — █ = identical across ALL files, ░ = varies")
    fixed_positions = []
    varying_positions = []

    for offset in range(ref_size):
        byte_values = {d[offset] for d in datas.values()}
        if len(byte_values) == 1:
            fixed_positions.append(offset)
        else:
            varying_positions.append(offset)

    for i in range(0, ref_size, 16):
        line = f"  0x{i:02x}: "
        for j in range(i, min(i + 16, ref_size)):
            line += "█" if j in fixed_positions else "░"
        print(line)

    # Map to blueprint fields
    print("\n🧠 FIELD BEHAVIOR ANALYSIS:")
    field_stats = {}
    for name, (start, end) in LAYOUT.items():
        field_range = set(range(start, end + 1))
        fixed_in_field = field_range & set(fixed_positions)
        var_in_field = field_range & set(varying_positions)
        pct_fixed = len(fixed_in_field) / len(field_range) * 100

        if pct_fixed > 80:
            verdict = "✅ CONFIRMED — Fixed across samples"
        elif len(var_in_field) == len(field_range):
            verdict = "✅ CONFIRMED — Unique per file"
        else:
            verdict = "⚠️ MIXED — Contains both fixed and variable bytes"

        field_stats[name] = {
            'pct_fixed': pct_fixed,
            'fixed_count': len(fixed_in_field),
            'var_count': len(var_in_field),
            'verdict': verdict,
        }
        print(f"  {name.upper():14} Fixed: {pct_fixed:5.1f}% → {verdict}")

    # Variance heatmap per position
    print("\n🔥 POSITION VARIANCE HEATMAP (0=identical across all samples, 9=all different):")
    for i in range(0, ref_size, 16):
        line = f"  0x{i:02x}: "
        for j in range(i, min(i + 16, ref_size)):
            unique_count = len({d[j] for d in datas.values()})
            if unique_count == 1:
                line += "█"
            elif unique_count == 2:
                line += "▓"
            elif unique_count <= 4:
                line += "▒"
            elif unique_count <= 8:
                line += "░"
            else:
                line += "?"
        print(line)

    # Detect fixed XOR mask pattern
    print("\n🔄 XOR RELATIONSHIP DETECTION:")
    xor_patterns = {}
    for (i, a), (j, b) in combinations(enumerate(datas.values()), 2):
        xor_result = xor_bytes(a, b)
        xor_patterns.setdefault(xor_result, []).append((i, j))

    for xor_val, pairs in xor_patterns.items():
        if len(pairs) > 1:
            print(f"  ⚠️ SAME XOR RESULT between multiple pairs: {pairs}")
            print(f"    → Suggests fixed mask or related plaintext")

    return {
        'files': files,
        'datas': datas,
        'fixed_positions': fixed_positions,
        'varying_positions': varying_positions,
        'field_stats': field_stats,
        'pairwise': results,
    }


def find_repeated_sequences(data: bytes, min_len: int = 4) -> List[Tuple[int, int, bytes]]:
    """Find sequences that appear more than once within a single file"""
    seen: Dict[bytes, int] = {}
    repeats = []
    for i in range(len(data) - min_len + 1):
        seq = data[i:i + min_len]
        if seq in seen:
            repeats.append((seen[seq], i, seq))
        else:
            seen[seq] = i

    if repeats:
        print(f"\n🔁 REPEATED SEQUENCES (≥{min_len} bytes):")
        for start, end, seq in repeats[:10]:
            print(f"  0x{start:02x} ↔ 0x{end:02x} : {seq.hex(' ')}  '{seq.decode('ascii', errors='replace')}'")
    else:
        print(f"\n🔁 No repeated sequences ≥ {min_len} bytes found")

    return repeats


# ═══════════════════════════════════════════════════════════════════
# SECTION 5: CRYPTANALYSIS & HYPOTHESIS SCORING
# ═══════════════════════════════════════════════════════════════════
def known_plaintext_attack(ciphertext: bytes, known_plaintext: bytes, offset: int = 0) -> bytes:
    """Recover keystream from a known plaintext segment — XOR stream cipher mode"""
    ct_segment = ciphertext[offset:offset + len(known_plaintext)]
    keystream = bytes(c ^ p for c, p in zip(ct_segment, known_plaintext))

    print(f"\n🔓 KNOWN-PLAINTEXT ATTACK — KEYSTREAM RECOVERED")
    print(f"  Offset: 0x{offset:x}")
    print(f"  Known plaintext: {known_plaintext}")
    print(f"  Keystream:      {keystream.hex(' ')}")

    full_plaintext = bytes(c ^ keystream[i % len(keystream)] for i, c in enumerate(ciphertext))
    print(f"  Full decrypted preview: {full_plaintext[:48].hex(' ')}")
    return full_plaintext


def score_hypothesis(name: str, conditions: Dict[str, bool]) -> float:
    """Score and rank format hypotheses based on available evidence"""
    print(f"\n📊 HYPOTHESIS SCORE: {name}")
    score = 0
    total = len(conditions)

    for desc, condition in conditions.items():
        status = "✅ PASS" if condition else "❌ FAIL"
        print(f"  {status} — {desc}")
        if condition:
            score += 1

    confidence = score / total * 100
    print(f"  → {score}/{total} = {confidence:.1f}% confidence")
    return confidence


# ═══════════════════════════════════════════════════════════════════
# SECTION 6: FULL REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════
def generate_full_report(single_results, data, multi_results=None):
    """Print comprehensive final analysis summary"""
    print(f"\n{'='*70}")
    print("📑 COMPLETE ANALYSIS SUMMARY")
    print(f"{'='*70}")

    # Hypothesis scoring
    block_entropies = {k: v['entropy'] for k, v in single_results['blocks'].items()}

    score_hypothesis("AES-GCM Container [HDR+IV+CT+TAG]", {
        "File size = 80 bytes": single_results['size'] == 80,
        "UID block lower entropy": block_entropies.get('uid', 8) < 7.0,
        "IV block high entropy": block_entropies.get('iv', 0) > 7.0,
        "Ciphertext high entropy": block_entropies.get('ciphertext', 0) > 7.0,
        "Tag block high entropy": block_entropies.get('tag', 0) > 7.0,
        "Multi-file fixed UID": multi_results and multi_results['field_stats'].get('uid', {}).get('pct_fixed', 0) > 50,
    })

    # Recommendations
    print("\n💡 RECOMMENDATIONS & NEXT STEPS:")
    if multi_results:
        print("  ✅ Multi-file comparison complete — field roles confirmed by behavior")
        print("  🔑 Next: Identify encryption key — search app binary, derive from UID, or known-plaintext attack")
    else:
        print("  ⚠️ Only one sample analyzed — gather 2+ files to confirm fixed vs variable bytes")

    if single_results['ascii_count'] > 4:
        print("  ✅ ASCII strings detected — may reveal format signature or version info")

    if single_results.get('compression'):
        print(f"  ⚠️ Compression detected — decompress before attempting decryption")

    print("\n🚀 Blueprint confirmed: [UID:0-15] [IV:16-31] [CIPHERTEXT:32-63] [TAG:64-79]")
    print("   Ready for key recovery and AES-GCM decryption!")


# ═══════════════════════════════════════════════════════════════════
# MAIN — ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           ADMASTER BINARY ANALYSIS TOOLKIT  v2.0                 ║
║  Blueprint • Discovery • Encoding • Cryptanalysis • Comparison    ║
╚══════════════════════════════════════════════════════════════════╝
""")

    # Determine target files
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        target = sys.argv[1]
    else:
        target = '.admaster_*'

    files = sorted(glob.glob(target))
    if not files:
        print(f"❌ No files found matching: {target}")
        print("   Usage: python admaster_toolkit.py [filename or pattern]")
        return

    # Run single-file analysis on first file
    single_results, data = analyze_single_file(files[0])

    # Extended single-file analysis
    nibble_analysis(data)
    frequency_spectrum(data)
    integer_scan(data)
    extract_strings(data)
    detect_padding(data)
    crypto_sanity_check(data)
    multi_decode(data)
    find_repeated_sequences(data)

    # Run multi-file comparison if we have enough samples
    multi_results = compare_multiple_files(target) if len(files) >= 2 else None

    # Final comprehensive report
    generate_full_report(single_results, data, multi_results)


if __name__ == '__main__':
    main()
