Claude Skills Suggest

## Claude Skills suggestions

Claude Skills are reusable instruction packages for specialized, repeatable workflows. A Skill requires a `SKILL.md` file with YAML frontmatter and Markdown instructions; optional `scripts/`, `references/`, and `assets/` directories can provide executable code, detailed references, and templates.[1]

### Best starter Skills

| Skill | What it does | Output |
|---|---|---|
| `supabase-docs-guidelines` | Creates consistent Supabase technical and compliance documents | Markdown, HTML, or PDF |
| `audit-log-review` | Reviews Supabase Auth, Platform, and database audit events | Findings report |
| `oauth-app-documenter` | Documents OAuth apps, redirect URIs, scopes, and secrets | Configuration record |
| `feature-preview-evaluator` | Evaluates Supabase preview features safely | Risk and rollout report |
| `save-pages-html` | Converts approved content into standalone HTML | `.html` file |
| `research-brief` | Produces sourced research briefs | Markdown or PDF |
| `meeting-to-actions` | Converts notes into decisions and action items | Action register |
| `security-review` | Reviews configuration against a checklist | Findings and remediation plan |
| `release-notes` | Converts commits and tickets into release notes | Markdown or HTML |
| `data-dictionary` | Documents database tables, columns, and ownership | Markdown or CSV |

## Recommended first Skill

Based on your recent Supabase documentation work, start with **`supabase-docs-guidelines`**. Keep it focused on producing repeatable documentation rather than making changes to Supabase.

```text
supabase-docs-guidelines/
├── SKILL.md
├── references/
│   ├── document-template.md
│   ├── security-checklist.md
│   └── compliance-matrix.md
└── assets/
    └── document-header.md
```

## Ready-to-use `SKILL.md`

```markdown
---
name: supabase-docs-guidelines
description: Create structured Supabase documentation for OAuth, SSO, audit logs, log drains, feature previews, security controls, legal records, and operational runbooks. Use when the user asks to document, review, standardize, or create guidelines for a Supabase configuration.
---

# Supabase Documentation Guidelines

## Purpose

Create accurate, practical, reviewable documentation for Supabase projects and organizations.

## Scope

Support these document types:

- OAuth and OIDC application records.
- SAML SSO configuration records.
- Auth Audit Log documentation.
- Platform Audit Log and Audit Log Drain records.
- PostgreSQL and PGAudit configuration.
- Feature Preview evaluations.
- Security and compliance control records.
- Legal and privacy document registers.
- Operational runbooks.
- Change and approval records.

## Workflow

1. Identify the Supabase product area.
2. Determine whether the document covers a project, organization, application, environment, or external service.
3. Separate current facts from assumptions.
4. Identify sensitive values that must not appear in the document.
5. Create a structured document with ownership, scope, configuration, risks, validation, and review information.
6. Include development, staging, and production distinctions.
7. Add a rollback or incident procedure when the feature can change external or persistent state.
8. Add a security and privacy section when logs, credentials, personal data, or regulated data are involved.
9. Add a source and version section for Supabase documentation and legal materials.
10. Finish with a checklist and approval record.

## Required sections

Use these sections whenever applicable:

- Document control.
- Purpose and scope.
- Environment and project identifiers.
- Architecture or data flow.
- Configuration.
- Ownership and access.
- Security requirements.
- Privacy and compliance.
- Testing and validation.
- Monitoring and alerting.
- Failure handling.
- Rollback or recovery.
- Retention and deletion.
- Change history.
- Approval.

## Security rules

- Never include passwords, API secrets, private keys, refresh tokens, access tokens, or raw credentials.
- Use secret-manager references instead of secret values.
- Distinguish public identifiers from confidential credentials.
- Apply least privilege to users, service accounts, OAuth apps, and log destinations.
- Use HTTPS and encrypted transport in staging and production.
- Separate development, staging, and production configuration.
- Require explicit approval before sending, publishing, deleting, or changing external resources.
- Mark unknown values as `TBD`; do not invent them.
- Redact personal data from examples and screenshots.

## Supabase-specific checks

For Auth and OAuth:

- Record provider, client type, redirect URIs, scopes, consent status, and secret expiry.
- Validate redirect URIs against the Supabase allow list.
- Prefer authorization code flow with PKCE for public clients.
- Keep confidential client secrets on the server side.

For SSO:

- Record IdP metadata, ACS URL, entity ID, certificate ownership, expiry, and attribute mappings.
- Document certificate renewal and break-glass access.
- Test both SP-initiated and IdP-initiated flows when supported.

For audit logs:

- Separate Auth Audit Logs, Platform Audit Logs, and PostgreSQL/PGAudit logs.
- Record retention, access, monitoring, and export destinations.
- Document whether database storage or external log storage is enabled.

For Log Drains:

- Record destination, endpoint reference, authentication method, encryption, batching, retry behavior, retention, and cost owner.
- Store credentials outside the document.
- Test event delivery and destination outage behavior.

For Feature Previews:

- Record feature stage, owner, evaluation scope, enablement date, risks, test results, feedback link, and rollback method.
- Do not approve production use without validation and a recovery plan.

For legal documents:

- Record document name, version, effective date, source URL, applicability, legal owner, review date, and approval status.
- Do not copy legal conclusions without legal review.
- Link the Terms of Service, DPA, Subprocessor List, privacy materials, and security evidence where relevant.

## Writing standards

- Use plain language.
- Use Markdown headings and tables.
- Prefer checklists for controls.
- Use YAML or JSON for machine-readable configuration.
- Put exact field names in code formatting.
- Explain the purpose of each sensitive configuration item.
- Distinguish required, optional, and environment-specific values.
- Use UTC for timestamps.
- Identify the authoritative source and retrieval date.
- Keep recommendations separate from confirmed configuration.

## Output format

Unless the user requests another format, produce:

1. A short purpose statement.
2. A structured document.
3. A configuration table.
4. A security and privacy checklist.
5. A validation checklist.
6. A rollback or incident section when applicable.
7. A final approval record.

## Quality checklist

- [ ] Scope is clear.
- [ ] Project and environment are identified.
- [ ] Owners are assigned.
- [ ] Secrets are not exposed.
- [ ] Production differences are documented.
- [ ] Security controls are explicit.
- [ ] Retention and access are defined.
- [ ] Testing is reproducible.
- [ ] Rollback or recovery is addressed.
- [ ] Unknown values are marked `TBD`.
- [ ] Source URLs and document versions are recorded.
- [ ] Legal or compliance claims are marked for review.
```

