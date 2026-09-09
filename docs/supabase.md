
# 📋 Supabase Local Development — Quick Summary

## Prerequisites

- **Container runtime** (Docker-compatible): Docker Desktop (preferred), Rancher Desktop, Podman, or OrbStack (macOS)

### Quickstart Commands

| Step | npm | Homebrew |
| --- | --- | --- |
| Install CLI | `npm install supabase --save-dev` | `brew install supabase` |
| Initialize project | `npx supabase init` | `supabase init` |
| Start local stack | `npx supabase start` | `supabase start` |
| Access dashboard | **[def]** | same |

### 🔒 Security Note

On untrusted networks, bind to localhost only:

```bash
docker network create -o 'com.docker.network.bridge.host_binding_ipv4=127.0.0.1' local-network
npx supabase start --network-id local-network
```

*Never expose your local stack publicly.*

### Benefits of Local Development

- **Faster**: Instant feedback, no remote deployment waits
- **Offline**: Works without internet
- **Cost-free**: Doesn't consume project quotas
- **Private**: Sensitive data stays local
- **Safe**: Experiment without affecting production

### CLI Capabilities

- Manage local dev environments
- Generate TypeScript types from DB schema
- Handle database migrations
- Manage environment variables & secrets
- Deploy to Supabase platform
- Essential for CI/CD pipelines

### Related Guides Available

- CLI getting started & workflows
- Database migrations & declarative schemas
- Seeding your database
- Managing config & restoring backups
- Customizing email templates
- Testing (pgTAP, RLS policies)

I'll cover all three for you. Let me first fetch the detailed content for the specific sections, then compile everything together.Here's the complete coverage of all three topics you requested:

---

#### 1. 🤖 Antigravity + Supabase: Automation Use Cases

The Antigravity agent can orchestrate the entire Supabase local development lifecycle. Here's how it maps to specific workflows:

## 🗄️ Automated Database Migrations

**Antigravity Prompt**:
> *"Look at my existing Supabase project schema. I need to add a `products` table with columns: id, name, description, price, category_id, created_at. Category references a `categories` table. Generate the migration files, apply them locally, and create seed data with 5 categories and 20 products."*

**What Antigravity does autonomously**:

1. **Plans** — Creates `implementation_plan.md` analyzing existing schema, identifying relationships
2. **Generates migrations** — Runs `supabase migration new create_categories_table` and `supabase migration new create_products_table`, writes the SQL with proper constraints and foreign keys
3. **Creates seed data** — Populates `supabase/seed.sql` with realistic sample data
4. **Applies & verifies** — Runs `supabase db reset`, then uses the browser subagent to visit [def], navigates to Table Editor, takes screenshots confirming tables exist with data
5. **Documents** — Generates `walkthrough.md` with the ER diagram, migration file list, and verification screenshots

**Time saved**: Manual migration writing + testing (~2 hours) → Agent completes in ~10 minutes with human review gates.

## 📝 TypeScript Type Generation

**Antigravity Prompt**:
> *"Generate TypeScript types from my local Supabase database schema and integrate them into my Next.js project. Create a typed Supabase client utility and update all existing API calls to use the generated types."*

**Workflow**:

1. Runs `supabase gen types typescript --local > types/database.ts`
2. Creates `utils/supabase.ts` with a properly typed client:

   ```typescript
   import { createClient } from '@supabase/supabase-js'
   import { Database } from '@/types/database'
   
   export const supabase = createClient<Database>(url, key)
   ```

3. Scans the project for untyped Supabase calls and refactors them
4. Runs TypeScript compiler (`npx tsc --noEmit`) to verify no type errors
5. Reports: *"Updated 17 files, 0 type errors, 3 files need manual review"*

## 🧪 Automated Test Generation & Execution

