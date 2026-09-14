import { defineSkill } from '@google/gemini-cli-sdk'

export default defineSkill({
  id: 'coding/typescript',
  name: 'TypeScript Checker',
  version: '0.1.0',
  description: 'Lint and typecheck TypeScript',
  tags: ['coding', 'typescript'],
  permissions: ['repo:read'],
  async execute(context: any) {
    const { path } = context.input ?? {}
    if (!path) throw new Error('path required')
    const diags = await context.callMcp('shell', 'run', { cmd: 'tsc --noEmit && eslint .', cwd: path })
    return { success: true, data: { diags }, meta: {} }
  }
})
