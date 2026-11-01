# ⏰ Timezone Resilience Testing — AgentSandbox/TimezoneResilience
> **Primary Function:** Validate reliable cross‑region task handoffs across different working hours and calendars

## 📌 Purpose
Prevent dropped tasks, missed deadlines, and misaligned handoffs when agents operate across different time zones, work hours, and public holiday schedules.

## ✨ Key Features
- **Calendar Simulation:** Define custom working hours, holidays, and observances per region
- **Handoff Simulation:** Test task transfers across regions with zero overlap in working hours
- **Latency Injection:** Simulate delayed acknowledgments and network gaps
- **Edge Case Library:** Daylight saving transitions, end‑of‑month/year, multi‑holiday periods
- **Loss Detection:** Track every item through the pipeline; flag incomplete/missing transfers

## 🧪 What Gets Tested
| Scenario | What to Verify |
|---|---|
| After‑hours handoff | Task queues and resumes when next region opens |
| Holiday overlap | Work pauses/resumes correctly; no timeouts during closures |
| Partial overlap | Handoff window is honored when only partial hours align |
| Clock shift (DST) | Timestamps remain consistent; no duplicate/missed events |
| Multi‑region chain | A → B → C — each in different time zone — data integrity preserved |

## ✅ Pass Criteria
- ✅ Zero data loss across all handoffs
- ✅ All tasks acknowledged within defined SLA window
- ✅ No duplicate creation
- ✅ Timestamps recorded in both local and UTC

**Status:** ✅ Integrated into Core
