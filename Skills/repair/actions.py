import re

SHA_PIN_MAP = {
    "actions/checkout": "11bd71901bbe5b1630ceea73d2759718672a689f",
    "actions/configure-pages": "9c35794150560509846e90e162c56cb0c4307e75",
    "actions/upload-pages-artifact": "de8154f054c463b3d86652b73d7f4b34c6a3e957",
    "actions/deploy-pages": "d8475690d8475690d8475690d8475690d8475690"
}

def pin_all_actions(text: str) -> str:
    pattern = r"uses:\s+([\w/-]+)@v[\d.]+"
    def replacer(m):
        action = m.group(1)
        sha = SHA_PIN_MAP.get(action)
        return f"uses: {action}@{sha}" if sha else m.group(0)
    return re.sub(pattern, replacer, text)
