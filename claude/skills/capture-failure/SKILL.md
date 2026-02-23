---
name: capture-failure
description: 실패/예상외 동작 발견 시 해당 도메인의 skill 파일에 pitfall로 기록. 같은 실수 반복 방지.
version: 1.2.0
---

# Capture Failure → Skill Update

실패한 시도나 예상외 동작을 발견하면 해당 도메인의 pitfall skill에 기록하여 재발을 방지한다.

## When to Activate

- 도구 실행이 에러를 반환했을 때
- 코드가 예상과 다르게 동작했을 때 (성공했지만 결과가 틀림)
- 시도한 접근법이 작동하지 않아 다른 방법으로 우회했을 때
- API 제한사항, 버그, 미문서화 동작을 발견했을 때
- 이전에 기록된 pitfall 덕분에 실수를 피했지만 새로운 변형을 발견했을 때

## 기록하지 않을 것

- 단순 오타나 사용자 실수 (재현 불가)
- 일회성 환경 문제 (네트워크, 권한 등)
- 이미 기록된 pitfall과 동일한 내용

## Procedure

### 1. 실패 분석

다음을 정리:
- **뭘 시도했나** (코드/명령)
- **어떻게 실패했나** (에러 메시지, 잘못된 결과)
- **원인이 뭔가** (API 제한, 버전 차이, 미문서화 동작)
- **해결책은 뭔가** (올바른 코드/우회법)

### 2. 대상 skill 결정

도메인별 매핑:
| 도메인 | Skill |
|--------|-------|
| UE Python API (`unreal.*`, `execute_python`) | `ue-python-pitfalls` |
| (향후 추가) | ... |

**해당 도메인의 pitfall skill이 없으면 새로 생성한다.**
- 위치: `~/.claude/skills/{domain}-pitfalls/SKILL.md`
- `ue-python-pitfalls`와 동일한 형식 사용
- 이 테이블에 새 도메인 매핑 추가

### 3. Pitfall 엔트리 작성

기존 skill의 마지막 번호 다음으로 추가. 형식:

```markdown
### N. 제목 (간결하게)

설명 1줄.

\```python
# WRONG
실패한 코드

# CORRECT
올바른 코드
\```
```

규칙:
- 제목은 현상 기반 (예: "Rotator 생성자 순서", "load_asset 루프 크래시")
- WRONG/CORRECT 쌍 필수 (코드가 아닌 경우 Before/After)
- 불필요한 설명 최소화
- 기존 엔트리와 중복 시 기존 엔트리에 보충

### 4. 재구조화 필요성 체크

엔트리 추가 후, 대상 skill의 엔트리 수를 확인:
- **20개 초과** → `[capture-failure] ue-python-pitfalls 엔트리 N개. /reorganize-pitfalls 실행을 권장합니다.`

### 5. 사용자에게 보고

업데이트 후 한 줄로:
```
[capture-failure] ue-python-pitfalls #13 추가: "제목"
```

새 skill 생성 시:
```
[capture-failure] 새 skill 생성: git-pitfalls #1 "제목"
```
