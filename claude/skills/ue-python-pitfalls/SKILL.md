---
name: ue-python-pitfalls
description: UE5 Python API 함정 자동 감지 및 회피. execute_python 또는 UE Python 코드 작성 시 활성화.
version: 1.1.0
---

# UE5 Python API Pitfalls

UE5 (특히 5.6) Python API의 알려진 함정들을 코드 작성 시 자동 회피.

## When to Activate

- `execute_python` MCP 도구 사용 시
- UE Python 코드를 작성하거나 리뷰할 때
- `unreal.` API 호출이 포함된 코드 생성 시

## Pitfalls

### 1. Rotator 생성자 순서 (C++ ≠ Python)

```
C++:    FRotator(Pitch, Yaw, Roll)
Python: unreal.Rotator(Roll, Pitch, Yaw)
```

```python
# WRONG
rot = unreal.Rotator(90, 0, 0)  # Pitch 90이 아님! Roll 90임

# CORRECT
rot = unreal.Rotator(roll, pitch, yaw)
```

CSS 캐릭터 카메라 바라보기: `unreal.Rotator(0, 0, cam_rot.yaw + 90)` (+90은 메시 오프셋)

### 2. UObject Falsiness

UObject는 valid해도 `bool()` 평가 시 falsy일 수 있음.

```python
# WRONG
if not actor:
    print("없음")  # valid 액터인데도 진입할 수 있음

# CORRECT
if actor is None:
    print("없음")
```

**모든 UObject 비교는 `is None` / `is not None` 사용.**

### 3. line_trace_single 반환값 (UE 5.6)

```python
# WRONG (이전 버전 방식)
hit, result = system_lib.line_trace_single(...)

# WRONG
hr.get_editor_property('blocking_hit')  # "property not found"

# CORRECT
hr = system_lib.line_trace_single(world, start, end,
    trace_channel=unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
    trace_complex=True, actors_to_ignore=[],
    draw_debug_type=unreal.DrawDebugTrace.NONE,
    ignore_self=False)
t = hr.to_tuple()
# t[0]=blocking_hit, t[3]=distance, t[4]=location,
# t[5]=impact_point, t[7]=impact_normal,
# t[9]=hit_actor, t[10]=hit_component
```

**주의**: `actors_to_ignore`에 실제 액터 전달 시 None 반환 버그. 빈 배열 `[]` 전달 후 결과에서 self-hit 필터링.

### 4. Material.expressions 접근 불가

```python
# WRONG
mat.get_editor_property('expressions')  # protected property 에러

# CORRECT
mel = unreal.MaterialEditingLibrary
count = mel.get_num_material_expressions(mat)
node = mel.get_material_property_input_node(mat, prop)
```

### 5. connect_material_expressions (UE 5.6)

```python
# WRONG (5.6에서 제거됨)
mel.connect_material_expressions_in_function(...)

# CORRECT (MF 내부에서도 동작)
mel.connect_material_expressions(from_expr, from_output, to_expr, to_input)
```

### 6. Material 연결 후 modify() 필수

`connect_material_expressions()` 후 `save_asset()`만 호출하면 에디터 재시작 시 연결 유실.

```python
# 연결 후 반드시:
for obj in unreal.ObjectIterator(unreal.MaterialExpression):
    if obj.get_outer() and obj.get_outer().get_name() == target_name:
        obj.modify()
material_or_function.modify()
el.save_asset(path, only_if_is_dirty=False)
```

### 7. RegisterComponent Python 미노출

`RegisterComponent()`, `AddComponentByClass()`, `FinishAddComponent()` 전부 Python 미노출.

**해결책 (우선순위)**:
1. 기존 C++ 액터 사용 (예: `CharacterSkinSystemPreviewActor`)
2. Blueprint 에셋에 컴포넌트 포함 후 spawn
3. C++ BPFunctionLibrary 래퍼 작성

```python
# CSS 프리뷰는 이걸 사용:
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor = eas.spawn_actor_from_class(
    unreal.CharacterSkinSystemPreviewActor, location, rotation)
```

