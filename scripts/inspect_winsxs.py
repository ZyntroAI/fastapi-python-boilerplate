import heapq
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("SystemRoot", r"C:Windows")) / "WinSxS"
TOP_N = 20


def gib(size):
    return f"{size / (1024 ** 3):,.3f} GiB"


def inspect(root):
    folder_sizes = defaultdict(int)
    largest_files = []
    errors = []
    file_count = 0
    logical_total = 0
    skipped_links = 0

    def on_error(error):
        errors.append(str(error))

    for current, directories, filenames in os.walk(
        root, topdown=True, onerror=on_error, followlinks=False
    ):
        current = Path(current)

        # Avoid following directory links or junctions.
        allowed = []
        for name in directories:
            path = current / name
            try:
                is_junction = getattr(path, "is_junction", lambda: False)
                if path.is_symlink() or is_junction():
                    skipped_links += 1
                else:
                    allowed.append(name)
            except OSError as error:
                errors.append(f"{path}: {error}")
        directories[:] = allowed

        relative = current.relative_to(root)
        group = relative.parts[0] if relative.parts else "(root files)"

        for name in filenames:
            path = current / name
            try:
                if path.is_symlink():
                    skipped_links += 1
                    continue

                size = path.stat().st_size
            except OSError as error:
                errors.append(f"{path}: {error}")
                continue

            file_count += 1
            logical_total += size
            folder_sizes[group] += size

            item = (size, str(path))
            if len(largest_files) < TOP_N:
                heapq.heappush(largest_files, item)
            elif item > largest_files[0]:
                heapq.heapreplace(largest_files, item)

    print(f"Folder: {root}")
    print(f"Accessible files: {file_count:,}")
    print(f"Logical total: {gib(logical_total)}")
    print(f"Skipped links/junctions: {skipped_links:,}")
    print(f"Access/read errors: {len(errors):,}")
    print("Logical sizes do NOT equal reclaimable space.")

    print(f"
Top {TOP_N} immediate subfolders by logical size:")
    for name, size in sorted(
        folder_sizes.items(), key=lambda item: item[1], reverse=True
    )[:TOP_N]:
        print(f"{gib(size):>14}  {name}")

    print(f"
Top {TOP_N} files by logical size:")
    for size, path in sorted(largest_files, reverse=True):
        print(f"{gib(size):>14}  {path}")

    if errors:
        print("
First 10 errors; results may be incomplete:")
        for error in errors[:10]:
            print(error)


if __name__ == "__main__":
    if not ROOT.is_dir():
        raise SystemExit(f"Folder not found or inaccessible: {ROOT}")
    inspect(ROOT)