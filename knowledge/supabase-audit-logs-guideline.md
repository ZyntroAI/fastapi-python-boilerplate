---
title: "Supabase Audit Logs Guideline"
description: "The three Supabase audit-log areas — Auth, Platform, and database/PGAudit — documented as separate controls."
tags:
  - knowledge/supabase
  - knowledge/security
  - knowledge/compliance
supabase_area: "Auth / Platform / Database"
doc_kind: "guideline"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-13"
review_frequency: "Annual"
source: "Supabase official documentation"
---

Supabase Audit Logs Document Guideline

## Supabase audit-log guidelines

Supabase has three distinct audit-log areas. Document them separately rather than combining them into one generic “audit log” record:

| Log type | Purpose | Main scope |
|---|---|---|
| Auth Audit Logs | User authentication and account-security events | Supabase project |
| Platform Audit Logs | Organization-member and dashboard/API administrative actions | Supabase organization |
| PostgreSQL/PGAudit logs | Database statements, schema changes, roles, and selected objects | Supabase database |

Auth events are automatically captured. Platform actions are automatically logged, while database auditing requires explicit configuration such as PGAudit or connection logging.[1][2][3]

## Document-control template

```markdown
# Supabase Audit Logging Standard

## Document control

- Document owner:
- Security owner:
- Supabase organization:
- Project:
- Environment:
- Version:
- Effective date:
- Last reviewed:
- Next review:
- Approval ticket:

## Purpose

Define what Supabase activities are logged, where logs are stored,
who can access them, how long they are retained, and how alerts
and investigations are handled.

## Scope

- Authentication events
- Organization and project administration
- Database activity
- Postgres connection activity
- Edge, API, Storage, and Realtime logs where applicable
- External log destinations

## Systems covered

- Project reference:
- Supabase organization:
- Production:
- Staging:
- Development:
```

## Auth Audit Logs

Supabase Auth Audit Logs capture events such as sign-ups, sign-ins, password changes, password resets, email verification, token refresh, sign-out, invitations, account changes, and MFA operations. The documented action names include `login`, `logout`, `user_signedup`, `user_deleted`, `user_updated_password`, `token_revoked`, `token_refreshed`, `challenge_created`, `verification_attempted`, and factor-management events.[1]

Document the storage decision:

```markdown
## Auth audit-log storage

- Auth logs enabled: Yes / No
- External log storage: Enabled / Disabled
- Database storage: Enabled / Disabled
- Database table: auth.audit_log_entries
- Reason for database-storage decision:
- Query owner:
- Retention policy:
- Export or forwarding method:
```

Supabase provides external log storage and optional PostgreSQL storage in `auth.audit_log_entries`. Database storage is searchable through SQL but consumes database storage, so the choice should be documented as a cost, queryability, and compliance decision.[1]

Example event record:

```json
{
  "timestamp": "2026-09-13T14:00:00Z",
  "user_id": "uuid",
  "action": "login",
  "ip_address": "redacted-or-controlled",
  "user_agent": "redacted-or-controlled",
  "metadata": {
    "provider": "email"
  }
}
```

Do not copy raw audit events containing personal data into tickets, public documents, or chat channels.

## Platform Audit Logs

Platform Audit Logs record organization-member activity performed through the Supabase Dashboard or Platform API. Examples include creating projects, inviting members, changing project settings, and modifying Edge Functions. Each entry can include the timestamp, actor, IP address, email, token type, action, metadata, response status, and target.[2]

Use this section:

```markdown
## Platform audit logging

- Enabled by plan: Team / Enterprise
- Dashboard location:
- Organization:
- Log-drain status:
- Log destination:
- Destination owner:
- Alerting owner:
- Access reviewers:
- Retention period:
- Export limitation acknowledged: Yes / No

## High-risk actions

Alert or review actions involving:

- Organization-owner changes
- Member invitations or removals
- Project creation or deletion
- Project-setting changes
- Secret or credential changes
- Edge Function deployment or modification
- Database configuration changes
- Audit-log-drain changes
```

