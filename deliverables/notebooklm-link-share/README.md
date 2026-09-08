# NotebookLM Link & Sharing Mastery

Pure-stdlib skill to normalize private/artifact NotebookLM links to clean public
URLs, validate structure, and generate share-ready templates.

## Usage
```python
from notebooklm_link_share import normalize_link, public_skill

raw = "https://notebooklm.google.com/notebook/c763d2b6-f074-4090-95cc-03d2592253bd/artifact/7f72e937-9018-4a11-9f4b-0952ad1601ff?utm_source=x"
normalize_link(raw)   # -> https://notebooklm.google.com/notebook/c763d2b6-f074-4090-95cc-03d2592253bd

public_skill(raw, style="short", title="My Doc")
# -> {"clean_url": ..., "validation": {...}, "share_template": "..."}
```

## API
- `normalize_link(url)` -> clean URL (raises NotebookLMError on invalid host/UUID)
- `normalize_skill(url)` -> `{"clean_url": ...}`
- `public_skill(url, style, title, contact)` -> clean_url + validation + share_template
- `generate_share_text(clean_url, style, title, contact)` -> short | detailed | formal
- `validate_link(clean_url)` -> `{valid, checks, recommendation}`
- `is_valid_uuid(uuid)`

## Test
```bash
python -m pytest tests/ -q    # 9 passed
```
