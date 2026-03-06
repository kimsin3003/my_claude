---
name: plugin-cache-pitfalls
description: Claude Code 커스텀 마켓플레이스 플러그인 .mcp.json 수정 시 캐시 동기화 함정 자동 감지 및 회피. 플러그인 MCP 설정 변경 시 활성화.
version: 1.0.0
---

# Claude Code Plugin Cache Pitfalls

커스텀 마켓플레이스 플러그인의 `.mcp.json`을 수정할 때 반드시 캐시도 함께 수정해야 함.

## When to Activate

- 커스텀 마켓플레이스 플러그인의 `.mcp.json` 수정 시
- 플러그인 MCP 서버가 연결되지 않는 문제 디버깅 시
- `/mcp`에서 Plugin은 보이지만 MCP connected가 안 나올 때

## Bug: 플러그인 캐시가 소스와 동기화되지 않음

Claude Code는 플러그인 소스가 아닌 **캐시**에서 `.mcp.json`을 읽는다.
소스를 수정해도 캐시가 자동 갱신되지 않는 버그가 있다. (GitHub Issue #13543)

### 경로

- **소스**: `~/.claude/plugins/custom-mcp-marketplace/plugins/<name>/.mcp.json`
- **캐시**: `~/.claude/plugins/cache/taewoo-custom/<name>/<version>/.mcp.json`

### 수정 방법

```bash
# 반드시 소스와 캐시 둘 다 수정해야 한다
# 소스만 수정하면 캐시의 옛 설정이 계속 사용됨
```

### 진단 방법

플러그인 MCP가 안 될 때:

1. 캐시의 `.mcp.json` 내용 확인
2. 소스의 `.mcp.json` 내용과 비교
3. 불일치하면 캐시를 소스와 동일하게 수정
4. Claude Code 재시작

### 지원되는 MCP 타입

플러그인 `.mcp.json`에서 사용 가능한 타입:

- `"type": "sse"` + `"url"` — SSE 방식 (검증됨)
- `"type": "http"` + `"url"` — Streamable HTTP 방식 (테스트 필요)
- `"command"` + `"args"` — stdio 방식 (검증됨)
- ~~`"type": "streamable-http"`~~ — 지원하지 않는 타입, 사용 금지
