---
title: "Supabase SSO Signing Guidelines"
description: "SAML 2.0 SSO with Supabase: core values, signing certificates, attribute mapping, and renewal."
tags:
  - knowledge/supabase
  - knowledge/security
  - knowledge/authentication
supabase_area: "Auth / SSO"
doc_kind: "guideline"
status: "active"
owner: "Platform Engineering"
last_reviewed: "2026-09-13"
review_frequency: "Annual"
source: "Supabase official documentation"
---

Supabase single signing Document Guidelines

## Supabase SSO signing-document guidelines

Assuming “single signing” means **Single Sign-On (SSO) signing documentation**, use this as an implementation and handoff guide for Supabase SAML 2.0.

Supabase Auth supports SAML 2.0 SSO with providers such as Google Workspace, Okta, Microsoft Entra, PingIdentity, and OneLogin. SAML SSO is disabled by default and is available on Pro plans and above.[1]

### 1. Record the core SAML values

Create a configuration record containing:

| Field | Value |
|---|---|
| Service Provider | Supabase Auth |
| Entity ID | `https://<project>.supabase.co/auth/v1/sso/saml/metadata` |
| Metadata URL | `https://<project>.supabase.co/auth/v1/sso/saml/metadata` |
| Download metadata | `https://<project>.supabase.co/auth/v1/sso/saml/metadata?download=true` |
| ACS URL | `https://<project>.supabase.co/auth/v1/sso/saml/acs` |
| SLO URL | `https://<project>.supabase.co/auth/v1/sso/slo` |
| NameID | `emailAddress` or `persistent` |
| Required user attribute | Email address |

Supabase’s SAML metadata contains the Service Provider information that must be supplied to the Identity Provider.[1]

### 2. Document signing certificates

Your document should identify:

- Certificate owner: the Identity Provider or Supabase Service Provider.
- Certificate purpose: signing SAML assertions or signing SAML requests.
- Certificate source: IdP metadata XML or metadata URL.
- Algorithm and key size, if exposed by the IdP.
- Issue date and expiration date.
- Renewal owner.
- Renewal process.
- Environments affected.
- Emergency contact.

Supabase verifies SAML assertions using the certificate included in the IdP metadata. Therefore, the certificate and metadata must be kept current.[1]

Do not place private keys, client secrets, Supabase secret keys, or full credentials in the document. Store them in a secrets manager and reference only the secret name or vault location.

### 3. Use metadata URLs where possible

Prefer an IdP metadata URL instead of manually copying certificate values. Supabase recommends metadata URLs when the provider supports them because they make certificate and metadata updates easier to maintain. Use an XML file when the provider only supplies a file or when the IdP is inaccessible from the public internet.[1]

Document the source like this:

```yaml
idp_metadata:
  type: url
  value: https://idp.example.com/saml/metadata
  owner: Identity and Access Management Team
  refresh_process: Review after certificate renewal
```

### 4. Define attribute mappings

Email is required because Supabase cannot create an SSO user without an email address. Other attributes should be mapped explicitly rather than assumed.[1]

Example:

```json
{
  "keys": {
    "email": {
      "name": "mail"
    },
    "first_name": {
      "name": "givenName"
    },
    "last_name": {
      "name": "sn"
    },
    "display_name": {
      "names": ["displayName", "cn"]
    },
    "groups": {
      "name": "groups",
      "array": true
    }
  }
}
```

Document each mapping:

| Supabase field | IdP attribute | Required |
|---|---|---:|
| Email | `mail` or `email` | Yes |
| First name | `givenName` | No |
| Last name | `sn` | No |
| Display name | `displayName` | No |
| Groups | `groups` | Only if used for authorization |

If an attribute can have multiple values, mark it as an array. Supabase otherwise uses only the first value.[1]

### 5. Separate environments

Use different SAML applications and ACS URLs for development, staging, and production. Never reuse production metadata or certificates casually in a lower environment.

Recommended names:

- `Supabase - Development`
- `Supabase - Staging`
- `Supabase - Production`

For multiple environments using the same company domain, Supabase documents an IdP-initiated pattern in which users select the correct app tile. This avoids ambiguous SP-initiated routing between organizations.[2]

Each environment record should include:

```yaml
environment: production
organization: acme-production
idp_application: Supabase - Production
acs_url: https://<production-project>.supabase.co/auth/v1/sso/saml/acs
auto_join: false
break_glass_account: stored-in-password-manager
```

### 6. Signing-key best practices

For Supabase JWT signing keys:

- Prefer asymmetric signing keys over the legacy shared JWT secret.
- Prefer ES256 where your runtime supports it.
- Use RS256 when broader compatibility is more important.
- Avoid HS256 for production unless there is a specific, documented reason.
- Rotate keys at least annually or according to your compliance policy.
- Never expose private signing keys in frontend code, source control, logs, or uploaded documents.
- Confirm that backend services do not depend directly on the legacy JWT secret before rotation.
- Keep a tested rollback procedure.

