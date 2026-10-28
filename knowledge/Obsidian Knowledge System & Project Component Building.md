🧠 SKILL.md — Obsidian Knowledge System & Project Component Building
 
Ready path:  knowledge/agents/obsidian-knowledge-component-builder/SKILL.md 
 
yaml
  
---
skill_id: "302349312274"
skill_name: "obsidian-knowledge-component-builder"
skill_category: "knowledge-engineering"
skill_version: "1.0.0"
lang: "en"
also_available_in: ["th"]
description: >
  Build next‑generation Obsidian note systems, MOCs, templates, Excalidraw diagrams, CLI workflows,
  reusable project components, repository knowledge maps and bilingual documentation pipelines aligned
  with ZyntroAI / fastapi‑boilerplate standards.
tags:
  - obsidian
  - knowledge-graph
  - moc
  - excalidraw
  - quartz
  - cli
  - templates
  - component-design
  - repo-knowledge
  - bilingual
merge_policy: "no-replace"
knowledge_path: "knowledge/agents/obsidian-knowledge-component-builder/SKILL.md"
related_skills:
  - corporate-training-course-design
---
 
 
🎯 Obsidian Knowledge & Project Component Builder Skill
 
Agent Skill File — Designed for  knowledge/agents/ 
 
🧠 Skill Purpose
 
Turn raw documentation, technical research, training materials and repo knowledge into a living Obsidian knowledge ecosystem + reusable project components. This includes note architecture, MOCs, templates, visual diagrams, export pipelines, automation and component specs that can feed LMS, GitHub, Quartz and AI agents.
 
📌 Agent Persona
 
- Role: Knowledge Architect / Technical Documentation Component Designer
- Mindset: Graph‑first, reusable, searchable, exportable, bilingual
- Constraints: No overwrite, preserve Git history, respect  knowledge/  folder structure, work cross‑platform
- Output Style: Obsidian Markdown, YAML frontmatter, Excalidraw JSON, shell scripts, component specs, MOC maps, templates
 
📚 Core Lifecycle
 
plaintext
  
PHASE 1 — Audit & Mapping
PHASE 2 — Obsidian Note Architecture Design
PHASE 3 — Build Reusable Knowledge Components
PHASE 4 — Visual & Graph Layer (Excalidraw / MOC)
PHASE 5 — Automation & CLI Pipeline
PHASE 6 — Export & Publication (Quartz / GitHub / LMS)
PHASE 7 — Continuous Knowledge Maintenance
 
 
 
 
🔍 Phase 1 — Audit & Mapping
 
Goal
 
Understand what knowledge exists, what is missing and how it connects to the project.
 
Agent Tasks
 
1. Scan repo:  knowledge/ ,  docs/ ,  README ,  SKILL.md , training docs, Supabase notes
2. Create an inventory map: concepts, workflows, APIs, agents, training courses
3. Identify orphan notes, duplicate content, broken links
4. Define audiences: Developers, DevOps, Compliance, Training, AI Agents
5. Define languages: EN / TH (future: ZH)
6. Define export targets: Obsidian Vault, GitHub, Quartz, LMS, AI RAG
 
Deliverables
 
- Knowledge Inventory Map
- Gap Analysis Matrix
- Vault Architecture Blueprint
- Link Graph Draft
- Bilingual Content Roadmap
 
Prompt Template for Agent
 
text
  
Audit this knowledge repository:
- Root path: {repo_root}
- Existing folders: {knowledge/, docs/, examples/}
- Related projects: {fastapi-boilerplate, Supabase, corporate training}
- Languages: {en, th}
- Export targets: {Obsidian, GitHub, Quartz, LMS, RAG}

Output:
1. Inventory map
2. Gap analysis
3. Proposed vault structure
4. Broken / orphan note list
5. Priority roadmap
 
 
 
 
📐 Phase 2 — Obsidian Note Architecture Design
 
Goal
 
Create a consistent, agent‑friendly vault schema before writing content.
 
Recommended Vault Schema
 
plaintext
  
