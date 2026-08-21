🇹🇭 Python: Auto Generate Knowledge

ถ้าจะใช้ Python แทน TypeScript ผมแนะนำให้แยกเป็น reusable script แล้วให้ GitHub Actions เรียกใช้ เพื่อสร้าง Knowledge จาก PR / Issue / CI event

Structure

scripts/
└── knowledge/
    ├── __init__.py
    ├── generator.py
    ├── github.py
    └── models.py

docs/
└── knowledge/
    ├── prs/
    ├── issues/
    ├── ci-cd/
    ├── dependencies/
    ├── security/
    └── decisions/

scripts/knowledge/models.py

from dataclasses import dataclass, field


@dataclass
class Knowledge:
    title: str
    knowledge_type: str
    source: str
    summary: str
    status: str = "active"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

scripts/knowledge/generator.py

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from models import Knowledge


ROOT = Path("docs/knowledge")


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def render(item: Knowledge) -> str:
    tags = ", ".join(f"`{tag}`" for tag in item.tags)

    metadata = "\n".join(
        f"- {key}: `{value}`"
        for key, value in item.metadata.items()
    )

    return f"""# {item.title}

## Metadata

- Type: `{item.knowledge_type}`
- Status: `{item.status}`
- Source: {item.source}
- Generated: `{datetime.now(timezone.utc).isoformat()}`
- Tags: {tags}

{metadata}

## Summary

{item.summary}

## Automation

This document was generated automatically from GitHub repository activity.

## Source

{item.source}
"""


def generate(item: Knowledge) -> Path:
    category = slugify(item.knowledge_type)
    directory = ROOT / category

    directory.mkdir(parents=True, exist_ok=True)

    filename = f"{slugify(item.title)}.md"
    output = directory / filename

    output.write_text(
        render(item),
        encoding="utf-8",
    )

    return output


def main() -> None:
    item = Knowledge(
        title=os.getenv(
            "KNOWLEDGE_TITLE",
            "CrystalCastle Repository Activity",
        ),
        knowledge_type=os.getenv(
            "KNOWLEDGE_TYPE",
            "ci-cd",
        ),
        source=os.getenv(
            "KNOWLEDGE_SOURCE",
            "https://github.com/ZyntroAI/new-crystalcastle",
        ),
        summary=os.getenv(
            "KNOWLEDGE_SUMMARY",
            "Automated knowledge generated from GitHub activity.",
        ),
        tags=os.getenv(
            "KNOWLEDGE_TAGS",
            "github,automation,ci-cd",
        ).split(","),
        metadata={
            "Event": os.getenv("GITHUB_EVENT_NAME", "local"),
            "Repository": os.getenv(
                "GITHUB_REPOSITORY",
                "ZyntroAI/new-crystalcastle",
            ),
            "Ref": os.getenv("GITHUB_REF", "local"),
            "SHA": os.getenv("GITHUB_SHA", "local"),
        },
    )

    output = generate(item)

    print(f"Knowledge generated: {output}")


if __name__ == "__main__":
    main()

requirements.txt

ไม่จำเป็นต้องลง package เพิ่มสำหรับ generator ตัวนี้ เพราะใช้ Python standard library:

# No external dependencies

GitHub Actions

.github/workflows/knowledge-auto-generate.yml

name: Knowledge Auto Generate

on:
  pull_request:
    types:
      - opened
      - closed
      - synchronize

  issues:
    types:
      - opened
      - closed

  workflow_run:
    workflows:
      - CrystalCastle CodeRabbit + Tests
      - Dependency Review
    types:
      - completed

  workflow_dispatch:

permissions:
  contents: write
  pull-requests: read
  issues: read
  actions: read

concurrency:
  group: knowledge-${{ github.ref }}
  cancel-in-progress: true

jobs:
  generate:
    name: Generate Knowledge
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Generate knowledge
        env:
          KNOWLEDGE_TITLE: "CrystalCastle Repository Activity"
          KNOWLEDGE_TYPE: "ci-cd"
          KNOWLEDGE_SOURCE: "https://github.com/${{ github.repository }}"
          KNOWLEDGE_SUMMARY: |
            Automated knowledge generated from GitHub activity.
            Event: ${{ github.event_name }}
            Ref: ${{ github.ref }}
            SHA: ${{ github.sha }}
          KNOWLEDGE_TAGS: "github,automation,ci-cd,knowledge"
        run: |
          PYTHONPATH=scripts/knowledge \
            python scripts/knowledge/generator.py

      - name: Commit knowledge
        run: |
          git config user.name "github-actions[bot]"
          git config user.email \
            "41898282+github-actions[bot]@users.noreply.github.com"

          git add docs/knowledge/

          if git diff --cached --quiet; then
            echo "No knowledge changes."
            exit 0
          fi

          git commit \
            -m "docs(knowledge): auto-generate repository knowledge"

          git push

🇬🇧 Knowledge Pipeline

GitHub
  │
  ├── Pull Request
  ├── Issue
  ├── CI
  ├── Dependency Review
  └── CodeRabbit
          │
          ▼
   Python Generator
          │
     ┌────┼────┐
     ▼    ▼    ▼
    PR   CI   Security
     │    │     │
     └────┼─────┘
          ▼
   Markdown Knowledge
          │
          ▼
docs/knowledge/

สำหรับ new-crystalcastle ผมแนะนำให้ Python เป็น knowledge engine และให้ GitHub Actions เป็น event/orchestration layer ส่วน Slack CLI เป็น notification layer:

GitHub → Python Knowledge → Markdown → CI → Slack CLI

I can also add GitHub API extraction so Python automatically generates knowledge from actual PR #59, Issues, reviews, and workflow results.
