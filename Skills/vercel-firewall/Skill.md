---
title: Vercel Firewall
product: vercel
url: /docs/vercel-firewall
canonical_url: "https://vercel.com/docs/vercel-firewall"
last_updated: 2026-08-11
type: conceptual
prerequisites:
  []
related:
  - /docs/vercel-firewall/ddos-mitigation
  - /docs/vercel-firewall/firewall-concepts
  - /docs/vercel-firewall/vercel-waf/ip-blocking
  - /docs/vercel-firewall/vercel-waf/custom-rules
  - /docs/vercel-firewall/vercel-waf/managed-rulesets
summary: Learn how Vercel Firewall helps protect your applications and websites from malicious attacks and unauthorized access.
install_vercel_plugin: npx plugins add vercel/vercel-plugin
---

# Vercel Firewall

The Vercel Firewall is a robust, multi-layered security system designed to protect your applications from a wide range of threats. Every incoming request goes through the following firewall layers:

<!-- docsgraph:related -->
## Related pages

> **For AI agents:** Follow these links to understand how this page connects to the rest of the Vercel ecosystem. For the full cross-link map (inbound, outbound, prerequisites, and semantic neighbors), see the .graph.md link below.

- [Bot Protection is now generally available](https://vercel.com/changelog/bot-protection-is-now-generally-available?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related)
- [Bot Protection is now in public beta](https://vercel.com/changelog/bot-protection-is-now-in-public-beta?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related)
- [Create custom WAF rules directly from the Vercel Firewall tab](https://vercel.com/changelog/create-custom-waf-rules-directly-from-the-vercel-firewall-tab?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related)
- [Create Vercel Firewall rules with natural language](https://vercel.com/changelog/create-vercel-waf-custom-rules-using-natural-language?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related)
- [Improved analytics experience now available on the Vercel Firewall](https://vercel.com/changelog/improved-analytics-experience-now-available-on-the-vercel-firewall?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related)
- [Application authentication on Vercel](https://vercel.com/kb/guide/application-authentication-on-vercel?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related) — Secure application authentication on Vercel across layers: proxy checks, the Data Access Layer, PPR-safe rendering, and
- [How to prepare your storefront for Black Friday traffic](https://vercel.com/kb/guide/black-friday-preparation?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related) — A practical checklist for keeping your storefront fast and your checkout path healthy through Black Friday and Cyber Mon
- [Building an AI chat app with RAG and source citations on Vercel](https://vercel.com/kb/guide/building-ai-chat-app-with-rag-and-citations-on-vercel?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related) — A production stack for AI chat with retrieval, reranking, source citations, and background ingestion on Vercel using Nex
- [Debug routing on Vercel](https://vercel.com/kb/guide/debug-routing-on-vercel?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related) — Learn how to debug how Vercel decides where to route your request
- [How to build and maintain HIPAA-compliant applications on Vercel](https://vercel.com/kb/guide/hipaa-compliance-guide-vercel?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related) — Deploy HIPAA-compliant healthcare apps on Vercel with built-in security, BAAs, and scalable serverless infrastructure.
- [How we run Vercel's CDN in front of Discourse](https://vercel.com/blog/how-we-run-vercels-cdn-in-front-of-discourse?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related)
- [Life of a Vercel request: Securing your app's traffic with Vercel](https://vercel.com/blog/life-of-a-request-securing-your-apps-traffic-with-vercel?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=related)

Full cross-link map for this page: [/docs/vercel-firewall.graph.md](/docs/vercel-firewall.graph.md?from=related&source_path=%2Fdocs%2Fvercel-firewall&source_site=vercel-docs&relationship=graph)
<!-- /docsgraph:related -->

- [Platform-wide firewall](#platform-wide-firewall): With [DDoS mitigation](/docs/vercel-firewall/ddos-mitigation), it protects against large-scale attacks such as DDoS and TCP floods and is available for free for all customers without any configuration required.
- [Web Application Firewall (WAF)](#vercel-waf): A customizable layer for fine-tuning security measures with logic tailored to your needs and [observability](#observability) into your web traffic.

### Concepts

Understand the fundamentals:

- How [Vercel protects every request](/docs/vercel-firewall/firewall-concepts#how-vercel-secures-requests).
- Why [DDoS](/docs/vercel-firewall/firewall-concepts#understanding-ddos) needs to be mitigated.
- How the firewall decides [which rule to apply first](#rule-execution-order).
- How the firewall uses [JA3 and JA4 TLS fingerprints](/docs/vercel-firewall/firewall-concepts#ja3-and-ja4-tls-fingerprints) to identify and restrict malicious traffic.

## Rule execution order

The automatic rules of the platform-wide firewall and the custom rules of the WAF work together in the following execution order:

1. [DDoS mitigation rules](/docs/vercel-firewall/ddos-mitigation)
2. [WAF IP blocking rules](/docs/vercel-firewall/vercel-waf/ip-blocking)
3. [WAF custom rules](/docs/vercel-firewall/vercel-waf/custom-rules)
4. [WAF Managed Rulesets](/docs/vercel-firewall/vercel-waf/managed-rulesets)

When you have more than one custom rule, you can [customize](/docs/vercel-firewall/vercel-waf/custom-rules#custom-rule-configuration) their order in the **Firewall** section in the sidebar of the project.

## Platform-wide firewall

> **🔒 Permissions Required**: DDoS Mitigation

Vercel provides automated [DDoS mitigation](/docs/vercel-firewall/ddos-mitigation) for all deployments, regardless of the plan that you are on. With this automated DDoS mitigation, we block incoming traffic if we identify abnormal or suspicious levels of incoming requests.

## Vercel WAF

> **🔒 Permissions Required**: Vercel WAF

The [Vercel WAF](/docs/vercel-firewall/vercel-waf) complements the platform-wide firewall by allowing you to define custom protection strategies using the following tools:

- [Custom Rules](/docs/vercel-firewall/vercel-waf/custom-rules)
- [IP Blocking](/docs/vercel-firewall/vercel-waf/ip-blocking)
- [WAF Managed Rulesets](/docs/vercel-firewall/vercel-waf/managed-rulesets)
- [Attack Mode](/docs/vercel-firewall/attack-mode)

You can also manage bypass rules and your WAF configuration programmatically with the [REST API](/docs/vercel-firewall/firewall-api) through the Vercel SDK, direct endpoint calls, or Terraform.

## Observability

You can use the following tools to [monitor the internet traffic](/docs/vercel-firewall/firewall-observability) at your team or project level:

- The [Monitoring](/docs/query/monitoring) feature at the team level allows you to create [queries](/docs/query/monitoring/monitoring-reference#example-queries) to visualize the traffic across your Vercel projects.
- **Firewall** in the Vercel dashboard sidebar on every project allows you to monitor the internet traffic to your deployments with a [traffic monitoring view](/docs/vercel-firewall/firewall-observability#traffic) that includes a live traffic window.
- [Firewall alerts](/docs/vercel-firewall/firewall-observability#firewall-alerts) allow you to react quickly to potential security threats.
- Use [Log Drains](/docs/drains/using-drains) to send your application logs to a Security Information and Event Management (SIEM) system.

---

[View full sitemap](/docs/sitemap)
