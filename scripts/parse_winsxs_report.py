import argparse
import json
import re
from pathlib import Path


SIZE_FIELDS = {
    "explorer_reported_size": (
        "Windows Explorer Reported Size of Component Store"
    ),
    "actual_component_store_size": "Actual Size of Component Store",
    "shared_with_windows": "Shared with Windows",
    "backups_and_disabled_features": "Backups and Disabled Features",
    "cache_and_temporary_data": "Cache and Temporary Data",
}

TEXT_FIELDS = {
    "last_cleanup": "Date of Last Cleanup",
    "cleanup_recommended": "Component Store Cleanup Recommended",
}

UNITS = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3,
    "TB": 1024 ** 4,
}


def extract_value(text, label):
    pattern = rf"^s*{re.escape(label)}s*:s*(.*?)s*$"
    match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1) if match else None


def parse_size(value):
    if value is None:
        return None

    match = re.fullmatch(
        r"([d.,]+)s*(B|KB|MB|GB|TB)",
        value.strip(),
        flags=re.IGNORECASE,
    )
    if not match:
        return {"text": value, "bytes": None}

    number_text, unit = match.groups()

    # English reports normally use a decimal point.
    # Accept a decimal comma when no decimal point is present.
    if "," in number_text and "." not in number_text:
        number_text = number_text.replace(",", ".")
    else:
        number_text = number_text.replace(",", "")

    try:
        size_bytes = round(float(number_text) * UNITS[unit.upper()])
    except ValueError:
        size_bytes = None

    return {"text": value, "bytes": size_bytes}


def parse_report(text):
    result = {
        name: parse_size(extract_value(text, label))
        for name, label in SIZE_FIELDS.items()
    }

    for name, label in TEXT_FIELDS.items():
        result[name] = extract_value(text, label)

    recommendation = result["cleanup_recommended"]
    if recommendation is not None:
        result["cleanup_recommended"] = {
            "yes": True,
            "no": False,
        }.get(recommendation.casefold())

    packages = extract_value(
        text, "Number of Reclaimable Packages"
    )
    result["reclaimable_packages"] = (
        int(packages) if packages and packages.isdigit() else None
    )

    exit_code = extract_value(text, "Exit code")
    result["dism_exit_code"] = (
        int(exit_code)
        if exit_code and re.fullmatch(r"-?d+", exit_code)
        else None
    )

    overhead_parts = [
        result["backups_and_disabled_features"],
        result["cache_and_temporary_data"],
    ]

    result["estimated_overhead_bytes"] = (
        sum(part["bytes"] for part in overhead_parts)
        if all(
            part is not None and part["bytes"] is not None
            for part in overhead_parts
        )
        else None
    )

    result["missing_size_fields"] = [
        name for name in SIZE_FIELDS if result[name] is None
    ]

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Parse an English DISM component-store report."
    )
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        text = args.report.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        parser.error(f"Unable to read report: {error}")

    result = parse_report(text)
    output = json.dumps(result, indent=2, ensure_ascii=False)
    print(output)

    if args.output:
        args.output.write_text(output + "
", encoding="utf-8")
        print(f"
JSON saved to: {args.output}")


if __name__ == "__main__":
    main()