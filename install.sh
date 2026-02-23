#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "=== Claude Code 설정 배포 ==="

mkdir -p "$CLAUDE_DIR"/{commands,skills}

cp "$SCRIPT_DIR/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "[OK] CLAUDE.md"

cp "$SCRIPT_DIR/claude/settings.json" "$CLAUDE_DIR/settings.json"
echo "[OK] settings.json"

cp "$SCRIPT_DIR/claude/commands/"* "$CLAUDE_DIR/commands/" 2>/dev/null && echo "[OK] commands" || echo "[SKIP] commands"

cp -r "$SCRIPT_DIR/claude/skills/"* "$CLAUDE_DIR/skills/" 2>/dev/null && echo "[OK] skills" || echo "[SKIP] skills"

echo ""
echo "=== MCP 서버 설정 ==="
echo "MCP 서버는 경로가 머신마다 다르므로 수동 설정 필요."
echo "참고: claude/mcp-servers.json"
echo ""
echo "범용 MCP 서버 자동 추가:"
claude mcp add context7 -- npx -y @upstash/context7-mcp 2>/dev/null && echo "[OK] context7" || echo "[SKIP] context7"
claude mcp add codex-cli -- npx -y codex-mcp-server 2>/dev/null && echo "[OK] codex-cli" || echo "[SKIP] codex-cli"

echo ""
echo "=== 배포 완료 ==="
