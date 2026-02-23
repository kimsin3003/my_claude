# My Claude Code Configuration

Claude Code 설정 파일 백업 및 동기화 레포.

## 구조

```
claude/
├── CLAUDE.md           # 개인 지침 (전역)
├── settings.json       # Claude Code 설정 (hooks, permissions, model)
├── mcp-servers.json    # MCP 서버 설정 (참고용, 경로는 머신마다 다름)
├── commands/           # 커스텀 slash commands
├── skills/             # 커스텀 skills
└── scripts/            # 유틸리티 스크립트
```

## 새 머신에 배포

```bash
git clone https://github.com/kimsin3003/my_claude.git
cd my_claude
bash install.sh
```

## 동기화 (현재 머신 → 레포)

```bash
bash ~/my_claude/sync.sh
```