Supabase states that Platform Audit Logs are available on Team and Enterprise plans. They can be viewed in the organization dashboard or streamed through Audit Log Drains, while dashboard export is currently limited.[2]

## Database and PGAudit

PGAudit extends PostgreSQL logging so you can selectively track reads, writes, functions, role changes, DDL, or other database activity. It supports session, user, global, and object-level approaches.[3]

Document the configuration precisely:

```markdown
## Database audit configuration

- PGAudit enabled: Yes / No
- Connection logging enabled: Yes / No
- Logging scope: Session / User / Object / Global
- Monitored roles:
- Monitored objects:
- Logged categories:
- Log destination:
- Review frequency:
- Performance owner:
```

Common PGAudit categories are:

| Category | Records |
|---|---|
| `read` | `SELECT` and `COPY` data retrieval |
| `write` | `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, and related changes |
| `function` | Function, procedure, and `DO` block execution |
| `role` | User and privilege changes |
| `ddl` | `CREATE`, `ALTER`, and `DROP` schema operations |
| `all` | All supported categories |

Start narrowly. For example, monitor DDL and role changes first, then add targeted write or object logging when the risk assessment justifies it. Global `all` logging can create excessive volume and make important events harder to find.[3]

Example role-scoped configuration:

```sql
alter role "migration_runner"
set pgaudit.log to 'ddl, role';
```

Example object-focused design:

```sql
create role "auth_auditor" noinherit;

grant select on auth.users to "auth_auditor";
grant delete on auth.users to "auth_auditor";

alter role "postgres"
set pgaudit.role to 'auth_auditor';
```

Use object-level logging cautiously, especially around `auth.users` and other sensitive tables. PGAudit records statements, not returned rows by default. Enabling row logging can expose sensitive values and affect performance, so it should require documented approval.[3]

## Connection logging

If your compliance program requires database connection evidence, document whether connection logging is enabled. Supabase can record connection lifecycle events such as connection received, authenticated, and authorized. New projects have connection logging off by default according to the current documentation.[4][5]

```markdown
## PostgreSQL connection logging

- Setting: On / Off
- Reason:
- Events collected:
- Monitoring query:
- Review frequency:
- Privacy assessment:
- Performance assessment:
```

Connection logs should not be treated as a replacement for statement-level PGAudit. They answer different questions:

- Connection logs: who connected and whether the connection was authenticated or authorized.
- PGAudit: what database activity was performed.

## Retention and access

Your document should define:

- Retention period by log type.
- Legal or regulatory requirements.
- Whether logs are immutable.
- Who can view raw events.
- Who can change logging configuration.
- How access is reviewed.
- How sensitive fields are protected.
- How incidents are preserved beyond normal retention.
- Whether logs are copied to an external SIEM.

Supabase’s available log retention depends on plan and product area, so record the actual retention visible for your plan instead of assuming one universal period.[2][6]

```markdown
## Retention matrix

| Log type | Supabase retention | External retention | Owner |
|---|---:|---:|---|
| Auth audit logs | Confirm in dashboard |  |  |
| Platform audit logs | Confirm by plan |  |  |
| Postgres logs | Confirm in dashboard |  |  |
| PGAudit events | Confirm in dashboard |  |  |
| Connection logs | Confirm in dashboard |  |  |
```

## Monitoring and review

Define both routine review and alerting:

```markdown
## Review procedure

