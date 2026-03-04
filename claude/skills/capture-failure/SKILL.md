---
name: capture-failure
description: "TRIGGER: 어떤 시도든 실패/예상외 동작 발생 후 다른 방법으로 우회 성공했을 때 즉시 실행. 실패→우회 패턴 감지 시 자동 기록."
version: 1.3.0
---

# Capture Failure → Pitfall 기록

## CRITICAL RULE

> **에러 발생 → 우회/수정으로 해결 = 반드시 이 skill 실행**
> 사용자 요청을 기다리지 말고, 우회 성공 직후 즉시 기록할 것.

## 트리거 패턴 (하나라도 해당되면 실행)

1. **에러→우회**: 도구/명령이 에러 반환 → 다른 방법으로 성공
2. **예상외 결과**: 코드가 성공했지만 결과가 틀림 → 수정
3. **API 함정 발견**: 미문서화 동작, 버전 차이, 플랫폼 차이
4. **pitfall 변형**: 기존 pitfall의 새로운 변형 발견

## 기록하지 않을 것

- 단순 오타나 사용자 실수 (재현 불가)
- 일회성 환경 문제 (네트워크 끊김, 일시적 권한 등)
- 이미 기록된 pitfall과 동일한 내용

## Procedure

### 1. 실패 분석 (간결하게)

- **시도**: 뭘 했나
- **실패**: 어떤 에러/잘못된 결과
- **원인**: 왜 실패했나
- **해결**: 올바른 방법

### 2. 대상 skill 결정

| 도메인 | Skill |
|--------|-------|
| UE Python API (`unreal.*`, `execute_python`) | `ue-python-pitfalls` |
| Git Bash / MSYS2 on Windows (`/옵션`, 경로 변환) | `git-bash-pitfalls` |

**매핑에 없는 도메인 → 새 skill 생성:**
- 위치: `~/.claude/skills/{domain}-pitfalls/skill.md`
- 기존 pitfall skill과 동일한 형식 사용
- 이 테이블에 새 매핑 추가

### 3. Pitfall 엔트리 추가

기존 skill의 마지막 번호 다음으로:

```markdown
### N. 제목 (현상 기반, 간결하게)

설명 1줄.

\```
# WRONG
실패한 코드/명령

# CORRECT
올바른 코드/명령
\```
```

규칙:
- WRONG/CORRECT 쌍 필수
- 기존 엔트리와 중복 시 보충만
- 20개 초과 시 `/reorganize-pitfalls` 권장

### 4. 보고

```
[capture-failure] {skill} #{N} 추가: "제목"
[capture-failure] 새 skill 생성: {skill} #1 "제목"
```
