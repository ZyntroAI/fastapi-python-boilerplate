import hashlib
import json
import sys
from pathlib import Path


def generate_sha256(file_path: Path, chunk_size: int = 65536) -> str:
    """Computes SHA-256 hash for a file using streaming chunks."""
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def verify_archive_manifest(
    target_dir: str | Path, manifest_file: str = "ARCHIVE-MANIFEST.json"
) -> dict:
    """Verifies target directory against ARCHIVE-MANIFEST.json.

    Optimized with short-circuit size checks, normalized paths, and
    permission handling.
    """
    base_path = Path(target_dir).resolve()
    manifest_path = base_path / manifest_file

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    except PermissionError:
        raise PermissionError(
            f"Permission denied reading manifest: {manifest_path}"
        )

    # Normalize relative paths to POSIX format (forward slashes) for cross-platform compatibility
    expected_files = {
        Path(item["path"]).as_posix(): item
        for item in manifest_data.get("files", [])
    }

    report = {
        "valid": [],
        "modified": [],
        "missing": [],
        "untracked": [],
        "permission_denied": [],
    }

    # 1. Check all files recorded in the manifest
    for rel_path_str, expected_info in expected_files.items():
        file_path = base_path / rel_path_str

        if not file_path.exists():
            report["missing"].append(rel_path_str)
            continue

        try:
            actual_size = file_path.stat().st_size

            # Short-circuit: Skip heavy hashing if file sizes differ
            if actual_size != expected_info["sizeBytes"]:
                report["modified"].append(
                    {
                        "path": rel_path_str,
                        "expected_size": expected_info["sizeBytes"],
                        "actual_size": actual_size,
                        "expected_hash": expected_info["checksum"],
                        "actual_hash": "SKIPPED (Size Mismatch)",
                    }
                )
            else:
                actual_hash = generate_sha256(file_path)
                if actual_hash != expected_info["checksum"]:
                    report["modified"].append(
                        {
                            "path": rel_path_str,
                            "expected_size": expected_info["sizeBytes"],
                            "actual_size": actual_size,
                            "expected_hash": expected_info["checksum"],
                            "actual_hash": actual_hash,
                        }
                    )
                else:
                    report["valid"].append(rel_path_str)

        except PermissionError:
            report["permission_denied"].append(rel_path_str)

    # 2. Check for untracked files in directory
    try:
        for file_path in base_path.rglob("*"):
            try:
                if (
                    file_path.is_dir()
                    or file_path.resolve() == manifest_path.resolve()
                ):
                    continue

                rel_path_str = file_path.relative_to(base_path).as_posix()
                if rel_path_str not in expected_files:
                    report["untracked"].append(rel_path_str)

            except PermissionError:
                rel_path_str = file_path.relative_to(base_path).as_posix()
                if rel_path_str not in report["permission_denied"]:
                    report["permission_denied"].append(rel_path_str)
    except PermissionError:
        print(
            f"[!] Warning: Permission denied during directory traversal of {base_path}",
            file=sys.stderr,
        )

    return report


def print_verification_summary(report: dict) -> bool:
    """Prints a formatted summary report and returns True if directory matches manifest perfectly."""
    print("=== ARCHIVE VERIFICATION REPORT ===")
    print(f"Valid Files        : {len(report['valid'])}")
    print(f"Modified Files     : {len(report['modified'])}")
    print(f"Missing Files      : {len(report['missing'])}")
    print(f"Untracked Files    : {len(report['untracked'])}")
    print(f"Permission Denied  : {len(report['permission_denied'])}")
    print("=" * 35)

    is_healthy = (
        not report["modified"]
        and not report["missing"]
        and not report["untracked"]
        and not report["permission_denied"]
    )

    if report["modified"]:
        print("\n[!] MODIFIED / CORRUPTED FILES:")
        for item in report["modified"]:
            print(f"  - {item['path']}")
            print(
                f"    Expected Hash: {item['expected_hash'][:12]}... (Size: {item['expected_size']} B)"
            )
            print(
                f"    Actual Hash:   {item['actual_hash'][:12] if len(item['actual_hash']) == 64 else item['actual_hash']} (Size: {item['actual_size']} B)"
            )

    if report["missing"]:
        print("\n[!] MISSING FILES:")
        for path in report["missing"]:
            print(f"  - {path}")

    if report["untracked"]:
        print("\n[!] UNTRACKED FILES:")
        for path in report["untracked"]:
            print(f"  - {path}")

    if report["permission_denied"]:
        print("\n[!] PERMISSION DENIED (UNABLE TO VERIFY):")
        for path in report["permission_denied"]:
            print(f"  - {path}")

    if is_healthy:
        print("\nSUCCESS: All files match the manifest perfectly.")

    return is_healthy


if __name__ == "__main__":
    target_directory = sys.argv[1] if len(sys.argv) > 1 else "."
    try:
        report_data = verify_archive_manifest(target_directory)
        success = print_verification_summary(report_data)
        sys.exit(0 if success else 1)
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(2)
