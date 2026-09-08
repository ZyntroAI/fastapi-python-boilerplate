def standardize_indentation(text: str, spaces: int = 2) -> str:
    lines = text.split("\n")
    normalized = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped:
            normalized.append("")
            continue
        indent_level = len(line) - len(stripped)
        normalized.append(" " * (indent_level // 2 * spaces) + stripped)
    return "\n".join(normalized)