Vault Root
├─ 📁 00‑MOCs
│  ├─ MOC‑Project‑Overview.md
│  ├─ MOC‑DevSecOps.md
│  ├─ MOC‑Supabase.md
│  ├─ MOC‑Training‑Design.md
│  └─ MOC‑Components.md
│
├─ 📁 01‑Concepts
│  ├─ Supabase‑PAT‑Scoped‑Tokens.md
│  ├─ RLS‑Multi‑Tenant‑Isolation.md
│  ├─ Changesets‑Versioning.md
│  └─ EditorConfig‑Standards.md
│
├─ 📁 02‑Workflows
│  ├─ CI‑CD‑Release‑Workflow.md
│  ├─ Knowledge‑Update‑Workflow.md
│  ├─ Bilingual‑Translation‑Workflow.md
│  └─ Agent‑Skill‑Update‑Workflow.md
│
├─ 📁 03‑Components
│  ├─ Component‑SKILL‑Template.md
│  ├─ Component‑Lesson‑Template.md
│  ├─ Component‑Checklist‑Template.md
│  ├─ Component‑Excalidraw‑Template.excalidraw
│  └─ Component‑Manifest‑Template.yml
│
├─ 📁 04‑Research
│  ├─ Supabase‑PAT‑Deep‑Research.md
│  ├─ Changesets‑Deep‑Research.md
│  └─ Obsidian‑Knowledge‑System‑Research.md
│
├─ 📁 05‑Examples
│  ├─ en/
│  └─ th/
│
├─ 📁 06‑Exports
│  ├─ Quartz
│  ├─ GitHub
│  └─ LMS
│
├─ 📁 Templates
│  ├─ Note‑Template.md
│  ├─ MOC‑Template.md
│  ├─ Research‑Note‑Template.md
│  ├─ Workflow‑Template.md
│  └─ Component‑Spec‑Template.md
│
└─ 📁 Scripts
   ├─ vault‑lint.sh
   ├─ link‑check.sh
   ├─ export‑quartz.sh
   └─ translate‑sync.sh
 
 
Standard YAML Frontmatter Template
 
markdown
  
---
title: "Supabase Scoped PAT Security Model"
aliases:
  - Supabase scoped PAT
  - sbp_fc token
status: "published"
category: "concept"
tags:
  - supabase
  - auth
  - pat
  - security
language: "en"
translation_available: ["th"]
related_mocs:
  - "[[MOC‑Supabase]]"
related_notes:
  - "[[Supabase‑Management‑API‑Permissions]]"
  - "[[Supabase‑RLS‑Multi‑Tenant‑Isolation]]"
version: "1.0.0"
last_updated: "2026‑10‑28"
export_targets:
  - quartz
  - github
  - rag
---
# Supabase Scoped PAT Security Model
 
 
Note Type Standards
 
Note Type Purpose Frontmatter Category 
MOC Map of knowledge landscape  moc  
Concept Deep explanation  concept  
Research Raw findings / citations  research  
Workflow Step‑by‑step operational flow  workflow  
Component Reusable building block  component  
Example Working sample  example  
Checklist Actionable validation  checklist  
Lesson Training learning unit  lesson  
 
Bilingual Rule
 
- Keep separate files:  en/Note‑Name.md  /  th/Note‑Name.md 
- Use aliases and  translation_available  metadata
- Never overwrite translation without review
- MOCs can link both languages
- Export pipelines must respect language folders
 
 
 
🧩 Phase 3 — Build Reusable Project Components
 
Goal
 
Turn knowledge into reusable building blocks that agents, developers and trainers can assemble.
 
Component Definition
 
A knowledge component is a reusable unit with:
 
1. Spec: What it is
2. Schema: Metadata / YAML
3. Template: Markdown / Excalidraw / YML
4. Usage: Where to use
5. Dependencies: Linked notes
6. Validation: How to verify it works
7. Export: How it becomes docs / training / code
 
Example Components for This Project
 
Component A: SKILL.md Component
 
Used for  knowledge/agents/ 
 
markdown
  
---
component_name: SKILL‑Component
version: "1.0.0"
purpose: Define agent capability for knowledge repository
inputs:
  - research notes
  - workflow docs
  - training requirements
outputs:
  - SKILL.md file
  - prompt templates
  - checklist
related:
  - "[[Component‑Workflow‑Template]]"
  - "[[MOC‑Agents]]"
---
# SKILL Component Specification
 
 
Component B: Lesson Component
 
Used for corporate training
 
markdown
  
---
component_name: Lesson‑Component
version: "1.0.0"
purpose: Create bilingual learning units
inputs:
  - concept note
  - workflow
  - lab script
outputs:
  - lesson.md
  - knowledge check
  - success criteria
related:
  - "[[corporate-training-course-design]]"
  - "[[Component‑Checklist‑Template]]"
