Title: GitHub API — Complete Reference & Implementation Guide
Kicker: REST + GraphQL — authentication, endpoints, SDKs, and enterprise best practices
Theme: dark
Genre: reference

# GitHub API — Complete Reference & Implementation Guide

The GitHub API lets you automate repositories, issues, pull requests, actions, and
organization administration. This guide covers the **REST v3** and **GraphQL v4**
APIs end to end: authentication, core endpoints with runnable `curl` examples,
Python SDK usage, and the reliability patterns you need in production.

| Item | Value |
| --- | --- |
| REST base URL | `https://api.github.com` |
| GraphQL endpoint | `https://api.github.com/graphql` |
| REST media type | `Accept: application/vnd.github+json` |
| REST API version header | `X-GitHub-Api-Version: 2022-11-28` |
| GraphQL Explorer | https://docs.github.com/en/graphql/overview/explorer |
| OpenAPI spec | https://github.com/github/rest-api-description |

---

## 1. Core Concepts

### REST vs GraphQL

**REST** is resource-oriented: one URL per resource (`/repos/{owner}/{repo}/issues`),
predictable verbs, and stable, well-documented response shapes. It is the right
default for CRUD automation, webhooks, and anything where you want the smallest
possible mental model.

**GraphQL** is a single endpoint where you ask for exactly the fields you want —
one round trip instead of N. It is the right choice when you're fetching nested
data (a PR plus its review threads, comments, and check runs) or building a
dashboard that would otherwise fan out dozens of REST calls.

| Dimension | REST v3 | GraphQL v4 |
| --- | --- | --- |
| Endpoint | Many URLs | One URL (`/graphql`) |
| Over/under-fetching | Common | Eliminated by field selection |
| Rate limit | 5,000 req/hour (authenticated) | 5,000 *points*/hour, cost per query |
| Best for | CRUD, webhooks, simple automation | Nested reads, dashboards, bulk queries |
| Pagination | `page` / `per_page` + `Link` header | `first` / `after` cursors |

### Versioning

REST requests should pin `X-GitHub-Api-Version`. Omitting it silently opts you
into the oldest supported version, which will eventually break. GraphQL has a
single evolving schema with deprecation warnings rather than dated versions.

### Rate limits

| Auth | REST limit | Notes |
| --- | --- | --- |
| Unauthenticated | 60 req/hour | Per IP |
| Personal access token (PAT) | 5,000 req/hour | Per user |
| GitHub App installation | 5,000 req/hour | Scales with repo count (up to 12,500+) |
| GraphQL (PAT or App) | 5,000 points/hour | Cost per query, minimum 1 point |

Check remaining budget without spending a request: `GET /rate_limit` is free.

```bash
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/rate_limit | jq '.resources.core'
```

---

## 2. Authentication

Never commit a token. Read it from an environment variable or a secret manager,
and grant the **narrowest scope** that does the job.

### 2.1 Personal Access Token (PAT)

Fine-grained PATs are preferred: they scope to specific repositories and
permissions (e.g. *Contents: Read*, *Issues: Read and write*).

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxx
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/user
```

Classic tokens use the same header. The older `Authorization: token <PAT>` form
still works but `Bearer` is the current convention.

### 2.2 GitHub App (recommended for automation)

Apps authenticate with a short-lived **JWT** signed by the app's private key,
then exchange it for an **installation token** scoped to the repos installed.

```python
import time, jwt, requests

APP_ID = 123456
KEY = open("private-key.pem").read()
INSTALLATION_ID = 98765432

# 1. Sign a JWT (10-minute lifetime max)
payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + 600,
           "iss": APP_ID}
jwt_token = jwt.encode(payload, KEY, algorithm="RS256")

