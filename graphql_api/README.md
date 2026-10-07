# GraphQL API (FastAPI + Strawberry)

Production-shaped FastAPI + Strawberry GraphQL API with async SQLAlchemy, JWT
auth, cursor pagination, subscriptions scaffold, health check, and Docker.

## Run (dev)
```bash
pip install -r requirements.txt
cp .env.example .env          # set SECRET_KEY
uvicorn app.main:app --reload
# Playground → http://localhost:8000/graphql  |  Health → /health
```

## Tests
```bash
pip install pytest pytest-asyncio
pytest tests/ -q        # 7 passed
```

## Layout
```
app/config.py      settings (SECRET_KEY from env)
app/auth.py        JWT create/decode (+ AuthError)
app/database.py    async SQLAlchemy engine/session
app/models.py      User ORM model
app/schema.py      Strawberry Query/Mutation/Subscription
app/main.py        FastAPI + GraphQLRouter(/graphql) + health
tests/             auth + schema execution tests
```

## Notes / gaps vs "production-ready"
- Resolvers use in-memory/demo data; wire to the ORM/CRUD layer + Redis cache
  for real use.
- `login` is a demo stub (any creds -> token); add passlib/bcrypt + real lookup.
- Subscription `user_created` is a template (Redis pub/sub not wired).
- Timezone-aware datetimes (UTC) used throughout.

## Database migrations (Alembic)

```bash
# Apply migrations (creates schema from alembic/versions)
cd graphql_api
alembic upgrade head

# After changing app/models.py, generate a new migration
alembic revision --autogenerate -m "describe change"

# Rollback one step
alembic downgrade -1
```

## DB-backed resolvers
- `login` verifies against the `users` table (bcrypt password hash).
- `me` / `users` query the DB through async SQLAlchemy sessions.
- `create_user` inserts a real row (admin-gated).
- Tests run against an in-memory SQLite DB (`tests/test_schema_db.py`).

- # GraphQL API — Complete Overview & Implementation Guide

GraphQL is an open-source query language and runtime for APIs, developed internally by Meta (Facebook) in 2012 and publicly released in 2015. It provides a flexible, efficient alternative to REST by letting clients request **exactly the data they need** — no more, no less.

---

## Core Concepts

| Concept | Description |
|---|---|
| **Schema** | Single source of truth defining all data types, relationships, and available operations; written in SDL (Schema Definition Language) |
| **Query** | Read‑only operation to fetch data |
| **Mutation** | Write operation to create/update/delete data |
| **Subscription** | Real‑time continuous data updates via WebSocket |
| **Resolver** | Backend function that maps each field in your schema to actual data |
| **Root Fields** | Entry points for queries/mutations/subscriptions |

---

## Basic Structure Example

### 1. Schema Definition (`schema.graphql`)
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
  published: Boolean!
}

type Query {
  # Get single user
  user(id: ID!): User
  # List all users
  users: [User!]!
  # Get filtered posts
  posts(published: Boolean): [Post!]!
}

type Mutation {
  createUser(name: String!, email: String!): User!
  createPost(title: String!, content: String, authorId: ID!): Post!
  updatePost(id: ID!, published: Boolean!): Post
}

type Subscription {
  postCreated: Post!
}
```

### 2. Example Query Request
```graphql
query GetUserWithPosts($userId: ID!) {
  user(id: $userId) {
    id
    name
    posts {
      title
      published
    }
  }
}
```
**Variables:**
```json
{ "userId": "123" }
```

### 3. Response
```json
{
  "data": {
    "user": {
      "id": "123",
      "name": "Alex Dev",
      "posts": [
        { "title": "GraphQL Basics", "published": true },
        { "title": "Advanced Resolvers", "published": false }
      ]
    }
  }
}
```

---

## GraphQL vs REST — Key Differences

| Feature | GraphQL | REST |
|---|---|---|
| **Data Fetching** | Single endpoint (`/graphql`), client specifies shape | Multiple endpoints, fixed response shapes |
| **Over‑fetching** | Eliminated — response matches request exactly | Common — returns full resource representation |
| **Under‑fetching** | Single request gets nested data | May require multiple chained requests |
| **Versioning** | Rarely needed — evolve schema backward‑compatible | New version endpoint typically required |
| **Type Safety** | Built‑in via schema + type systems | Depends on docs/validation (OpenAPI etc.) |
| **Caching** | Requires custom handling (Apollo Client, Relay) | Built‑in HTTP caching |

---

## Popular Server Implementations

| Language/Stack | Libraries |
|---|---|
| **Node.js** | Apollo Server, GraphQL Yoga, Express GraphQL, Nexus |
| **Python** | Strawberry, Graphene, Ariadne |
| **Java/Kotlin** | Spring GraphQL, DGS Framework |
| **Go** | gqlgen, graphql‑go |
| **Ruby** | GraphQL‑Ruby |
| **C#/.NET** | Hot Chocolate, GraphQL.NET |

### Minimal Node.js Example (Apollo Server)
```javascript
import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';

// Mock database
const users = [
  { id: '1', name: 'Alex', email: 'alex@example.com' }
];

// TypeDefs = Schema
const typeDefs = `#graphql
  type User { id: ID!, name: String!, email: String! }
  type Query { user(id: ID!): User }
`;

// Resolvers
const resolvers = {
  Query: {
    user: (parent, { id }) => users.find(u => u.id === id)
  }
};

const server = new ApolloServer({ typeDefs, resolvers });
const { url } = await startStandaloneServer(server, { listen: { port: 4000 } });
console.log(`GraphQL ready at ${url}`);
```

---

## Popular Client Libraries
- **Apollo Client** — React, Vue, Angular, Svelte; caching, dev tools, subscriptions
- **Relay** — Facebook’s official high‑performance client
- **urql** — Lightweight, flexible, minimal bundle
- **GraphQL Request** — Simple fetch‑based wrapper

---

## Best Practices
1. **Use Variables** — Never interpolate query strings; prevents injection and improves reuse
2. **Pagination** — Prefer cursor‑based (`first`, `after`) over offset for large datasets
3. **Error Handling** — Return partial data + `errors` array; use `null` for missing fields
4. **Performance** — Implement **N+1 query protection** (DataLoader); add depth/complexity limits
5. **Security** — Authentication context in resolvers; rate‑limiting; disable introspection in production
6. **Documentation** — Schemas are self‑documenting; use tools like **GraphiQL** or **Apollo Sandbox**

---

## Common Use Cases
- Mobile apps with variable data needs
- Dashboards & analytics (many related fields in one call)
- Microservices — federated schema stitching
- Real‑time features (chat, live updates) via Subscriptions

---

I can turn this into a runnable starter project with schema, resolvers, and client example you can clone and test immediately — tap **Fast** and select **Pro** to get it.

Would you like me to focus on a specific stack (Node.js/TypeScript, Python, etc.) or integrate this with your existing ZyntroAI/Obsidian workflow?