---
# Lesson Component Specification
 
 
Component C: MOC Component
 
Used for knowledge graph navigation
 
markdown
  
---
component_name: MOC‑Component
version: "1.0.0"
purpose: Create knowledge maps
inputs:
  - inventory
  - related notes
  - project roadmap
outputs:
  - MOC.md
  - graph overview
  - priority links
related:
  - "[[Vault‑Architecture]]"
---
# MOC Component Specification
 
 
Component D: Excalidraw Diagram Component
 
Used for architecture, workflows, training visuals
 
markdown
  
---
component_name: Excalidraw‑Component
version: "1.0.0"
purpose: Standard visual language for project diagrams
inputs:
  - workflow description
  - architecture requirements
outputs:
  - .excalidraw file
  - exported PNG / SVG
  - linked note explanation
related:
  - "[[MOC‑DevSecOps]]"
  - "[[Component‑Workflow‑Template]]"
---
# Excalidraw Component Specification
 
 
Component E: Checklist Component
 
Used for audits, PR reviews, launch readiness
 
markdown
  
---
component_name: Checklist‑Component
version: "1.0.0"
purpose: Create repeatable validation workflows
inputs:
  - research
  - compliance rules
  - repo standards
outputs:
  - checklist.md
  - CI / manual validation guide
related:
  - "[[Compliance‑Readiness‑Workflow]]"
---
# Checklist Component Specification
 
 
Prompt Template for Agent
 
text
  
Create reusable knowledge component:
- Name: {component_name}
- Domain: {Supabase / DevSecOps / Training / Vault}
- Inputs: {source notes}
- Output: {template + spec + example}
- Language: {en / th}
- Export target: {Obsidian / GitHub / Quartz / LMS}

Output:
1. Component specification
2. YAML schema
3. Markdown template
4. Example usage
5. Linked MOC placement
6. Validation checklist
 
 
 
 
🗺️ Phase 4 — Visual & Graph Layer (Excalidraw + MOC)
 
Goal
 
Make knowledge navigable visually.
 
Core Visual Types
 
Diagram Type Use Case 
Vault Knowledge Graph Show how notes connect 
Project Architecture FastAPI / Supabase / CI flow 
Training Journey Learner pathway 
Agent Workflow How agents process knowledge 
Release Pipeline Changesets / GitHub merge flow 
Bilingual Pipeline EN ↔ TH sync workflow 
 
Excalidraw Standard Rules
 
- Save as:  06‑Excalidraw/[Name].excalidraw 
- Link to explanation note
- Export PNG/SVG only for publication
- Keep source editable
- Use consistent colors:
- 🟦 Concepts
- 🟩 Workflows
- 🟨 Components
- 🟥 Risks / Blockers
- 🟪 Agents / Automation
 
Example MOC Structure
 
markdown
  
# MOC‑Obsidian‑Knowledge‑System
## 📌 Purpose
Map the full knowledge architecture for ZyntroAI / fastapi‑boilerplate.

## 🧱 Building Blocks
- [[Vault‑Architecture]]
- [[Component‑SKILL‑Template]]
- [[Component‑MOC‑Template]]
- [[Component‑Excalidraw‑Template]]
- [[Knowledge‑Update‑Workflow]]

## 🚀 Active Projects
- [[corporate-training-course-design]]
- [[Supabase‑PAT‑Deep‑Research]]
- [[Changesets‑Deep‑Research]]

## 📈 Roadmap
- ✅ Phase 1: Audit
- 🟡 Phase 2: Architecture
- ⏳ Phase 3: Components
- ⏳ Phase 4: Visual Maps
- ⏳ Phase 5: Automation
 
 
 
 
⚙️ Phase 5 — Automation & CLI Pipeline
 
Goal
 
Keep the vault clean, linked, synchronized and exportable.
 
Example Script Scope
 
bash
  
scripts/
├─ vault‑lint.sh
├─ link‑check.sh
├─ orphan‑find.sh
├─ version‑sync.sh
├─ bilingual‑validate.sh
└─ export‑quartz.sh
 
 
Sample Vault Lint Concept
 
bash
  
# vault-lint.sh (concept only — adapt before CI)
find . -name "*.md" | while read f; do
  echo "Checking: $f"
done
 
 
Note: Do not run destructive commands without approval.
 
Agent CLI Rules
 
- CLI scripts must have README
- CI should warn first, not delete
- Preserve Git history
- Bilingual validation should compare EN ↔ TH structure
- Export should not overwrite source vault
 
