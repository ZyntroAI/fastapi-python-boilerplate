import { defineSkill } from '@google/gemini-cli-sdk'

export default defineSkill({
  id: 'security/secret-scan',
  name: 'Secret Scanner',
  version: '0.1.0',
  description: 'Detect and redact secrets',
  tags: ['security', 'audit'],
  permissions: ['repo:read'],
  async execute(context: any) {
    const { path } = context.input ?? {}
    if (!path) throw new Error('path required')
    const findings = await context.callMcp('gitleaks', 'detect', { path, redact: true })
    return { success: true, data: { findings }, meta: {} }
  }
})
