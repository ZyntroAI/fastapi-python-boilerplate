# 🗺️ Agent Capability Map — AgentCapabilityMap
> **Primary Function:** Maintain a dynamic registry of agent skills, expertise, and performance across all regions

## 📌 Purpose
Enable intelligent task routing by knowing exactly what each agent is good at, where they operate, what languages they speak, and how reliably they perform — in real time.

## ✨ Key Features
- **Skill Registry:** What each agent can do — data analysis, customer support, legal guidance, emergency coordination, etc.
- **Regional Expertise:** Which jurisdictions, cultures, and local frameworks each agent understands
- **Performance Metrics:** Response time, accuracy rating, success rate, user satisfaction
- **Dynamic Updates:** Auto‑refreshes based on recent performance history
- **Smart Matching:** Recommends best‑suited agent or team for any given request

## 📊 Map Data Structure
```json
{
  "agent_id": "sg-001",
  "region": "Southeast Asia",
  "languages": ["en", "th", "zh"],
  "expertise": ["cross-border logistics", "local regulations"],
  "performance": {
    "accuracy_score": 0.98,
    "avg_response_time_sec": 1.8,
    "tasks_completed": 1240
  },
  "availability": "online"
}
