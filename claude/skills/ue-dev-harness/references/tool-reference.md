# 도구 레퍼런스

> skill.md에서 참조. 검증/구현에 사용할 MCP 도구와 선택 기준.

## Evaluator 도구 선택

| 검증 대상 | 도구 | 언제 사용 |
|-----------|------|-----------|
| 에셋 프로퍼티, CDO 값, 클래스 구조 | `execute_python` | 에디터 타임 확인 |
| BP 노드 연결, 그래프 구조 | `get_blueprint_graph` | BP 로직 수정 시 |
| AnimBP 노드 연결, dead node | `analyze_animgraph` | 애니메이션 작업 시 |
| 런타임 상태, 게임플레이 로직 | `play_in_editor` → `pie_*` 시리즈 | 에디터 타임 불가 |
| 공간/충돌 | `line_trace` | 물리, 배치 |
| 에셋 무결성 | `validate_assets` | 에셋 수정 후 항상 |
| 참조 관계 | `get_asset_references` | 에셋 생성/이동/삭제 |
| 머티리얼 노드 구조 | `get_material_expressions` | 머티리얼 수정 시 |
| 메쉬 데이터 (UV, 버텍스, 섹션) | `execute_python` | 메쉬 파이프라인 |
| 콘솔 명령 결과 | `pie_execute_command` | stat, 디버그 명령 |

## Generator 도구 선택

**에셋 생성/수정:**
- `execute_python` — 범용 UE Python (가장 유연)
- `create_blueprint_with_components` — BP + 컴포넌트
- `add_blueprint_node` / `connect_blueprint_pins` — BP 그래프 로직
- `create_material` / `add_material_expression` / `connect_material_nodes` — 머티리얼
- `create_data_asset` — DataAsset
- `spawn_actor` / `set_property` — 레벨 배치

**코드 수정:**
- 소스 파일 직접 Edit — C++ / Python
- `save_asset` — 에셋 저장

## 테스트 코드 공통 패턴

```python
import unreal
errors = []
def check(cond, ac, msg):
    if not cond: errors.append(f'FAIL {ac}: {msg}')

# ... 검증 코드 ...

if errors:
    for e in errors: unreal.log_error(e)
    raise Exception(f'{len(errors)} failed: ' + '; '.join(errors))
unreal.log('All tests passed')
```

**필수 규칙:**
- UObject 비교: `is None` / `is not None` (ue-python-pitfalls #2)
- 실패 메시지: `f'expected {expected}, got {actual}'`
- 부작용 최소화: 프로젝트 상태 변경 시 원복
- 경계값: 0, max, null, 빈 컨테이너
