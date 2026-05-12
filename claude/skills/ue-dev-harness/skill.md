---
name: ue-dev-harness
description: UE 개발 하네스. UE 관련 작업 시 활성화 — 기능 구현/수정, 크래시 분석, 최적화, 빌드/테스트 절차. 프로젝트별 빌드 커맨드/테스트 정보도 이 skill이 관리 (references/projects/).
version: 3.4.0
---

# UE Development Harness

3-Phase (계획→구현→검증) 구조로 UE 개발을 자율 수행.
상세 참조: `references/test-strategies.md`, `references/tool-reference.md`

## When to Activate

- **모든 언리얼 코드 관련 작업 시 자동 활성화** (구현, 수정, 분석, 디버깅, 최적화, 코드 질문 등)
- 사용자가 `/ue-dev-harness` 직접 호출 시

## 핵심 원칙

1. **완료 기준(AC) 먼저** — 구현 전에 "done"을 정의
2. **테스트 코드로 검증** — 자동화 가능한 것은 코드로
3. **실패 시 자동 재시도** — Evaluator 실패 → Generator 복귀 (최대 3회)
4. **모델이 잘 하는 건 가이드하지 않음** — 하네스는 모델이 혼자 못하는 부분만 보완
5. **상속 체인은 root와 leaf까지 끝까지 추적** — 코드 분석 시 클래스/virtual 메서드 동작을 추론할 때, 상속 체인의 모든 단계를 root(인터페이스/추상 베이스)와 leaf(final/구체)까지 빠짐없이 따라간다. "직계 부모만" 또는 "base 본문만" 보고 단정 금지. virtual 메서드는 `grep "::MethodName"`으로 base와 모든 derived의 override/정의를 찾고, 각 본문이 super를 호출하는지, 어떤 derived를 호출하는지 모두 확인. `ExecuteXxx`처럼 specialized 이름은 base의 template-method 패턴 신호 — "진짜 `Execute`는 어디"를 별도 grep으로 검증. Explore agent 보고서는 trust 후 그대로 인용 금지 — 결론에 의존하는 핵심 함수는 직접 cpp 펴서 verify.
6. **익명 namespace에 file-local helper 만들지 말 것** — cpp 파일 상단의 `namespace { ... }` 안에 file-scope static helper 함수를 새로 만들지 않는다. CSS/UE 코드 베이스 컨벤션에 어긋남. 대신 해당 클래스의 **private static 멤버 함수**로 둔다 (헤더에 선언, cpp에 정의). inline switch/loop로 본문에 직접 풀어쓰는 것도 OK. 한 번만 쓰이고 짧은 helper는 호출 지점에 inline. 클래스 외부에서 재사용이 명확히 필요한 경우에만 별도 utility 클래스/namespace를 고려하되, 새 namespace 신설은 신중히.
7. **독립 작업은 N개 agent를 동시에 invoke해서 진짜 병렬화** — 같은 패턴의 독립 작업(파일 N≥3개에 동일한 변경, 또는 독립적인 N개 탐색)은 단일 메시지 안에서 **N개 Agent tool을 동시에 invoke**한다. 한 agent에 N개 파일을 위임하면 그 agent 내부에서 sequential 처리라 실질 병렬 X. **단일 메시지 multiple Agent invocations**가 true parallel. main thread sequential Edit은 N=2 이하인 경우만. 패턴 신호: "독립 N개 작업"이 보이면 즉시 N agent 분할.
8. **주석은 거의 쓰지 않는다** — 기본값은 "주석 없음". 코드/함수 이름으로 이해할 수 있는 곳에는 절대 쓰지 않는다. WHAT 설명(코드가 무엇을 하는지) 금지. WHY 주석도 "**히스토리상 이 코드/순서가 반드시 있어야 한다**" 같이 외부 컨텍스트가 없으면 알 수 없는 강제 사항만 정당화된다. 추가 정당화 사례: workaround for specific bug, 숨겨진 invariant, 호출 순서 강제. 그 외("design rationale", "what this code does", "summary of approach")는 모두 PR 설명이나 commit 메시지로 옮긴다. **예외 — virtual 함수의 interface marker는 허용**: `// FGCObject`, `// FTickableGameObject`, `// ICharacterSkinPipeline` 같이 어느 인터페이스의 구현인지 표시하는 한 줄짜리 grouping marker는 가독성 위해 둘 수 있다. 클래스 docstring/long-form comment는 거의 항상 redundant — 핵심 design decision은 commit/PR에 두고 코드는 코드로만 말한다.