1. Review high-risk authentication events.
2. Review organization-member administrative activity.
3. Review privileged database activity.
4. Investigate repeated failed sign-ins or MFA failures.
5. Check for unexpected changes to roles, schemas, or audit settings.
6. Record findings in the security review register.
7. Escalate confirmed incidents according to the incident-response plan.
```

Useful review signals include:

- Repeated failed login or verification attempts.
- Password recovery activity on privileged accounts.
- MFA factor enrollment or removal.
- Token revocation or unusual refresh activity.
- New organization members.
- Project deletion or setting changes.
- Unexpected Edge Function changes.
- DDL executed outside an approved change window.
- Privileged role modifications.
- Access to sensitive authentication tables.
- Changes that disable or reduce audit coverage.

Supabase’s unified Logs view supports filtering by time range, log type, level, status, method, path, event message, and—in applicable Auth and Postgres events—user.[7]

## Evidence and investigation

For every investigation, preserve:

```markdown
## Investigation record

- Case ID:
- Detection time:
- Event time range:
- Affected project:
- Affected organization:
- Actor or user:
- Event type:
- Source log:
- Event identifiers:
- Query or filter used:
- Raw evidence location:
- Initial assessment:
- Containment action:
- Root cause:
- Corrective action:
- Reviewer:
- Closure date:
```

Do not rely only on screenshots. Preserve structured event data, timestamps in UTC, the query or filter used, and the exact project or organization context.

## Ready-to-use checklist

```markdown
## Audit readiness checklist

- [ ] Auth Audit Logs are enabled and understood.
- [ ] Database storage for auth logs has a documented rationale.
- [ ] Platform Audit Logs are available for the current plan.
- [ ] Audit Log Drains are configured where required.
- [ ] PostgreSQL connection logging has been assessed.
- [ ] PGAudit scope is documented.
- [ ] Sensitive objects are monitored appropriately.
- [ ] Excessive global logging has been avoided.
- [ ] Retention periods are recorded.
- [ ] Log access is least-privilege.
- [ ] Security alerts have named owners.
- [ ] A review schedule exists.
- [ ] Incident evidence-preservation steps are documented.
- [ ] The configuration is reviewed after schema, auth, or organization changes.
```

The key guideline is to document **what is covered, where it is stored, who can access it, how long it is retained, and how it is reviewed**. Treat Auth Audit Logs, Platform Audit Logs, and database/PGAudit records as separate controls with separate owners and retention decisions.

การอ้างอิง:
[1] Log Actions Reference https://supabase.com/docs/guides/auth/audit-logs
[2] Platform Audit Logs | Supabase Docs https://supabase.com/docs/guides/security/platform-audit-logs
[3] PGAudit: Postgres Auditing | Supabase Docs https://supabase.com/docs/guides/database/extensions/pgaudit
[4] Postgres connection logging | Supabase Docs https://supabase.com/docs/guides/platform/postgres-connection-logging
[5] Customer Responsibilities https://supabase.com/docs/guides/security/soc-2-compliance
[6] Check usage for monthly active users (MAU) - Supabase https://supabase.com/docs/guides/troubleshooting/check-usage-for-monthly-active-users-mau-MwZaBs
[7] Logging | Supabase Docs https://supabase.com/docs/guides/observability/logs
[8] Understanding Postgres Logging Levels and How They Impact Your ... https://supabase.com/docs/guides/troubleshooting/understanding-postgresql-logging-levels-and-how-they-impact-your-project-KXiJRm
[9] Query and filter logs - Docs - Supabase https://supabase.com/docs/guides/observability/advanced-log-filtering
[10] How to Interpret and Explore the Postgres Logs https://supabase.com/docs/guides/troubleshooting/how-to-interpret-and-explore-the-postgres-logs-OuCIOj
[11] Logging | Supabase Docs https://supabase.com/docs/guides/monitoring-and-debugging/logs?queryGroups=product&product=postgres&queryGroups=source&source=edge_logs
[12] Superuser Settings https://supabase.com/docs/guides/database/custom-postgres-config
[13] Auth | Supabase Docs https://supabase.com/docs/guides/auth
[14] General configuration | Supabase Docs https://supabase.com/docs/guides/auth/general-configuration
[15] pgmq: Queues | Supabase Docs https://supabase.com/docs/guides/database/extensions/pgmq
