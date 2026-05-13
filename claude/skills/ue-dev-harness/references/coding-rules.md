# Coding Conventions (Stop-hook 강제 점검 대상)

이 파일은 `check-coding-rules.js` Stop hook에 의해 코드 파일이 수정된 turn 종료 시점에 강제로 재로드된다. 본문이 길어도 OK — hook이 매번 다시 읽힌다.

수정한 모든 코드 파일(.cpp/.h/.hpp/.cc/.cs/.c)이 아래 항목을 만족하는지 점검하고, 위반이 있으면 수정한다.

---

## R1. 익명 namespace에 file-local helper 만들지 말 것

cpp 파일 상단의 `namespace { ... }` 안에 file-scope static helper 함수를 새로 만들지 않는다. CSS/UE 코드베이스 컨벤션 위반.

**대체 방법:**
- 해당 클래스의 **private static 멤버 함수**로 둔다 (헤더에 선언, cpp에 정의).
- inline switch/loop로 본문에 직접 풀어쓰는 것도 OK.
- 한 번만 쓰이고 짧은 helper는 호출 지점에 inline.
- 클래스 외부에서 재사용이 명확히 필요한 경우에만 별도 utility 클래스/namespace를 고려하되, 새 namespace 신설은 신중히.

**탐지:** cpp 파일 상단에 `namespace { ... }` 추가했는가? 그 안에 `static` 또는 일반 함수가 있는가?

---

## R2. Enumerate/Iterator 패턴·신규 template 함수 금지

함수 이름에 `Enumerate*`/`Iterate*`/`ForEach*` 같은 단어를 쓰지 않는다. Custom iterator, range adapter, yield-style 콜백 함수 신설 금지.

**컬렉션 반환:** 그냥 `TArray<T> GetXxx()` 또는 `TArray<T> CollectXxx()`로 통째 반환.

**신규 template 함수 작성 금지** (기존 코드의 template 사용·유지는 OK).

**호출자 측의 ranged for** (`for (auto& X : Container)`)는 언어 기본 문법이므로 허용.

**이유:** 단순·직관 API 선호. 디버깅·트레이싱 용이.

**탐지:**
- 함수 이름에 Enumerate/Iterate/ForEach가 있는가?
- 신규로 추가한 `template <...>` 함수가 있는가?
- callback parameter로 컬렉션을 yield하는 함수를 만들었는가?

---

## R3. 별도 helper 함수 신설은 보수적으로

호출 지점이 한 곳뿐이면 inline으로 본문에 펼치는 게 낫다.

**함수로 분리할 정당화 사유:**
- 여러 호출 사이트에서 재사용
- 본문이 길어 가독성이 inline 비용보다 더 큰 손상
- 명시적 추상화가 도메인 개념을 표현

**특히 한 줄짜리 위임 함수**(다른 함수에 인자만 넘기는)는 분리하지 말고 직접 호출.

**탐지:** 새로 추가한 private 멤버 함수가 1곳에서만 호출되는가? 그 본문이 5~10줄 이내인가? → inline 후보.

---

## R4. 멤버 변수로 helper 사이를 잇지 말 것

함수 A가 클래스 멤버에 데이터를 쓰고, 함수 B가 그 멤버를 읽기만 하며, A와 B가 한 흐름에서 1회씩 연속 호출된다면 — 그 멤버는 instance state가 아니라 **두 helper 사이의 임시 본드**다.

**대응:** 둘을 호출 지점에 inline하고 멤버를 지역 변수로 강등(또는 삭제).

**탐지 신호:**
- 멤버 필드가 한 함수에서 채워지고 즉시 다른 함수에서 소비되며, 다른 곳에선 안 읽힘
- Map/Array 멤버가 build-then-consume 단일 패턴으로만 쓰임
- 함수 이름이 `Map*`/`Build*`/`Collect*` + `Find*`/`Get*` 짝으로 등장 (생산자-소비자 분할)
- `void DoX(); void GetXResult();` 류 시그니처

**예외:**
- 같은 데이터를 여러 호출 사이트에서 재사용 (진짜 캐시)
- 멤버가 클래스 라이프타임 동안 의미를 갖는 진짜 state

---

## R5. 변수명을 과도하게 축약하지 않는다

단일 글자(`I`, `M`, `S`, `C`)나 의미 불명한 단축형(`Inst`, `Dup`, `Cmd` 단독) 금지.

**권장 풀네임:**
- `Dup` → `DupCommand` 또는 `DuplicatedCommand`
- `Inst` → `Instance`
- `Cmd` → `Command`
- `M` → `Modifier` / `Mapped` / `Matched` (맥락에 따라)
- `I` → `Instance` / `Item`
- `S` → `Section` / `Source` / `Surface`

**허용:**
- 루프 인덱스 `Idx` / `Index` / `i` (짧은 루프 한정) / `j`
- 수학적 의미 명확한 `x/y/z`, `r/g/b`

**이유:** 작성 시 1초 절약하려고 읽는 사람의 5초를 빼앗지 않는다.

**탐지:** ranged for / 람다 / 짧은 스코프 안에서 1~2글자 변수명을 만들었는가? Idx/Index 같은 컨벤션 외 단일글자는 풀네임으로.

---

## R6. 주석은 거의 쓰지 않는다

기본값은 "주석 없음".

**금지:**
- WHAT 설명(코드가 무엇을 하는지)
- 함수명/변수명으로 이해 가능한 곳의 주석
- "design rationale", "summary of approach" 류

**정당화되는 WHY 주석:**
- 히스토리상 이 코드/순서가 반드시 있어야 한다는 외부 컨텍스트
- workaround for specific bug
- 숨겨진 invariant, 호출 순서 강제

**예외 — 허용:**
- virtual 함수의 interface marker: `// FGCObject`, `// FTickableGameObject`, `// ICharacterSkinPipeline` 같은 한 줄 grouping marker

**언어:** 주석은 영어, 핵심만 간결하게, 인간 개발자가 작성한 것처럼.

---

## 점검 절차 (hook 발동 시)

1. 위 R1~R6을 모두 읽었는지 확인
2. 이 turn에서 수정한 각 코드 파일을 빠르게 훑으며 항목별 위반 여부 점검
3. 위반 발견 시 → Edit으로 즉시 수정
4. 위반 없으면 → "코딩 규칙 점검 완료"라고만 짧게 보고 후 종료
