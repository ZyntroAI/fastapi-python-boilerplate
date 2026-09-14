import { defineSkill } from '@google/gemini-cli-sdk'

export default defineSkill({
  id: 'devops/ci-cd',
  name: 'CI/CD Pipeline',
  version: '0.1.0',
  description: 'Pipeline status, retry, and wait',
  tags: ['devops', 'ci-cd'],
  permissions: ['repo:read', 'actions:read'],
  async execute(context: any) {
    const { owner, repo, run } = context.input ?? {}
    if (!owner || !repo || !run) throw new Error('owner/repo/run required')
    const status = await context.callMcp('github', 'getWorkflowRun', { owner, repo, run })
    return { success: true, data: { run, status }, meta: {} }
  }
})
