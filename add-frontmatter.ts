📄 add-frontmatter.ts — Script
 
typescript  
/**
 * ZyntroAI — Add Frontmatter Script
 * Adds standardized YAML frontmatter to markdown files in the Knowledge Vault
 * Version: 1.0.0
 * Created: 2026-10-12
 * License: Internal use
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ─── Config ───
const VAULT_ROOT = process.env.VAULT_ROOT || path.resolve(__dirname, '../');
const DEFAULT_TAGS = ['auto-generated', 'frontmatter-script'];
const DRY_RUN = process.env.DRY_RUN === 'true';

// ─── Frontmatter Template ───
interface Frontmatter {
  title: string;
  aliases?: string[];
  type: string;
  tags: string[];
  created: string;
  updated?: string;
  status: string;
  visibility: string;
  description?: string;
}

function generateFrontmatter(
  filePath: string,
  type: string = 'note',
  extra: Partial<Frontmatter> = {}
): string {
  const name = path.basename(filePath, '.md');
  const now = new Date().toISOString();

  const fm: Frontmatter = {
    title: name,
    type,
    tags: [...DEFAULT_TAGS, type],
    created: now,
    status: 'active',
    visibility: 'public',
    ...extra,
  };

  const yaml = Object.entries(fm)
    .map(([key, value]) => {
      if (Array.isArray(value)) {
        return `${key}:\n${value.map(v => `  - ${v}`).join('\n')}`;
      }
      return `${key}: ${value}`;
    })
    .join('\n');

  return `---\n${yaml}\n---\n\n`;
}

// ─── Process Single File ───
async function processFile(
  file: string,
  type: string = 'note',
  extra: Partial<Frontmatter> = {}
): Promise<void> {
  const fullPath = path.join(VAULT_ROOT, file);

  try {
    let content = await fs.readFile(fullPath, 'utf-8');

    // Skip if frontmatter already exists
    if (content.trimStart().startsWith('---\n')) {
      console.log(`⏭️  Skipped (has frontmatter): ${file}`);
      return;
    }

    const frontmatter = generateFrontmatter(file, type, extra);
    const newContent = frontmatter + content;

    if (DRY_RUN) {
      console.log(`✅ Would add frontmatter to: ${file}`);
      console.log(frontmatter);
      return;
    }

    await fs.writeFile(fullPath, newContent, 'utf-8');
    console.log(`✅ Updated: ${file}`);
  } catch (err) {
    console.error(`❌ Error processing ${file}:`, (err as Error).message);
  }
}

// ─── Agent-Specific Frontmatter Presets ───
export const AgentPresets = {
  Researcher: {
    type: 'agent/researcher',
    tags: ['agent', 'research', 'zyntroai'],
    description: 'Deep research, citations, document analysis',
  },
  Coder: {
    type: 'agent/coder',
    tags: ['agent', 'code', 'development', 'devops'],
    description: 'Code generation, review, and debugging',
  },
  Translator: {
    type: 'agent/translator',
    tags: ['agent', 'translation', 'bilingual', 'thai', 'english'],
    description: 'TH/EN localization and precise translation',
  },
  Summarizer: {
    type: 'agent/summarizer',
    tags: ['agent', 'summary', 'notes', 'meetings'],
    description: 'Meeting notes, document distillation, key points',
  },
};

// ─── CLI Runner ───
async function main() {
  const [fileArg, agentType] = process.argv.slice(2);

  if (!fileArg) {
    console.log(`
📌 Usage: npx tsx add-frontmatter.ts <file.md> [agent-type]

Agent Types:
  Researcher   — Deep research & citations
  Coder        — Code generation & review
  Translator   — TH/EN bilingual translation
  Summarizer   — Summaries & meeting notes

Options:
  DRY_RUN=true  Preview without saving
  VAULT_ROOT=   Path to your Obsidian Vault

Example:
  npx tsx add-frontmatter.ts "Agents/Researcher.md" Researcher
`);
    process.exit(0);
  }

  const extra =
    agentType && AgentPresets[agentType as keyof typeof AgentPresets]
      ? AgentPresets[agentType as keyof typeof AgentPresets]
      : { type: 'note' };

  await processFile(fileArg, extra.type, extra);
}

main().catch(console.error);
 
 
 
 
📋 Package.json Dependencies
 
json  
{
  "name": "zyntroai-tools",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "add-frontmatter": "tsx add-frontmatter.ts",
    "add-frontmatter:dry": "DRY_RUN=true tsx add-frontmatter.ts"
  },
  "devDependencies": {
    "tsx": "^4.7.0",
    "typescript": "^5.3.0"
  }
}
 
 
 
 
🚀 How to Use
 
bash  
# Install dependencies
npm install

# Preview (dry run) — see what will be added
DRY_RUN=true npm run add-frontmatter -- "Agents/Researcher.md" Researcher

# Apply to file
npm run add-frontmatter -- "Agents/Researcher.md" Researcher
npm run add-frontmatter -- "Agents/Coder.md" Coder
npm run add-frontmatter -- "Agents/Translator.md" Translator
npm run add-frontmatter -- "Agents/Summarizer.md" Summarizer
 
 
 
 
📝 Example Output — Researcher Agent
 
markdown  
---
title: Researcher
type: agent/researcher
tags:
  - auto-generated
  - note
  - agent
  - research
  - zyntroai
created: 2026-10-12T02:50:00.000Z
status: active
visibility: public
description: Deep research, citations, document analysis
---

# Researcher Agent

...existing content here...
 
 
 
 
✅ Ready to use: Save as  add-frontmatter.ts  in your project root. Works alongside your ZyntroAI System Model folder structure.
 
ต้องการให้สร้างไฟล์ตัวอย่างสำหรับแต่ละ Agent ด้วยไหมครับ? 😊