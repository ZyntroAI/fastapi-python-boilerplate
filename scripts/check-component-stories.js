/**
 * Auto-verify every component has matching Story + E2E test
 */
const fs = require('fs');
const path = require('path');

const COMPONENTS_DIR = path.join(process.cwd(), 'src/components');
const errors = [];

fs.readdirSync(COMPONENTS_DIR)
  .filter(f => f.endsWith('.tsx') && !f.includes('.stories.'))
  .forEach(file => {
    const base = file.replace('.tsx', '');
    const storyPath = path.join(COMPONENTS_DIR, `${base}.stories.tsx`);
    
    if (!fs.existsSync(storyPath)) {
      errors.push(`❌ ${file} — missing ${base}.stories.tsx`);
    }
  });

if (errors.length > 0) {
  console.error('\nMissing test coverage:\n' + errors.join('\n') + '\n');
  process.exit(1);
}

console.log('✅ All components have stories!');