Supabase describes asymmetric signing keys as the recommended direction because they support local verification, safer rotation, and better separation from API keys.[3]

For SAML specifically, Supabase requires the IdP’s certificate for assertion verification, while self-hosted Supabase requires a Base64-encoded PKCS#1 RSA private key of at least 2048 bits for SAML signing; a 4096-bit key may be preferable for production deployments.[1][4]

### 7. Testing checklist

Before production rollout, test:

- SP-initiated login.
- IdP-initiated login.
- Correct redirect to the intended project.
- Valid and invalid email domains.
- New-user provisioning or auto-join behavior.
- Existing-user behavior.
- Attribute mappings.
- Group or role claims, if used.
- Expired or replaced certificates.
- Incorrect audience or ACS URL.
- User removal from the IdP.
- Break-glass non-SSO access.
- Session expiration and reauthentication.
- Multiple environments with the same email domain.

Supabase notes that SSO-created users are not automatically linked to existing password or social-login accounts. Applications should use the user UUID rather than assuming email is a unique identifier.[1]

### 8. Include an operational runbook

Your document should contain:

```markdown
## Certificate renewal

Owner: Identity and Access Management Team
Notice period: 30 days before expiration
Change window: Approved maintenance window
Required artifact: Updated IdP metadata XML or metadata URL
Validation: Test login with a non-production account
Rollback: Restore the previous metadata if still valid
Escalation: Security Operations / Supabase support

## Break-glass access

Account location: Enterprise password manager
Use condition: SSO outage or emergency administration
MFA: Required
Review frequency: Quarterly
Test procedure: Approved maintenance window only
```

Certificate expiration should be tracked with a calendar reminder well before expiry. Supabase specifically warns that expired certificates are a common cause of SSO failures and recommends scheduling a reminder before renewal.[5]

### 9. Recommended document structure

Use this final structure for the authoritative document:

```markdown
# Supabase SAML SSO Configuration

## Document control
- Owner
- Version
- Last reviewed
- Next review
- Approvers

## Scope
- Supabase organization
- Project
- Environment
- Identity Provider

## SAML endpoints
- Entity ID
- Metadata URL
- ACS URL
- SLO status
- NameID format

## Certificate inventory
- Certificate owner
- Thumbprint
- Expiration date
- Renewal owner
- Metadata source

## Attribute mappings
- Required attributes
- Optional attributes
- Group and role mappings

## Access model
- Allowed domains
- Auto-join policy
- Organization roles
- Break-glass access

## Security controls
- Key storage
- Rotation schedule
- Least-privilege permissions
- Audit logging
- Secrets handling

## Testing
- Test accounts
- Test cases
- Expected results
- Evidence location

## Operations
- Renewal procedure
- Incident procedure
- Rollback procedure
- Support contacts

## Change history
- Date
- Change
- Author
- Approval
```

This format is suitable for security review, onboarding an IdP administrator, and maintaining a production SSO configuration without exposing sensitive signing material.

การอ้างอิง:
[1] Single Sign-On with SAML 2.0 for Projects - Supabase Docs https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml
[2] Multiple SSO Providers | Supabase Docs https://supabase.com/docs/guides/platform/sso/multiple-providers
[3] JWT Signing Keys | Supabase Docs https://supabase.com/docs/guides/auth/signing-keys
[4] Configure SAML SSO | Supabase Docs https://supabase.com/docs/guides/self-hosting/self-hosted-saml-sso
[5] Set Up SSO with Google Workspace | Supabase Docs https://supabase.com/docs/guides/platform/sso/gsuite
[6] Enable SSO for Your Organization | Supabase Docs https://supabase.com/docs/guides/platform/sso
[7] Enterprise Single Sign-On | Supabase Docs https://supabase.com/docs/guides/auth/enterprise-sso
[8] Choosing the Right SSO Login Flow | Supabase Docs https://supabase.com/docs/guides/platform/sso/choosing-login-flow
[9] Step 12: Join Organization... https://supabase.com/docs/guides/platform/sso/azure
[10] supabase/apps/docs/content/guides/auth/enterprise-sso. ... https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/enterprise-sso.mdx
[11] SSO and SAML Endpoints | supabase/auth | DeepWiki https://deepwiki.com/supabase/auth/3.5-sso-and-saml-endpoints
[12] SAML and SSO | supabase/auth | DeepWiki https://deepwiki.com/supabase/auth/4.4-saml-and-sso
[13] What is SAML? A practical guide to the authentication protocol https://dev.to/supabase/what-is-saml-a-practical-guide-to-the-authentication-protocol-232j
[14] Enterprise SSO and SAML for Self-Hosted Supabase: Complete ... https://www.supascale.app/blog/enterprise-sso-and-saml-for-selfhosted-supabase-complete-set
[15] Single Sign-On (SSO) | supabase-community/supabase-auth-rs | DeepWiki https://deepwiki.com/supabase-community/supabase-auth-rs/4.7-single-sign-on-(sso)