## Other useful Skills

### `oauth-app-documenter`

Use it for requests such as:

- “Document our Google OAuth app.”
- “Create an OAuth redirect URI record.”
- “Review our Supabase OAuth configuration.”
- “Prepare an OAuth security checklist.”

Recommended behavior:

- Separate public client IDs from secrets.
- Record exact redirect URIs by environment.
- List scopes and their business justification.
- Track secret expiration and rotation.
- Require review for broad permissions.

### `audit-log-review`

Use it for:

- “Review these Supabase audit logs.”
- “Find suspicious authentication activity.”
- “Summarize platform-admin changes.”
- “Prepare an audit-log evidence report.”

Recommended output:

- Time range.
- Event counts.
- High-risk events.
- Affected projects or users.
- Evidence references.
- False-positive notes.
- Recommended actions.

### `feature-preview-evaluator`

Use it for:

- “Evaluate this Supabase preview feature.”
- “Create a rollout plan.”
- “Document a Feature Preview.”
- “Prepare a rollback plan.”

Recommended output:

- Purpose.
- Current feature stage.
- Development test plan.
- Staging criteria.
- Production gate.
- Rollback method.
- Feedback and review dates.

## Claude installation structure

For Claude Code, a personal Skill can be placed under:

```text
~/.claude/skills/supabase-docs-guidelines/SKILL.md
```

A project-specific Skill can be committed under:

```text
.claude/skills/supabase-docs-guidelines/SKILL.md
```

Claude Code can invoke a Skill explicitly with `/supabase-docs-guidelines` or load it automatically when the description matches the request.[2]

For Claude.ai or API uploads, package the directory with `SKILL.md` at the expected skill-directory level. Anthropic’s documentation recommends validating the package, checking referenced files, testing representative prompts, and keeping the main `SKILL.md` under 500 lines.[1]

## Design recommendations

- Create several focused Skills instead of one large “Supabase everything” Skill.
- Keep factual reference material in `references/`.
- Keep templates and schemas in `assets/`.
- Add scripts only when deterministic processing is needed.
- Make external actions draft-only unless approval is explicitly required.
- Review downloaded or community Skills before enabling them.
- Never hardcode credentials or private infrastructure details.

Anthropic recommends focused Skills, clear activation descriptions, examples, incremental testing, composability, and careful review of downloaded Skills.[1]

การอ้างอิง:
[1] Creating custom skills - Claude.ai Documentation https://claude.com/docs/skills/how-to
[2] Extend Claude with skills - Claude Code Docs https://docs.anthropic.com/en/docs/claude-code/skills
[3] Documentation - Claude Platform Docs https://docs.anthropic.com/
[4] Using Agent Skills with the API - Claude Platform Docs https://docs.anthropic.com/en/build-with-claude/skills-guide
[5] Extend Claude Code - Claude Code Docs https://docs.anthropic.com/en/docs/claude-code/features-overview
[6] Claude Cookbook https://docs.anthropic.com/en/docs/resources/cookbook
[7] Get started with Agent Skills in the API - Claude Platform Docs https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/quickstart
[8] Jeffallan/claude-skills: 67 Specialized Skills for Full-Stack ... https://github.com/jeffallan/claude-skills
[9] Collection of Claude Code skills for enhanced AI workflows · GitHub https://github.com/glebis/claude-skills
[10] ComposioHQ/awesome-claude-skills https://github.com/ComposioHQ/awesome-claude-skills
[11] simonw/claude-skills https://github.com/simonw/claude-skills
[12] jezweb/claude-skills: Skills for Claude Code CLI such as ... https://github.com/jezweb/claude-skills
[13] GitHub - anthropics/skills: Public repository for Agent Skills https://github.com/anthropics/skills
[14] Discover Claude Skills on GitHub https://claudeskillsgithub.com/
[15] GitHub Official Skills - Claude Skills Hub https://claudeskills.info/official/github/
