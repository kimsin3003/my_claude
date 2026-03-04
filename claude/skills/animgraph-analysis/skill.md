---
name: animgraph-analysis
description: AnimBP/AnimGraph 구조 분석 방법론. AnimBP 분석, 최적화, 노드 조사 시 활성화.
version: 1.0.0
---

# AnimGraph Analysis Methodology

AnimBP 구조를 체계적으로 분석하는 방법론. T3D export 기반으로 C++ 플러그인 없이 동작.

## When to Activate

- AnimBP 구조 분석 요청 시
- AnimGraph 최적화 조사 시
- AnimBP 노드 연결 검증 시

## 핵심 원칙

**노드 존재 ≠ 노드 연결 ≠ 노드 실행**
- `ObjectIterator`로 찾은 노드가 실제 연결되어 있다고 가정하지 말 것
- 반드시 Pin LinkedTo로 연결 검증 후 BFS reachability 확인

## 분석 단계

### Phase 1: 노드 토폴로지 (AnimGraph 구조)

MCP `analyze_animgraph` 도구 사용:

```
analyze_animgraph(blueprint_path="/Game/path/to/ABP", graph="AnimGraph")
```

확인 사항:
- 연결된 노드 vs 미연결(dead) 노드 분류
- 고비용 노드 식별: ControlRig, PoseDriver, LayeredBoneBlend, SlopeWarping
- LOD Threshold 확인 (-1 = 항상 실행, 문제)
- available_graphs로 전체 그래프 목록 확인
- Sub-graph별 동일 분석 반복

### Phase 2: 함수/로직 노드 (EventGraph, TransitionRule)

T3D export에서 AnimGraphNode 외에 K2Node(Blueprint 로직)도 파싱:

```python
# T3D에서 K2Node 추출
# EventGraph: 매 틱 실행되는 BP 로직 (변수 계산, 조건 분기)
# TransitionRule: StateMachine 전환 조건 (매 프레임 평가)
# AnimNotify: 키프레임 이벤트
```

확인 사항:
- EventGraph의 틱 함수 복잡도
- TransitionRule 개수와 조건 복잡도
- 매 프레임 호출되는 Pure function 개수
- GameplayTag 쿼리 빈도

### Phase 3: C++ NativeUpdateAnimation

소스 코드 분석:
- `NativeUpdateAnimation` 내 게임스레드 연산 식별
- `NativeThreadSafeUpdateAnimation` 활용 여부
- Proxy 변수 캐싱 패턴 확인

### Phase 4: LinkedAnimLayer 내부

무기별/상태별 AnimLayer ABP의 내부 구조:
- 각 Layer ABP의 노드 수, 고비용 노드, LOD 설정
- 입력/출력 포즈 연결 구조

## T3D Export 방법

```python
import unreal, os, tempfile

bp = unreal.load_asset(bp_path)
export_file = os.path.join(tempfile.gettempdir(), 'mcp_abp_export.copy')
task = unreal.AssetExportTask()
task.set_editor_property('automated', True)
task.set_editor_property('object', bp)
task.set_editor_property('filename', export_file)
task.set_editor_property('prompt', False)
task.set_editor_property('replace_identical', True)
unreal.Exporter.run_asset_export_task(task)
```

### T3D 구조 핵심

- **2-pass 구조**: 전반부 forward declaration (Class= 있음), 후반부 properties (Class= 없음)
- **Pin 연결**: `CustomProperties Pin (PinName="..." Direction="..." LinkedTo=(NodeName GUID,))`
- **그래프 식별**: ExportPath에서 `BPName.BPName:GraphName` 패턴으로 소속 그래프 추출
- **노드 속성**: `Node=` 라인에 SourceBones, LODThreshold, ControlRigClass 등 포함

## 함정 (Pitfalls)

1. **ObjectIterator는 미연결 노드도 반환** — 반드시 핀 연결 검증 필요
2. **EdGraph.Nodes는 Python에서 protected** — `get_editor_property('nodes')` 실패, T3D 사용
3. **AnimGraphNode에 export_text() 없음** — UObject wrapper는 struct와 달리 export_text 미지원
4. **SaveCachedPose 간접 참조** — BFS에서 unreachable로 나오지만 UseCachedPose로 실제 사용됨
5. **같은 노드명이 다른 그래프에 존재** — 반드시 graph-qualified key 사용 (e.g. `AnimGraph::NodeName`)

## 최적화 체크리스트

- [ ] 고비용 노드(ControlRig, PoseDriver, BoneBlend, SlopeWarping) LOD 확인
- [ ] 미연결 노드 정리 대상 식별
- [ ] NativeThreadSafeUpdateAnimation 활용 여부
- [ ] EventGraph 틱 함수 복잡도
- [ ] TransitionRule 평가 비용
- [ ] LinkedAnimLayer 내부 구조
- [ ] GameplayTag 쿼리 캐싱 여부
