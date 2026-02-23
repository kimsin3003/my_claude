#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

cp "$CLAUDE_DIR/CLAUDE.md" "$SCRIPT_DIR/claude/CLAUDE.md"
cp "$CLAUDE_DIR/settings.json" "$SCRIPT_DIR/claude/settings.json"
cp "$CLAUDE_DIR/commands/"*.md "$SCRIPT_DIR/claude/commands/" 2>/dev/null || true
rm -rf "$SCRIPT_DIR/claude/skills/"*
cp -r "$CLAUDE_DIR/skills/"* "$SCRIPT_DIR/claude/skills/" 2>/dev/null || true
cp ~/WorkHistory/context/writing-guide.md "$SCRIPT_DIR/context/" 2>/dev/null || true

cd "$SCRIPT_DIR"
git add -A
if git diff --cached --quiet; then
  echo "no changes"
else
  git commit -m "sync $(date +%Y-%m-%d_%H:%M)"
  git push
fi
