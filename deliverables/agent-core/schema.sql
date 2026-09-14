-- Agent Core — task store schema.
-- Apply once per Supabase project (SQL editor or a migration).

create table if not exists public.agent_tasks (
    id            uuid primary key default gen_random_uuid(),
    user_id       uuid references auth.users (id) not null,
    agent_task_id text unique not null,
    prompt        text not null,
    status        text not null default 'pending',
    result        jsonb,
    error         jsonb,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

-- Multi-tenant isolation. Without this, one user can read another's tasks.
alter table public.agent_tasks enable row level security;

drop policy if exists "Users own agent tasks" on public.agent_tasks;
create policy "Users own agent tasks"
    on public.agent_tasks
    for all
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

create index if not exists agent_tasks_user_created_idx
    on public.agent_tasks (user_id, created_at desc);