**Antigravity Prompt**:
> *"My todos table has RLS enabled with a policy 'Users can only access their own todos.' Generate comprehensive pgTAP tests covering: SELECT visibility, INSERT permissions, UPDATE restrictions, DELETE restrictions, and anonymous user access. Run the tests and fix any failing policies."*

**Workflow**:

1. **Analyzes** existing schema and policies via `supabase db dump` or direct file reading
2. **Generates test file** at `supabase/tests/todos_rls.test.sql` with:
   - Test data setup (multiple users, todos owned by different users)
   - Tests for each CRUD operation under different roles
   - Negative test cases (what users *shouldn't* be able to do)
3. **Runs tests** via `supabase test db`
4. **If tests fail**: Agent diagnoses the issue, proposes a policy fix, updates the migration, re-runs tests
5. **Creates walkthrough** with test results, policy analysis, and any fixes applied

## 🔄 CI/CD Pipeline Automation

**Antigravity Prompt**:
> *"Set up GitHub Actions for my Supabase project. On every PR: start Supabase locally, run all migrations, execute pgTAP tests, and generate a test coverage report. If tests fail, post a comment on the PR with the failure details."*

**Workflow**:

1. Creates `.github/workflows/db-tests.yml` using `supabase/setup-cli@v1`
2. Configures the workflow to: checkout → setup CLI → `supabase start` → `supabase test db`
3. Adds failure handling that extracts test output and posts PR comments
4. Optionally adds a separate workflow for deploying migrations on merge to main
5. Tests the workflow locally using `act` or validates the YAML syntax

## 🔐 Security & RLS Policy Audit

**Antigravity Prompt**:
> *"Audit my Supabase project for security issues. Check all RLS policies for gaps, verify that no tables are missing RLS, check for hardcoded secrets in config files, and ensure auth providers are properly configured. Generate a security report with severity ratings and proposed fixes."*

**Workflow**:

1. Scans all tables for `alter table ... enable row level security`
2. Analyzes each policy for common vulnerabilities (missing `using` clauses, overly permissive conditions)
3. Checks `supabase/config.toml` and `.env` files for exposed secrets
4. Reviews auth provider configurations
5. Generates `security-audit.md` with findings categorized by severity (Critical/High/Medium/Low)
6. For each issue, provides a specific SQL or config fix

## 🚀 Deployment Automation

**Antigravity Prompt**:
> *"Link my local project to the production Supabase instance, pull any remote schema changes, verify migrations apply cleanly, then deploy to production. Create a rollback plan and notify the team via Slack."*

**Workflow**:

1. Runs `supabase link --project-ref <project-id>`
2. Executes `supabase db pull` to capture any remote changes
3. Runs `supabase db reset` locally to verify consistency
4. Executes `supabase db push` for deployment
5. Deploys edge functions via `supabase functions deploy`
6. Creates `deployment-report.md` with: migration list, before/after schema diff, verification queries, and rollback SQL scripts

---

## 2. 📚 Detailed Section Summaries

## 🗄️ Database Migrations

### Core Concepts

Migrations are version-controlled SQL files that track schema changes over time. Each migration is a timestamped file in `supabase/migrations/`.

### Two Workflows

**Workflow A: Write SQL directly** (for SQL-savvy developers)

```bash
# 1. Create migration file
supabase migration new create_employees_table

# 2. Edit the generated file: supabase/migrations/<timestamp>_create_employees_table.sql
create table employees (
  id bigint primary key generated always as identity,
  name text,
  email text,
  created_at timestamptz default now()
);

# 3. Apply migration
supabase db reset
```

**Workflow B: Use Dashboard + Diff** (for visual developers)

1. Make changes in the local Studio Dashboard ([def])
2. Run `supabase db diff --schema public` to see the SQL
3. Copy the output into a new migration file
4. Run `supabase db reset`

### Seeding Data

Create `supabase/seed.sql` — automatically runs on `supabase db reset`:

```sql
insert into public.employees (name) values
  ('Erlich Bachman'), ('Richard Hendricks'), ('Monica Hall');
```

### Deployment

```bash
supabase login
supabase link --project-ref <project-id>
supabase db pull   # Only if remote has changes not in local migrations
supabase db reset  # Verify locally
supabase db push   # Deploy to production
```

### Advanced: Syncing Auth & Storage Schemas

```bash
supabase db pull --schema auth     # Pull auth triggers/policies
supabase db pull --schema storage  # Pull storage RLS policies
```

### Storage Buckets via Config

Define buckets in `supabase/config.toml`:

```toml
[storage.buckets.images]
public = false
file_size_limit = "50MiB"
allowed_mime_types = ["image/png", "image/jpeg"]
objects_path = "./images"
```

Then seed: `supabase seed buckets`

---

## 🧪 Testing Overview

### Two Testing Approaches

#### Approach 1: Database Unit Testing with pgTAP

Tests run directly in Postgres using transactions for isolation.

**Setup**:

```bash
supabase test new todos_rls.test
```

**Test structure** (`supabase/tests/todos_rls.test.sql`):

```sql
begin;
create extension if not exists pgtap with schema extensions;
select plan(4);  -- Declare number of tests

-- Setup test data
insert into auth.users (id, email) values
  ('123e4567-e89b-12d3-a456-426614174000', 'user1@test.com'),
  ('987fcdeb-51a2-43d7-9012-345678901234', 'user2@test.com');

insert into public.todos (task, user_id) values
  ('User 1 Task 1', '123e4567-e89b-12d3-a456-426614174000'),
  ('User 1 Task 2', '123e4567-e89b-12d3-a456-426614174000'),
  ('User 2 Task 1', '987fcdeb-51a2-43d7-9012-345678901234');

-- Test as User 1
set local role authenticated;
set local request.jwt.claim.sub = '123e4567-e89b-12d3-a456-426614174000';

select results_eq(
  'select count(*) from todos',
  ARRAY[2::bigint],
  'User 1 should only see their 2 todos'
);

select lives_ok(
  $$insert into todos (task, user_id) values ('New Task', '123e4567-e89b-12d3-a456-426614174000'::uuid)$$,
  'User 1 can create their own todo'
);

-- Test as User 2
set local request.jwt.claim.sub = '987fcdeb-51a2-43d7-9012-345678901234';

select results_eq(
  'select count(*) from todos',
  ARRAY[1::bigint],
  'User 2 should only see their 1 todo'
);

select results_ne(
  $$ update todos set task = 'Hacked!' where user_id = '123e4567-e89b-12d3-a456-426614174000'::uuid returning 1 $$,
  $$ values(1) $$,
  'User 2 cannot modify User 1 todos'
);

select * from finish();
rollback;
```

**Run tests**:

```bash
supabase test db
```

#### Approach 2: Application-Level Testing

Tests through your app code (TypeScript example with Vitest). No transaction isolation — use unique IDs per test suite.

**Key strategies**:

- Generate unique user IDs per test suite (`crypto.randomUUID()`)
- Use admin client (`service_role` key) for test data setup
- Sign in as different users to test RLS from the client perspective
- Clean up in `afterAll` hooks if needed

### CI/CD Integration (GitHub Actions)

```yaml
name: Database Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: supabase/setup-cli@v1
      - run: supabase start
      - run: supabase test db
```

### Best Practices

1. **Test all CRUD operations** for RLS policies
2. **Test negative cases** — what users *shouldn't* be able to do
3. **Test with multiple roles**: anonymous, authenticated, different users
4. **Use `begin`/`rollback`** for pgTAP test isolation
5. **Run on every PR** — catch regressions early

---

## ⚙️ CLI Configuration (`supabase/config.toml`)

Generated by `supabase init`. Changes require `supabase stop` + `supabase start`.

### Key Config Sections

| Section | Key Settings | Default | Purpose |
| --- | --- | --- | --- |
| **General** | `project_id` | Working dir name | Distinguish projects on same host |
| **Auth** | `auth.enabled` | `true` | Enable GoTrue auth service |
| | `auth.site_url` | `"http://localhost:3000"` | Base URL for redirects/emails |
| | `auth.jwt_expiry` | `3600` (1hr) | Token validity in seconds |
| | `auth.enable_signup` | `true` | Allow new user signups |
| | `auth.rate_limit.*` | Various | Rate limits for emails, sign-ins, tokens |
| **DB** | `db.pooler.max_client_conn` | `100` | Max PgBouncer connections |
| | `db.seed.enabled` | `true` | Run seeds on start/reset |
| | `db.seed.sql_paths` | `["./seed.sql"]` | Seed file locations |
| | `db.settings.*` | Various | Postgres tuning params |
| **Studio** | `studio.enabled` | `true` | Enable local dashboard |
| | `studio.port` | `54323` | Dashboard port |
| | `studio.openai_api_key` | `env(OPENAI_API_KEY)` | AI features in Studio |
| **Realtime** | `realtime.enabled` | `true` | Enable Realtime service |
| **Storage** | `storage.enabled` | `true` | Enable Storage service |
| | `storage.file_size_limit` | `"50MiB"` | Max upload size |
| **Analytics** | `analytics.enabled` | `false` | Enable Logflare |
| **Inbucket** | `inbucket.enabled` | `true` | Local email testing server |
| | `inbucket.port` | `54324` | Email web UI port |
| **Experimental** | `experimental.webhooks.enabled` | `false` | Auto-enable webhooks |
| | `experimental.orioledb_version` | `null` | OrioleDB storage engine |
| **Remotes** | `remotes.<branch>.project_id` | Required | Branch-specific deploy targets |

### Auth Provider Example

```toml
[auth.external.github]
enabled = true
client_id = "env(SUPABASE_AUTH_GITHUB_CLIENT_ID)"
secret = "env(SUPABASE_AUTH_GITHUB_SECRET)"
redirect_uri = "http://localhost:54321/auth/v1/callback"
```

Store secrets in `.env` (never commit to git).

### Branch-Specific Config

```toml
[remotes.staging]
project_id = "your-staging-project-ref"

[remotes.staging.db.seed]
sql_paths = ["./seeds/staging.sql"]
```

---

## 3. 🚀 Step-by-Step: Local Supabase Project Setup

### Prerequisites

1. **Install a container runtime**: Docker Desktop (recommended), Rancher Desktop, Podman, or OrbStack (macOS)
2. **Node.js** (if using npm/pnpm/yarn install method)

---

### Step 1: Install the Supabase CLI

Choose **one** method and use it consistently:

**Option A: npm (project-local)**

```bash
npm install supabase --save-dev
# Run with: npx supabase <command>
```

**Option B: Homebrew (global, macOS/Linux)**

```bash
brew install supabase
# Run with: supabase <command>
```

**Option C: pnpm**

```bash
pnpm add supabase --save-dev
# Run with: pnpm supabase <command>
```

---

### Step 2: Initialize Your Project

```bash
# In your project repository
npx supabase init
```

This creates:

your-project/
└── supabase/
    ├── config.toml       # Project configuration
    ├── migrations/       # Schema migration files (empty)
    └── seed.sql          # Seed data (empty)

---

### Step 3: Start the Local Supabase Stack

```bash
npx supabase start
```

This pulls Docker images and starts all services. First run takes a few minutes.

**Output includes**:

Started Supabase local development setup.

         API URL: http://localhost:54321
     GraphQL URL: http://localhost:54321/graphql/v1
          DB URL: postgresql://postgres:postgres@localhost:54322/postgres
      Studio URL: http://localhost:54323    <-- Your dashboard
    Inbucket URL: http://localhost:54324    <-- Email testing
      JWT secret: super-secret-jwt-token-with-at-least-32-characters-long
        anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

```

---

### Step 4: Access the Local Dashboard

Open **[def]** in your browser. This is your local Supabase Studio — identical to the cloud dashboard.

> 🔒 **Security note**: On untrusted networks, bind to localhost only:
>
> ```bash
> docker network create -o 'com.docker.network.bridge.host_binding_ipv4=127.0.0.1' local-network
> npx supabase start --network-id local-network
> ```
>
> *Never expose your local stack publicly.*

---

### Step 5: Create Your First Migration

**Method A: Write SQL directly** (recommended for version control)

```bash
npx supabase migration new create_profiles_table
```

Edit `supabase/migrations/<timestamp>_create_profiles_table.sql`:

```sql
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique,
  avatar_url text,
  updated_at timestamptz default now()
);

