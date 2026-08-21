
python_script = r'''#!/usr/bin/env python3
"""
Auto-run script for PR #79 - 22 AUG 2026
Repository: ZyntroAI/new-crystalcastle
This script automatically applies all CI fixes and project setup changes.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def info(msg):  print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")
def ok(msg):    print(f"{Colors.GREEN}[OK]{Colors.NC}   {msg}")
def warn(msg):  print(f"{Colors.YELLOW}[WARN]{Colors.NC} {msg}")
def err(msg):   print(f"{Colors.RED}[ERR]{Colors.NC}  {msg}")

def run_cmd(cmd, check=False, capture=False):
    """Run a shell command."""
    info(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if check and result.returncode != 0:
        err(f"Command failed: {cmd}")
        if result.stderr:
            print(result.stderr)
        sys.exit(1)
    return result

def write_file(path, content):
    """Write content to a file, creating parent directories if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    ok(f"Created {path}")

def main():
    print("=" * 50)
    print("  PR #79 Auto-Setup Script")
    print("  Date: 22 AUG 2026")
    print("=" * 50)
    print()

    # =========================================================================
    # STEP 1: Delete broken CI file
    # =========================================================================
    info("Step 1: Deleting broken CI file...")
    broken_ci = Path(".github/jobs/CI")
    if broken_ci.exists():
        broken_ci.unlink()
        # Remove empty parent directory
        try:
            Path(".github/jobs").rmdir()
        except OSError:
            pass
        ok("Deleted .github/jobs/CI")
    else:
        warn(".github/jobs/CI not found, skipping delete")

    # =========================================================================
    # STEP 2: Create correct GitHub Actions workflow
    # =========================================================================
    info("Step 2: Creating .github/workflows/ci.yml...")
    ci_yml = '''name: CI

on:
  push:
    branches:
      - main
      - master
      - dev
      - pure-agent
      - root
      - develop
      - crystalcastle-ai
  pull_request:
    branches:
      - main
      - master
      - dev
      - pure-agent
      - root
      - develop
      - crystalcastle-ai
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build-and-test:
    name: Node.js ${{ matrix.node-version }}
    runs-on: ubuntu-latest

    strategy:
      fail-fast: true
      matrix:
        node-version: ["20", "22"]

    env:
      CI: true

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm

      - name: Validate package lock
        run: npm ci

      - name: Run lint
        run: npm run lint --if-present

      - name: Run type check
        run: npm run typecheck --if-present

      - name: Run tests
        run: npm run test --if-present

      - name: Build
        run: npm run build --if-present

      - name: Upload build artifact
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: build-node-${{ matrix.node-version }}
          path: |
            build
            dist
          if-no-files-found: ignore
'''
    write_file(".github/workflows/ci.yml", ci_yml)

    # =========================================================================
    # STEP 3: Fix package.json
    # =========================================================================
    info("Step 3: Fixing package.json...")
    pkg_path = Path("package.json")
    if not pkg_path.exists():
        err("package.json not found!")
        sys.exit(1)

    with open(pkg_path, 'r', encoding='utf-8') as f:
        pkg = json.load(f)

    # Fix scripts
    pkg.setdefault("scripts", {})
    pkg["scripts"]["typecheck"] = "tsc --noEmit"
    pkg["scripts"]["test"] = "vitest run"
    pkg["scripts"]["test:watch"] = "vitest"

    # Fix devDependencies - remove invalid entries
    dev_deps = pkg.get("devDependencies", {})
    for key in ["node", "npm", "yarn"]:
        dev_deps.pop(key, None)

    # Add new dev dependencies if not present
    if "jsdom" not in dev_deps:
        dev_deps["jsdom"] = "^24.0.0"
    if "vitest" not in dev_deps:
        dev_deps["vitest"] = "^2.0.0"

    pkg["devDependencies"] = dev_deps

    with open(pkg_path, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, indent=2)
        f.write("\n")
    ok("Fixed package.json")

    # =========================================================================
    # STEP 4: Create TypeScript configs
    # =========================================================================
    info("Step 4: Creating TypeScript configuration files...")

    tsconfig = '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
'''
    write_file("tsconfig.json", tsconfig)

    tsconfig_node = '''{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
'''
    write_file("tsconfig.node.json", tsconfig_node)

    # =========================================================================
    # STEP 5: Create/Update Vite config with Vitest
    # =========================================================================
    info("Step 5: Creating vite.config.ts with Vitest support...")

    vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
'''
    write_file("vite.config.ts", vite_config)

    # =========================================================================
    # STEP 6: Create test setup file
    # =========================================================================
    info("Step 6: Creating test setup file...")

    setup_ts = '''import '@testing-library/jest-dom/vitest'
'''
    write_file("src/test/setup.ts", setup_ts)

    # =========================================================================
    # STEP 7: Create sample test
    # =========================================================================
    info("Step 7: Creating sample App test...")

    app_test = '''import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(document.body).toBeInTheDocument()
  })
})
'''
    write_file("src/App.test.tsx", app_test)

    # =========================================================================
    # STEP 8: Install new dependencies
    # =========================================================================
    info("Step 8: Installing new dev dependencies...")
    result = run_cmd("npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom", check=False)
    if result.returncode == 0:
        ok("Installed dependencies via npm")
    else:
        err("npm install failed. Please check your Node.js/npm setup.")
        sys.exit(1)

    # =========================================================================
    # STEP 9: Verify setup
    # =========================================================================
    print()
    print("=" * 50)
    info("Running verification checks...")
    print("=" * 50)

    info("Checking TypeScript config...")
    result = run_cmd("npx tsc --noEmit", check=False)
    if result.returncode == 0:
        ok("TypeScript check passed")
    else:
        warn("TypeScript check had issues (may need src files)")

    info("Checking lint...")
    result = run_cmd("npm run lint --if-present", check=False)
    if result.returncode == 0:
        ok("Lint check passed")
    else:
        warn("Lint check had issues")

    info("Running tests...")
    result = run_cmd("npm run test --if-present", check=False)
    if result.returncode == 0:
        ok("Tests passed")
    else:
        warn("Tests had issues")

    info("Running build...")
    result = run_cmd("npm run build --if-present", check=False)
    if result.returncode == 0:
        ok("Build passed")
    else:
        warn("Build had issues")

    # =========================================================================
    # DONE
    # =========================================================================
    print()
    print("=" * 50)
    print(f"{Colors.GREEN}PR #79 Auto-Setup Complete!{Colors.NC}")
    print("=" * 50)
    print()
    print("Summary of changes:")
    print("  [DELETE] .github/jobs/CI")
    print("  [CREATE] .github/workflows/ci.yml")
    print("  [MODIFY] package.json")
    print("  [CREATE] tsconfig.json")
    print("  [CREATE] tsconfig.node.json")
    print("  [CREATE] vite.config.ts")
    print("  [CREATE] src/test/setup.ts")
    print("  [CREATE] src/App.test.tsx")
    print()
    print("Next steps:")
    print("  1. Review the changes: git status && git diff")
    print("  2. Commit the changes: git add -A && git commit -m 'fix: complete CI setup and project config'")
    print("  3. Push to your branch: git push origin zyntromedia-patch-20")
    print()

if __name__ == "__main__":
    main()
'''

with open('/mnt/agents/output/auto_setup_pr79.py', 'w', encoding='utf-8') as f:
    f.write(python_script)

print("Python script created successfully at /mnt/agents/output/auto_setup_pr79.py")
print()
print("Usage:")
print("  python3 auto_setup_pr79.py")