---

## Phase 0: 규모 판별

모든 작업에 전체 사이클을 돌릴 필요 없음.

| 규모 | 기준 | 적용 |
|------|------|------|
| **경량** | 1~2파일, 명확한 수정, 리스크 낮음 | AC 간단히 정의 → 바로 구현 → 테스트, 사용자 승인 생략 가능 |
| **중량** | 3파일+, 시스템 영향, 리스크 있음 | 전체 Phase 1→2→3 수행, 사용자 승인 필수 |

판단이 애매하면 중량으로.

---

## Phase 1: Planner

### 프로젝트 컨텍스트 로드
작업 대상 프로젝트를 판별하고 `references/projects/{프로젝트}.md`를 읽는다.
빌드 커맨드, 테스트 절차, 프로젝트 고유 주의사항이 포함되어 있다.
해당 프로젝트 파일이 없으면 빈 파일을 생성한다.

### 작업 유형 판별
- "크래시", "버그", "에러", 콜스택 → **모드 A: 크래시 분석**
- "느리다", "최적화", "성능", 프로파일링 데이터 → **모드 B: 최적화**
- 그 외 → **모드 C: 신규 피쳐**
- 어디에도 안 맞음 → **자가진화** (하단 참조)

---

### 모드 A: 크래시 분석/수정

> 원인 분석이 작업의 본체. "왜?"를 먼저 답한 후에야 수정.

1. **재현 조건 정리** — 맵, 상태, 시퀀스, 빌드 타입에서 추출
2. **콜스택 → 코드 추적** — 크래시 지점부터 변수 레벨 추적 (함수명만 보고 판단 금지)
3. **원인 가설 & 검증** — 가설이 재현 조건과 정상 케이스 모두 설명하는지 확인. 못하면 코드로 복귀.
4. **AC 정의** — 재현 조건에서 정상 동작 + 기존 동작 보존 + 경계 조건 안전
5. **사용자 승인** — 원인 분석 + 수정 계획

### 모드 B: 최적화

> 숫자 없는 최적화는 최적화가 아님. Baseline 먼저.

1. **병목 식별** — 프로파일링 데이터 파싱 또는 직접 측정 방법 제안
2. **baseline 수집** — 수정 전 동작 값 + 성능 수치 기록
3. **전략 수립** — 수정 방법, 기대 효과, 리스크 (스레드 안전성 등)
4. **AC 정의** — 동작 보존 (baseline 대비) + 성능 개선 수치 + 스레드 안전성
5. **사용자 승인** — baseline + 전략

### 모드 C: 신규 피쳐

1. **컨텍스트 수집** — 관련 에셋/코드 탐색, 변수 레벨까지 확인
2. **작업 분해** — 구현 단위 분리, 의존 관계 정리
3. **AC 정의** — 각 단위별 검증 가능한 조건
4. **사용자 승인** — 계획 + AC

### Planner 출력
- 작업 목록 (TaskCreate 등록)
- AC 목록
- 모드 B: baseline 데이터

---

## Phase 2: Generator

Planner 계획에 따라 구현. 도구 상세: `references/tool-reference.md`

### C++ 수정 시 빌드 처리

C++ 수정 후 에디터 반영 필수. **직접 빌드를 실행하고, 결과를 확인한다. 사용자에게 빌드를 요청하지 않는다.**

1. **에디터 실행 중 → 라이브 코딩 우선** (`LiveCoding.Compile` 콘솔 커맨드)
   - 라이브 코딩 후 **반드시 프로젝트 로그(`Saved/Logs/*.log`)에서 성공/실패 확인**
   - `LogLiveCoding: Error: Live coding failed` → 라이브 코딩 실패. 헤더 수정 등이 원인.
   - 라이브 코딩 실패 시 에디터 종료 → 증분 빌드(Build.bat) → 에디터 재시작
2. **에디터 미실행 → 증분 빌드** (`references/projects/{프로젝트}.md`의 빌드 커맨드)
3. **절대 clean/full rebuild 하지 않는다.**
4. 빌드 성공 확인 후 Phase 3 진행. 실패 시 에러 분석 → Generator로 복귀.
5. **헤더(.h) 수정 시** 사용자에게 허락을 받은 후 수정 (컴파일 시간이 크므로, 승인 없이 수정 금지)
6. **에디터 실행 시 항상 `-unattended -CrashForUAT` 플래그 추가** — 크래시 dialog 없이 즉시 종료, exit code로 감지 가능