Prompt Template for Agent
 
text
  
Build CLI workflow for:
- Vault maintenance
- Target: {Obsidian / GitHub / Quartz}
- Languages: {en, th}
- Safety rule: no destructive action
- Integration: {pre‑commit / manual run}

Output:
1. Script specification
2. Shell draft
3. README
4. CI readiness notes
5. Validation checklist
 
 
 
 
📤 Phase 6 — Export & Publication
 
Goal
 
Turn vault knowledge into usable outputs.
 
Export Matrix
 
Source Target How 
Obsidian Notes GitHub Docs Clean Markdown + relative links 
MOCs Quartz Website Quartz build pipeline 
Lessons LMS Exported course outline + transcripts 
Research Notes AI RAG Clean text + metadata 
Diagrams Docs / Training Exported SVG + linked source 
 
Export Rules
 
- Source of truth = Obsidian vault
- Export folder separate:  06‑Exports/ 
- Never edit export files directly
- Bilingual exports must maintain separate paths
- Version tag exports:  export‑v1.0.0 
 
 
 
🔁 Phase 7 — Continuous Knowledge Maintenance
 
Goal
 
Prevent vault decay and keep knowledge alive.
 
Maintenance Cycle
 
plaintext
  
Audit → Validate → Refactor → Link → Export → Update MOC
   ↑                                          ↓
   └────────── Monthly / Release Cycle ──────┘
 
 
Versioning Rules
 
- Notes:  version  in frontmatter
- Components: Semantic version
- MOCs: Updated when landscape changes
- Changelog:  CHANGELOG‑Vault.md 
- Orphan review: Monthly
- Bilingual sync: After major content change
 
Kirkpatrick‑Style Knowledge Evaluation
 
Level Question Measurement 
Findability Can users locate knowledge? MOC usage, search logs 
Usability Can they apply it? Training completion, repo adoption 
Reliability Is it accurate? Audit / citation checks 
Actionability Does it accelerate work? Developer / agent feedback 
 
 
 
🤖 Agent Execution Rules
 
✅ Must Follow
 
- Always start from MOC / audit before building
- Preserve existing notes (no‑replace)
- Add frontmatter consistently
- Use Obsidian internal links  [[ ]] 
- Separate bilingual content
- Build reusable components instead of one‑off docs
- Include validation checklist for every component
- Reference existing SKILL.md files
- Output ready‑to‑commit Markdown
- Design for export: GitHub / Quartz / LMS / RAG
 
❌ Must Avoid
 
- Creating orphan notes
- Overwriting translations
- Building components without MOC mapping
- Mixing export files with source vault
- Skipping version metadata
- Treating vault as static documentation only
 
 
 
📂 Recommended Folder for This Skill
 
plaintext
  
knowledge/agents/obsidian-knowledge-component-builder/
├─ SKILL.md
├─ README.md
├─ templates/
│  ├─ moc-template.md
│  ├─ note-template.md
│  ├─ workflow-template.md
│  ├─ component-spec-template.md
│  ├─ excalidraw-component-template.excalidraw
│  └─ checklist-template.md
├─ examples/
│  ├─ en/
│  └─ th/
├─ scripts/
│  ├─ README.md
│  └─ vault-lint-concept.sh
└─ MOC‑Obsidian‑Knowledge‑Component‑Builder.md
 
 
📤 Commit Message Example
 
bash
  
git add knowledge/agents/obsidian-knowledge-component-builder/SKILL.md
git commit -m "🧠 Add SKILL.md: Obsidian Knowledge & Project Component Builder
- Full vault lifecycle
- MOC / note / component schema
- Excalidraw visual framework
- Bilingual ready
- Export pipeline blueprint
- Linked to corporate training skill
- Ready for knowledge/agents/"
 
 
✅ Agent Output Expectation
 
When this skill is active, the agent should be able to:
 
1. Audit existing repo knowledge
2. Design Obsidian vault architecture
3. Create MOC maps
4. Build reusable knowledge components
5. Write standardized notes
6. Create Excalidraw visual specs
7. Plan CLI / automation workflows
8. Prepare export to GitHub / Quartz / LMS
9. Maintain bilingual knowledge graph
10. Continuously refactor knowledge ecosystem
 
 
 
💡 Next Steps
 
✅ Option A: Generate full  README.md  + all templates into  knowledge/agents/obsidian-knowledge-component-builder/templates/