#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "=== Claude Code 설정 동기화 ==="

cp "$CLAUDE_DIR/CLAUDE.md" "$SCRIPT_DIR/claude/CLAUDE.md"
cp "$CLAUDE_DIR/settings.json" "$SCRIPT_DIR/claude/settings.json"

cp "$CLAUDE_DIR/commands/"*.md "$SCRIPT_DIR/claude/commands/" 2>/dev/null || true

rm -rf "$SCRIPT_DIR/claude/skills/"*
cp -r "$CLAUDE_DIR/skills/"* "$SCRIPT_DIR/claude/skills/" 2>/dev/null || true

node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync(process.env.HOME + '/.claude.json', 'utf8'));
const globalMcp = config.mcpServers || {};
const projectMcp = {};
for (const [key, val] of Object.entries(config.projects || {})) {
  if (val.mcpServers && Object.keys(val.mcpServers).length > 0) {
    projectMcp[key] = val.mcpServers;
  }
}
fs.writeFileSync('$SCRIPT_DIR/claude/mcp-servers.json', JSON.stringify({ globalMcpServers: globalMcp, projectMcpServers: projectMcp }, null, 2));
"

cd "$SCRIPT_DIR"
git add -A
if git diff --cached --quiet; then
  echo "변경사항 없음"
else
  git commit -m "sync claude config $(date +%Y-%m-%d_%H:%M)"
  git push
  echo "=== Push 완료 ==="
fi