빌드 불필요한 경우 (에셋만 수정, Python만 수정) → 바로 Phase 3.

### 규칙
- 한 구현 단위 완료 후 바로 Phase 3으로 검증
- 검증 실패 시 이 Phase로 복귀
- ue-python-pitfalls 함정 회피 준수

---

## Phase 3: Evaluator

AC 기반으로 테스트 설계 → 코드 생성 → 실행 → 판정.
전략 상세: `references/test-strategies.md`

### 원칙: 모든 검증은 코드로

- **사용자에게 화면 확인을 요청하지 않는다** — 반드시 코드로 검증 가능한 방법을 고안
- 에디터 MCP 연결됨 → `execute_python`, `pie_*`, `validate_assets` 등 자동 테스트
- 에디터 MCP 미연결 → 에디터를 실행하거나, 테스트 가능한 환경을 직접 구축
- 코드 리뷰가 필요한 경우 → Codex와 함께 논의 (`/codex:rescue`)
- 각 AC에 최소 하나의 코드 기반 검증
- 검증 불가능한 AC → Planner로 돌아가 테스트 가능한 형태로 재정의
- 테스트 코드 패턴: `references/tool-reference.md` 참조

### 실패 시

```
실패 → 테스트 문제인지 구현 문제인지 판별
  → 테스트 문제: 테스트 수정
  → 구현 문제: Generator로 복귀
  → 최대 3회 반복
  → 3회 실패: 사용자에게 보고
```

---

## Phase 4: 완료

1. **사용자에게 결과 보고** — 무엇을 했고, 테스트 결과
2. **WorkHistory 기록** — `~/WorkHistory/topics/` 해당 프로젝트 폴더에 기록
   - 새로운 시스템 지식, 발견한 패턴/함정, 아키텍처 인사이트
   - 단순 코드 변경 내역은 기록 불필요 (git에 있으므로)

---

## 전체 흐름

```
[사용자 요청]
     │
     ▼
  Phase 0: 규모 판별
     │
     ├─ 경량 → AC 정의 → 구현 → 테스트 → 완료
     │
     └─ 중량 → Phase 1: Planner
                  │
                  ├─ 크래시 → 모드A (원인 분석 → 수정 계획)
                  ├─ 최적화 → 모드B (baseline → 전략)
                  ├─ 피쳐   → 모드C (설계 → 분해)
                  └─ 미분류 → 자가진화
                  │
                  ▼ 사용자 승인
               Phase 2: Generator
                  │ (C++ → 빌드 대기)
                  ▼
               Phase 3: Evaluator
                  │ (미연결 → 코드 리뷰)
                  │◄── 실패 시 Phase 2 (최대 3회)
                  ▼ 통과
               Phase 4: 완료 + WorkHistory
```

---

## 자가진화: 하네스 업데이트

하네스가 현재 작업에 불충분하면 skill 자체를 업데이트.
**업데이트도 하네스 3-Phase를 통과한다.**

### 트리거
- 기존 모드에 매핑 안 됨 (새 모드 필요)
- 매핑은 되지만 절차/전략이 부족 (기존 모드 보강)
- 작업 중 발견한 교훈을 향후 재활용 가능 (교훈 반영)
- **프로젝트 빌드/테스트 정보 갱신** — 새 빌드 커맨드, 테스트 절차, 프로젝트 설정 발견 시 `references/projects/`에 반영

### 절차

1. **Planner** — 무엇이 부족한지 정의, 변경 초안, AC 작성, 사용자 승인
2. **Generator** — `skill.md` 또는 `references/*.md` Edit, version 올림
3. **Evaluator** — 파일 Re-read, 변경 완전성 + 기존 모드 영향 없음 확인

업데이트 완료 후 원래 작업을 (새/보강된) 모드로 수행.

---

## 주의사항

- **직접 할 수 있는 작업은 사용자에게 요청하지 않는다** (빌드, 에셋 저장, 테스트 실행 등)
- C++ 헤더 수정 → 사용자에게 사전 고지 (컴파일 시간), 그러나 빌드는 직접 실행
- PIE 크래시 → 즉시 중단, 원인 분석
- ue-python-pitfalls 규칙 적용 (테스트 코드 포함)
- TaskCreate/TaskUpdate로 진행 추적
- 프로젝트별 빌드/테스트 → `references/projects/` 참조
