#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Setting up MCP Environment..."

# 1. Load env
if [ ! -f .env ]; then
    cp .env.mcp .env
    echo "✅ Created .env from template — please edit with your tokens"
fi
set -a; source .env; set +a

# 2. Create directories
mkdir -p data src docs config scripts
echo "✅ Directory structure ready"

# 3. Validate tokens
if [[ "$GITHUB_TOKEN" == "ghp_yourFineGrainedTokenHere" ]]; then
    echo "⚠️  Update GITHUB_TOKEN in .env before using GitHub server"
fi

# 4. Verify npx
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found — install Node.js 20+: https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js/npx available"

echo ""
echo "🎉 Setup complete!"
echo "📁 Config: $(pwd)/mcp-config.json"
echo "📝 Edit .env → then add config to your MCP client"
