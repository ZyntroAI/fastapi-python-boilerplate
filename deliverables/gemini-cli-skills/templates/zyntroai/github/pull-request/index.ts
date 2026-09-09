import { defineSkill } from '@google/gemini-cli-sdk'

export default defineSkill({
  id: 'github/pull-request',
  name: 'GitHub PR Manager',
  version: '0.1.0',
  description: 'Analyze, review, and manage pull requests',
  tags: ['github', 'automation', 'devops'],
  permissions: ['repo:read', 'repo:write'],
  async execute(context: any) {
    const { owner, repo, pr } = context.input ?? {}
    if (!owner || !repo || !pr) throw new Error('owner/repo/pr required')
    const summary = await context.callMcp('github', 'getPullRequest', { owner, repo, number: pr })
    return { success: true, data: { pr, summary }, meta: {} }
  }
})
