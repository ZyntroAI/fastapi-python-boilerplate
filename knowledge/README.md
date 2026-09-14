# Knowledge Base

Curated, source-referenced notes that support this project. Each note is a single
Markdown file with YAML front matter, suitable for shelling into an Obsidian vault.

**Last updated:** 2026-09-13

## Index

| Note | Area | Sources | Words |
|---|---|---:|---:|
| [GitHub Actions SHA Pinning Guidelines](github-actions-sha-pinning-guidelines.md) | Engineering / CI-CD | 12 | 944 |
| [Supabase Audit Log Drains Guidelines](supabase-audit-log-drains-guidelines.md) | Platform / Logging | 12 | 1,557 |
| [Supabase Audit Logs Guideline](supabase-audit-logs-guideline.md) | Auth / Platform / Database | 15 | 1,630 |
| [Supabase Feature Preview Guidelines](supabase-feature-preview-guidelines.md) | Platform / Change Control | 14 | 1,258 |
| [Supabase Legal Documents Guidelines](supabase-legal-documents-guidelines.md) | Legal / Compliance | 14 | 1,585 |
| [Supabase OAuth Apps Guidelines](supabase-oauth-apps-guidelines.md) | Auth / OAuth | 15 | 1,354 |
| [Supabase SSO Signing Guidelines](supabase-sso-signing-guidelines.md) | Auth / SSO | 15 | 1,294 |

## Tag index

| Tag | Notes | Members |
|---|---:|---|
| `#knowledge/authentication` | 2 | [supabase-oauth-apps-guidelines.md](supabase-oauth-apps-guidelines.md), [supabase-sso-signing-guidelines.md](supabase-sso-signing-guidelines.md) |
| `#knowledge/change-control` | 1 | [supabase-feature-preview-guidelines.md](supabase-feature-preview-guidelines.md) |
| `#knowledge/ci` | 1 | [github-actions-sha-pinning-guidelines.md](github-actions-sha-pinning-guidelines.md) |
| `#knowledge/compliance` | 2 | [supabase-audit-logs-guideline.md](supabase-audit-logs-guideline.md), [supabase-legal-documents-guidelines.md](supabase-legal-documents-guidelines.md) |
| `#knowledge/github-actions` | 1 | [github-actions-sha-pinning-guidelines.md](github-actions-sha-pinning-guidelines.md) |
| `#knowledge/legal` | 1 | [supabase-legal-documents-guidelines.md](supabase-legal-documents-guidelines.md) |
| `#knowledge/observability` | 1 | [supabase-audit-log-drains-guidelines.md](supabase-audit-log-drains-guidelines.md) |
| `#knowledge/platform` | 1 | [supabase-feature-preview-guidelines.md](supabase-feature-preview-guidelines.md) |
| `#knowledge/security` | 5 | [github-actions-sha-pinning-guidelines.md](github-actions-sha-pinning-guidelines.md), [supabase-audit-log-drains-guidelines.md](supabase-audit-log-drains-guidelines.md), [supabase-audit-logs-guideline.md](supabase-audit-logs-guideline.md), [supabase-oauth-apps-guidelines.md](supabase-oauth-apps-guidelines.md), [supabase-sso-signing-guidelines.md](supabase-sso-signing-guidelines.md) |
| `#knowledge/supabase` | 6 | [supabase-audit-log-drains-guidelines.md](supabase-audit-log-drains-guidelines.md), [supabase-audit-logs-guideline.md](supabase-audit-logs-guideline.md), [supabase-feature-preview-guidelines.md](supabase-feature-preview-guidelines.md), [supabase-legal-documents-guidelines.md](supabase-legal-documents-guidelines.md), [supabase-oauth-apps-guidelines.md](supabase-oauth-apps-guidelines.md), [supabase-sso-signing-guidelines.md](supabase-sso-signing-guidelines.md) |
| `#knowledge/supply-chain` | 1 | [github-actions-sha-pinning-guidelines.md](github-actions-sha-pinning-guidelines.md) |

## Conventions

- **Filename** — lowercase kebab-case with a `.md` extension.
- **Front matter** — `title`, `description`, `tags`, `supabase_area`, `doc_kind`,
  `status`, `owner`, `last_reviewed`, `review_frequency`, `source`.
- **Tags** — hierarchical `knowledge/<value>` (see `tags` above).
- **Citations** — each note ends with a `การอ้างอิง:` block listing numbered
  `[n] Title URL` entries; inline markers `[n]` refer to it. Preserve both.
- **Never** put credentials, client secrets, tokens, or private keys in a note.

> This index is generated — run `python3 knowledge/build_knowledge_readme.py`
> after adding or editing a note. `--check` verifies it in CI.