# 2. Exchange for an installation token (1-hour lifetime)
resp = requests.post(
    f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens",
    headers={"Authorization": f"Bearer {jwt_token}",
             "Accept": "application/vnd.github+json"},
    timeout=30,
)
resp.raise_for_status()
token = resp.json()["token"]  # valid for 60 minutes
```

Cache the installation token and refresh it before expiry — do not mint one per
request.

### 2.3 Required scope reference

| Task | Fine-grained permission | Classic scope |
| --- | --- | --- |
| Read user profile | *(none)* | `read:user` |
| Read/write repository contents | Contents: Read and write | `repo` |
| Manage issues | Issues: Read and write | `repo` |
| Manage pull requests | Pull requests: Read and write | `repo` |
| Read/trigger Actions runs | Actions: Read and write | `workflow` |
| Edit workflow files | **Workflows: Write** | `workflow` |
| Read org members | Members: Read | `read:org` |

Editing `.github/workflows/*` requires the distinct **Workflows** permission.
Without it, pushes and the Contents API both return `403` with
"refusing to allow a GitHub App to create or update workflow … without
workflows permission".

---

## 3. REST API Reference

All examples assume:

```bash
export GITHUB_TOKEN=...
export API="-H \"Authorization: Bearer $GITHUB_TOKEN\""
OWNER=octocat
REPO=hello-world
```

### 3.1 Base URL and headers

```bash
curl -i \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "User-Agent: my-app" \
  https://api.github.com/user
```

Every response carries rate-limit and pagination metadata:

```text
x-ratelimit-limit: 5000
x-ratelimit-remaining: 4998
x-ratelimit-reset: 1726000000
link: <https://api.github.com/user/repos?page=2>; rel="next", ...; rel="last"
```

### 3.2 User profile

```bash
# Authenticated user
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" https://api.github.com/user

# Any user by login
curl -sS -H "Accept: application/vnd.github+json" \
  https://api.github.com/users/$OWNER
```

```json
{
  "login": "octocat",
  "id": 1,
  "type": "User",
  "public_repos": 8,
  "followers": 16000,
  "created_at": "2011-01-25T18:44:36Z"
}
```

### 3.3 Repositories

```bash
# List the authenticated user's repos (paginated)
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/user/repos?per_page=100&sort=updated"

# Get one repository
curl -sS -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$OWNER/$REPO

# Create a repository
curl -sS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/user/repos \
  -d '{"name":"new-repo","private":true,"auto_init":true}'
```

Key fields: `full_name`, `default_branch`, `private`, `visibility`,
`permissions` (`push` / `pull` / `admin`), `pushed_at`.

### 3.4 File contents

```bash
# Read a file (contents are base64-encoded)
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/contents/README.md

# Decode
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/contents/README.md \
  | jq -r '.content' | base64 -d
```

Create or update a file — you must supply the current blob `sha` when updating:

```bash
SHA=$(curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/contents/notes.txt \
  | jq -r '.sha // empty')

curl -sS -X PUT -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$OWNER/$REPO/contents/notes.txt \
  -d "$(jq -n --arg msg "docs: update notes" --arg c "$(printf 'hello' | base64)" \
        --arg sha "$SHA" '{message:$msg, content:$c, sha:$sha}')"
```

> **Large files:** the Contents API is limited to ~1 MB. Use the Git Data API
> (`/git/blobs` → `/git/trees` → `/git/commits`) for larger payloads.

### 3.5 Issues

```bash
# List open issues
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=50"

# Create an issue
curl -sS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{"title":"Bug: crash on startup","body":"Steps to reproduce…","labels":["bug"]}'

# Add a comment (issue comments share the number space with issues)
curl -sS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/comments \
  -d '{"body":"Confirmed on v1.2.3."}'
```

Note: the issues endpoint returns **pull requests too** (they share numbering);
filter with `jq '[.[] | select(.pull_request == null)]'`.

### 3.6 Pull requests

```bash
# List PRs
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"

# Create a PR
curl -sS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d '{"title":"feat: add caching","head":"feature/caching","base":"main",
       "body":"Adds a Redis cache layer.","draft":false}'

# Merge a PR (merge | squash | rebase)
curl -sS -X PUT -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/17/merge \
  -d '{"merge_method":"squash","commit_title":"feat: add caching (#17)"}'
```

```json
{
  "number": 17,
  "state": "open",
  "mergeable": true,
  "head": { "ref": "feature/caching", "sha": "a1b2c3d" },
  "base": { "ref": "main" },
  "draft": false
}
```

### 3.7 Workflows and Actions

```bash
# List workflows
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows

# Trigger a workflow_dispatch run
curl -sS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/deploy.yml/dispatches \
  -d '{"ref":"main","inputs":{"environment":"staging"}}'

# List runs for a workflow, newest first
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=10"

# Re-run a failed run
curl -sS -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/1234567890/rerun
```

A dispatched run returns `204 No Content`; poll `/actions/runs` to pick up the
new run id.

---

## 4. GraphQL API

Endpoint: `https://api.github.com/graphql` — POST only. Explore and validate
queries interactively in the
[GraphQL Explorer](https://docs.github.com/en/graphql/overview/explorer).

### 4.1 Query

```graphql
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    name
    stargazerCount
    defaultBranchRef { name }
    openIssues: issues(states: OPEN) { totalCount }
    pullRequests(states: OPEN, first: 5) {
      nodes { number title author { login } }
    }
  }
}
```

```bash
curl -sS -X POST https://api.github.com/graphql \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"query($o:String!,$n:String!){repository(owner:$o,name:$n){name stargazerCount}}",
       "variables":{"o":"octocat","n":"hello-world"}}'
```

### 4.2 Mutation

```graphql
mutation($input: CreateIssueInput!) {
  createIssue(input: $input) {
    issue { number url }
  }
}
```

```json
{ "input": { "repositoryId": "MDEwOlJlcG9zaXRvcnk...",
             "title": "GraphQL-created issue",
             "body": "Filed via the v4 API." } }
```

### 4.3 Efficient fetching patterns

**Query cost.** Every connection (`issues`, `pullRequests`, `commits`) is charged
by the number of nodes requested. Asking for `first: 100` on three nested
connections costs far more than three separate modest queries — request only the
fields you will use.

**Bulk aliasing.** Fetch many repositories in one round trip instead of looping:

```graphql
query {
  a: repository(owner: "octocat", name: "hello-world") { stargazerCount }
  b: repository(owner: "octocat", name: "Spoon-Knife") { stargazerCount }
}
```

**Cursor pagination.** GraphQL uses cursor-based paging, not offsets:

```graphql
issues(first: 50, after: $cursor) {
  pageInfo { hasNextPage endCursor }
  nodes { number title }
}
```

Pass `endCursor` back as `after` for the next page until `hasNextPage` is false.

---

## 5. SDKs and Tools

### 5.1 PyGitHub

```bash
pip install PyGithub
```

```python
from github import Github, Auth

auth = Auth.Token(os.environ["GITHUB_TOKEN"])
g = Github(auth=auth)

repo = g.get_repo("octocat/hello-world")
print(repo.stargazers_count, repo.default_branch)

# Create an issue
issue = repo.create_issue(title="Automated report", body="Generated nightly.")
print(issue.html_url)

# Open a pull request and squash-merge it
pr = repo.create_pull(title="chore: bump deps", head="bump", base="main",
                      body="Dependabot sweep.")
pr.merge(merge_method="squash")

# List open PRs, newest first
for pr in repo.get_pulls(state="open", sort="created")[:10]:
    print(pr.number, pr.title)
```

PyGitHub handles pagination transparently via `PaginatedList` — slice it, don't
page manually.

### 5.2 GitHub CLI (`gh`)

```bash
gh auth login
gh pr create --base main --head feature/caching --title "feat: caching" --body "…"
gh pr merge 17 --squash --delete-branch
gh run list --limit 10
gh api repos/octocat/hello-world/issues --jq '.[].title'
```

`gh api` is the escape hatch for anything the CLI doesn't wrap, and `--jq`
filters the JSON inline.

### 5.3 Octokit (JavaScript / TypeScript)

```bash
npm install @octokit/rest
```

```javascript
import { Octokit } from "@octokit/rest";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

await octokit.issues.create({
  owner: "octocat", repo: "hello-world",
  title: "Automated report", body: "Generated nightly.",
});

const { data } = await octokit.pulls.list({ owner: "octocat", repo: "hello-world",
                                            state: "open", per_page: 10 });
```

Octokit supports `@octokit/plugin-throttling` and `@octokit/plugin-retry` for
production resilience.

---

## 6. Best Practices

### 6.1 Rate-limit handling

Read the headers on every response and back off before you hit zero:

```python
import time, requests

def get(url, token):
    r = requests.get(url, headers={"Authorization": f"Bearer {token}",
                                   "Accept": "application/vnd.github+json"},
                     timeout=30)
    remaining = int(r.headers.get("x-ratelimit-remaining", 1))
    if remaining < 10:
        reset = int(r.headers["x-ratelimit-reset"])
        time.sleep(max(0, reset - time.time()) + 1)
    return r
```

On `403` or `429` with `x-ratelimit-remaining: 0`, sleep until
`x-ratelimit-reset` rather than retrying immediately. For secondary
(abuse) limits, honor `Retry-After` and add jitter.

### 6.2 Pagination

REST uses numbered pages plus a `Link` header; follow `rel="next"` rather than
constructing URLs yourself:

```python
def paginate(url, token):
    while url:
        r = get(url, token)
        yield from r.json()
        url = r.links.get("next", {}).get("url")
```

Prefer `per_page=100` to cut round trips. Prefer cursor pagination for
high-volume or frequently-changing collections, where offsets can skip or repeat
items.

### 6.3 Error handling

| Status | Meaning | Action |
| --- | --- | --- |
| `401` | Bad or expired credentials | Re-authenticate; for Apps, refresh the installation token |
| `403` | Forbidden / rate-limited / missing scope | Check `x-ratelimit-remaining`; inspect scope |
| `404` | Not found **or** no access | Verify the token can see the resource |
| `422` | Validation failed | Read `errors[]` in the body |
| `5xx` | GitHub-side failure | Exponential backoff with jitter, then alert |

```python
if r.status_code == 422:
    print(r.json()["errors"])  # field-level detail
```

### 6.4 Security

- Never log full tokens, and never commit them — use env vars or a secret store.
- Grant least privilege: prefer fine-grained PATs or GitHub App tokens over
  classic `repo`-wide scopes.
- Rotate tokens on a schedule and revoke unused ones.
- Verify webhook signatures (`X-Hub-Signature-256`) with the shared secret.
- Treat `404` on a private resource as a possible permission gap, not absence.

### 6.5 Conditional requests

Cache responses with `ETag` (or `Last-Modified`) and revalidate cheaply — a
`304 Not Modified` does **not** count against your rate limit:

```python
etag = None
headers = {"Accept": "application/vnd.github+json",
           "Authorization": f"Bearer {token}"}
if etag:
    headers["If-None-Match"] = etag
r = requests.get(url, headers=headers, timeout=30)
if r.status_code == 304:
    ...  # unchanged, use cached copy
else:
    etag = r.headers.get("etag")
```

Use `If-Modified-Since` when you stored a `Last-Modified` value instead.

### 6.6 Idempotency

REST has no idempotency-key header, so make writes safe by design:

- Check-then-write: GET the resource first and skip if the desired state holds.
- For file writes, always send the current `sha` so a stale update is rejected
  rather than clobbering a concurrent change.
- Use unique, deterministic titles/markers (a run id in the issue title) so a
  retried create can be detected and deduplicated.
- On timeout, re-read before retrying — a create may have succeeded even when the
  response was lost.

---

## 7. Resources

| Resource | Link |
| --- | --- |
| REST reference | https://docs.github.com/en/rest |
| GraphQL reference | https://docs.github.com/en/graphql |
| GraphQL Explorer | https://docs.github.com/en/graphql/overview/explorer |
| REST OpenAPI description | https://github.com/github/rest-api-description |
| Webhook events | https://docs.github.com/en/webhooks |
| Octokit (JS) | https://github.com/octokit/octokit.js |
| PyGitHub | https://github.com/PyGithub/PyGithub |
| GitHub CLI manual | https://cli.github.com/manual |
| Rate limits | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api |

> **Note on authentication errors.** Endpoints such as `/user`, `/user/repos`,
> and `/repos/{owner}/{repo}/...` return `404` or `403` when a token is missing,
> expired, or lacks scope. That is an authorization response, not API downtime —
> set up auth as shown in §2 and retry.
