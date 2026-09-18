<#
.SYNOPSIS
Setup MCP Environment for ZyntroAI
#>
$ErrorActionPreference = "Stop"

Write-Host "🔧 Setting up MCP Environment..." -ForegroundColor Cyan

# 1. Create .env
if (-not (Test-Path .env)) {
    Copy-Item .env.mcp .env
    Write-Host "✅ Created .env from template — please edit with your tokens" -ForegroundColor Green
}

# 2. Create directories
"data", "src", "docs", "config", "scripts" | ForEach-Object {
    if (-not (Test-Path $_)) { New-Item -ItemType Directory -Force | Out-Null }
}
Write-Host "✅ Directory structure ready" -ForegroundColor Green

# 3. Check npx
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npx not found — install Node.js 20+: https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js/npx available" -ForegroundColor Green

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "📁 Config: $(Get-Location)\mcp-config.json"
Write-Host "📝 Edit .env → then add config to your MCP client"
