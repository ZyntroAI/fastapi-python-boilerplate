// ZyntroAI canonical skill template
import { defineSkill, SkillContext, SkillResult } from '@google/gemini-cli-sdk'

export default defineSkill({
  id: '<category>/<name>',
  name: '<Human Readable Name>',
  version: '1.0.0',
  description: '<What it does>',
  tags: ['<tag>'],
  permissions: ['repo:read'],
  async execute(context: SkillContext): Promise<SkillResult> {
    return { success: true, data: {}, meta: { latency: 0, tokens: 0 } }
  }
})