### 8. load_asset 루프 크래시

```python
# WRONG — 에디터 크래시 가능
for path in paths:
    asset = el.load_asset(path)

# CORRECT
for path in paths:
    if el.does_asset_exist(path):
        pass  # 존재 확인만
```

### 9. screenshot_dir 없음

```python
# WRONG
unreal.Paths.screenshot_dir()  # AttributeError

# CORRECT
unreal.Paths.project_saved_dir() + 'Screenshots/'
```

### 10. ObjectIterator Stale 객체

노드 생성 직후 ObjectIterator가 stale 객체를 반환할 수 있음.

```python
# 생성 시 고유 좌표 지정
mel.create_material_expression(mat, unreal.MaterialExpressionAdd, x=500, y=300)

# (x, y) 좌표를 키로 식별
for obj in unreal.ObjectIterator(unreal.MaterialExpression):
    if obj.material_expression_editor_x == 500 and obj.material_expression_editor_y == 300:
        target = obj
```

### 11. duplicate_selected_actors → None

```python
# WRONG (성공해도 None 반환)
new_actors = eas.duplicate_selected_actors(world)

# CORRECT (새 액터 반환됨)
new_actor = eas.duplicate_actor(actor, world)
```

### 12. CustomInput 첫 번째 이름 변경 불가

```python
# WRONG — 첫 번째 input 이름 변경 안됨
custom.set_editor_property('input_name', 'NewName')

# CORRECT — 전체 배열 교체
new_inputs = []
for name in ['Input1', 'Input2']:
    ci = unreal.CustomInput()
    ci.import_text('(InputName="' + name + '")')
    new_inputs.append(ci)
custom.set_editor_property('inputs', new_inputs)
```

### 13. AnimBP 노드 존재 ≠ 연결됨

AnimGraph에서 `find_object`나 `ObjectIterator`로 노드를 찾아도, 실제로 Root에 연결되어 평가되는지는 별개.
**실 사례**: ABP_Hero_TPP에서 PoseDriver 44개 존재했으나 T3D BFS로 확인하니 **6개만 연결**, 38개는 미연결(비실행).

```python
# WRONG - 노드 존재만 확인 (ObjectIterator도 마찬가지)
obj = unreal.find_object(None, f"{graph_path}.AnimGraphNode_PoseDriver_0")
if obj:
    print("사용됨")  # 미연결 노드일 수 있음!

# CORRECT - T3D Export + Pin LinkedTo BFS (MCPBridge 불필요)
task = unreal.AssetExportTask()
task.set_editor_property('object', animblueprint)
task.set_editor_property('filename', output_path)  # .T3D
task.set_editor_property('automated', True)
task.set_editor_property('prompt', False)
unreal.Exporter.run_asset_export_task(task)
# T3D 텍스트 파싱 → Pin LinkedTo 추출 → Root부터 BFS → 연결 노드만 수집
```

**검증 방법**: T3D 텍스트에서 각 노드의 `CustomProperties Pin` 라인 파싱, `LinkedTo(AnimGraphNode_XXX ...)` 필드로 연결 관계 추출, Root(Output Pose)부터 BFS 탐색.

**에셋 분석 시 반드시 연결 상태를 검증할 것.** 미연결 노드는 컴파일에서 제외되므로 성능 영향 없음.

### 14. EdGraph.Nodes protected 접근 불가

```python
# WRONG
anim_graph.get_editor_property('nodes')  # "protected and cannot be read"

# CORRECT - find_object로 개별 노드 탐색
for i in range(30):
    obj = unreal.find_object(None, f"{graph_path}.AnimGraphNode_Type_{i}")
```

## Remote Control 설정 참고

```ini
# Config/DefaultRemoteControl.ini
[/Script/RemoteControlCommon.RemoteControlSettings]
bEnableRemotePythonExecution=True
RemoteControlHttpServerPort=30030
RemoteControlWebSocketServerPort=30031
```

- HTTP/WebSocket 포트가 **절대 겹치면 안됨**
- `bEnableRemotePythonExecution=True` 없으면 Python 실행 차단됨
