Yep — here’s a clean text version of your message:

---

Yep, here’s a minimal `gateway.config.ts` for your Knowledge team bot with 2 subgraphs:

**Setup idea:**
1. **docs-subgraph**: Handles Notion/Confluence search  
2. **tickets-subgraph**: Handles `/ask` → create ticket + FAQ logic

```ts
// gateway.config.ts
import { defineConfig } from '@graphql-hive/gateway';

export const config = defineConfig({
  supergraph: {
    // Pull schemas from GraphQL Hive registry
    // Or point directly to your subgraphs
    products: [
      {
        name: 'docs',
        url: process.env.DOCS_SUBGRAPH_URL, // http://localhost:4001
      },
      {
        name: 'tickets',
        url: process.env.TICKETS_SUBGRAPH_URL, // http://localhost:4002
      }
    ]
  },
  
  plugins: [
    // Free in Hive Gateway v2 - Apollo charges for this
    {
      usage: {
        clientName: 'slack-knowledge-bot',
        enabled: true
      }
    },
    
    // Auth for your Slack bot tokens
    {
      auth: {
        jwt: {
          jwksUri: process.env.JWKS_URL,
          requiredScopes: ['knowledge:read']
        }
      }
    },
    
    // Rate limit so /ask spam doesn't kill Notion API
    {
      rateLimit: {
        window: '1m',
        max: 60,
        key: 'user.id'
      }
    },
    
    // Cache repeated /ask questions
    {
      cache: {
        ttl: 300 // 5 min
      }
    },
    
    // OpenTelemetry - full trace spans
    {
      opentelemetry: {
        endpoint: process.env.OTEL_ENDPOINT
      }
    }
  ],
  
  // Persisted docs for common queries
  persistedDocuments: {
    enabled: true
  }
});
```

**How Slack Bolt ties in:**
Your `app.js` slash command becomes just 1 resolver in `tickets-subgraph`:

```js
app.command('/ask', async ({ command, ack, respond }) => {
  await ack();
  // This calls the 'tickets' subgraph via Gateway
  const res = await gatewayClient.query(CREATE_TICKET_MUTATION, {
    question: command.text,
    userId: command.user_id
  });
  await respond(res.data.createTicket.answer);
});
```

**To run it:**

```bash
npm i -g @graphql-hive/gateway
hive-gateway --config gateway.config.ts --opentelemetry
```

**Why this fits Knowledge teams:**
1. **Split ownership**: Docs team owns `docs-subgraph`, Support team owns `tickets-subgraph`  
2. **See what users ask**: Hive usage tab shows top `/ask` queries → build FAQ from real data  
3. **No vendor lock**: MIT license + works with Slack CLI deploy

Want me to also drop the code for the `docs-subgraph` Notion search resolver so Copilot can fill it?