alter table profiles enable row level security;

create policy "Users can view their own profile"
  on profiles for select
  using (auth.uid() = id);

create policy "Users can update their own profile"
  on profiles for update
  using (auth.uid() = id);
```

Apply the migration:

```bash
npx supabase db reset
```

**Method B: Use Dashboard + Diff**

1. Go to [def] → Table Editor → Create table
2. Run `npx supabase db diff --schema public` to see the SQL
3. Copy into a migration file, then `npx supabase db reset`

---

### Step 6: Add Seed Data

Edit `supabase/seed.sql`:

```sql
-- Seed data runs automatically on `supabase db reset`
insert into profiles (id, username) values
  ('123e4567-e89b-12d3-a456-426614174000', 'testuser');
```

---

### Step 7: Generate TypeScript Types

```bash
npx supabase gen types typescript --local > types/database.ts
```

Use in your app:

```typescript
import { createClient } from '@supabase/supabase-js'
import { Database } from './types/database'

const supabase = createClient<Database>(
  'http://localhost:54321',
  'your-anon-key'
)
```

---

### Step 8: Write & Run Tests

```bash
# Create a test file
npx supabase test new profiles_rls.test
```

Write your pgTAP tests in `supabase/tests/profiles_rls.test.sql`, then:

```bash
npx supabase test db
```

---

### Step 9: Link & Deploy to Production

```bash
# 1. Authenticate
npx supabase login

