#!/bin/bash
# Claude Code 설정 동기화 스크립트
# .claude 디렉토리의 설정을 이 레포로 복사 후 push

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "=== Claude Code 설정 동기화 ==="

# 설정 파일 복사
cp "$CLAUDE_DIR/CLAUDE.md" "$SCRIPT_DIR/claude/CLAUDE.md"
cp "$CLAUDE_DIR/settings.json" "$SCRIPT_DIR/claude/settings.json"

# commands
cp "$CLAUDE_DIR/commands/"*.md "$SCRIPT_DIR/claude/commands/" 2>/dev/null || true

# skills (recursive, 덮어쓰기)
rm -rf "$SCRIPT_DIR/claude/skills/"*
cp -r "$CLAUDE_DIR/skills/"* "$SCRIPT_DIR/claude/skills/" 2>/dev/null || true

# scripts
cp "$CLAUDE_DIR/scripts/"* "$SCRIPT_DIR/claude/scripts/" 2>/dev/null || true

# MCP servers 추출 (API 키 제외)
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

# Git push
cd "$SCRIPT_DIR"
git add -A
if git diff --cached --quiet; then
  echo "변경사항 없음"
else
  git commit -m "sync claude config $(date +%Y-%m-%d_%H:%M)"
  git push
  echo "=== Push 완료 ==="
fi