# 2. Link to your cloud project (get project-ref from dashboard URL)
npx supabase link --project-ref abcdefghijklmnop

# 3. If cloud project has existing schema changes, pull them first
npx supabase db pull
npx supabase db reset  # Verify locally

# 4. Deploy migrations
npx supabase db push

# 5. Deploy edge functions (if any)
npx supabase functions deploy <function-name>
```

---

### Step 10: Daily Development Workflow

```bash
# Start the stack (resumes from previous state)
npx supabase start

# Make changes → create migration → apply
npx supabase migration new add_column_to_profiles
# Edit the SQL file...
npx supabase db reset

# Run tests
npx supabase test db

# When done
npx supabase stop
```

---

### Useful Commands Cheat Sheet

| Command | Purpose |
| --- | --- |
| `supabase init` | Initialize project structure |
| `supabase start` | Start local stack |
| `supabase stop` | Stop local stack |
| `supabase status` | Show service URLs and keys |
| `supabase db reset` | Reset DB + apply migrations + seed |
| `supabase migration new <name>` | Create new migration file |
| `supabase db diff` | Show schema changes as SQL |
| `supabase db pull` | Pull remote schema as migration |
| `supabase db push` | Deploy migrations to linked project |
| `supabase test new <name>` | Create pgTAP test file |
| `supabase test db` | Run all database tests |
| `supabase gen types` | Generate TypeScript types |
| `supabase login` | Authenticate CLI |
| `supabase link` | Link local project to cloud |

---

Would you like me to dive deeper into any specific area — for example, a concrete Antigravity prompt template for Supabase migrations, or more advanced RLS testing patterns?

[def]: http://localhost:54323
