---
name: pbb-cook-and-pack
description: PBB 에셋을 CookAndPack하여 패키지 테스트용 pak 파일을 생성한다.
version: 1.0.0
user_invocable: true
---

# PBB CookAndPack

특정 에셋만 쿡+패킹하여 패키지 테스트용 pak 파일을 생성한다.

## Arguments

- `<assets>` — 쿡할 에셋 경로 (Content 기준 상대경로, `.uasset` 확장자 포함). 여러 개는 `+`로 구분.

예시: `/pbb-cook-and-pack Characters/PMC/Animation/Rig_Hand_IK.uasset+Characters/Hero/Default/Hero_TPP/Rig_AO.uasset`

## Procedure

### 1. 실행

```bash
cd "H:/PBB/P2_taewoo_game_dev"
MSYS_NO_PATHCONV=1 Engine/Build/BatchFiles/RunUAT.bat CookAndPackAssets \
  -project="H:/PBB/P2_taewoo_game_dev/Game/Game.uproject" \
  -TargetPlatform=Win64 \
  "-TargetAssets=<assets>"
```

### 주의사항

- **경로 형식**: Content 폴더 기준 상대 경로 + `.uasset` 확장자 필수
  - O: `Characters/PMC/Animation/Rig_Hand_IK.uasset`
  - X: `/Game/Characters/PMC/Animation/Rig_Hand_IK`
- **MSYS_NO_PATHCONV=1** 필수: Git Bash가 `/`로 시작하는 경로를 `C:/Program Files/Git/...`로 변환하는 것을 방지
- **UnrealPak.exe** 필요: 없으면 `Engine/Build/BatchFiles/Build.bat UnrealPak Win64 Development`로 빌드
- **에디터 실행 중**: MCPBridge 포트 충돌로 쿡 프로세스가 ExitCode=1을 반환하여 실패할 수 있음. **에디터를 닫고 실행하는 것이 안전**
- **`-CookAndPackDir`**: 지정하면 타임스탬프 이름(`{날짜}_PakOrder.pak` + `.sig`)으로 해당 폴더에 직접 출력됨. CompileBuild Paks 폴더를 직접 지정하면 편리

### 2. 결과 및 pak 배포

- `-CookAndPackDir` 미지정 시: `Game/Saved/StagedBuilds/WindowsClient/Game/Content/Paks/Game-WindowsClient.pak`
- `-CookAndPackDir` 지정 시: 해당 폴더에 `{날짜}_PakOrder.pak` + `.sig` 생성

### pak 우선순위 (GetPakOrderFromPakFilePath)

| 파일명 패턴 | 우선순위 | 설명 |
|------------|---------|------|
| `*_PakOrder.pak` | 99999 | **최고 우선순위** — 다른 모든 pak을 덮어씀 |
| `{ProjectName}-*.pak` | 4 | 게임 메인 pak (예: `Game-WindowsClient.pak`) |
| Content 디렉토리 내 기타 pak | 3 | |
| Engine Content 내 pak | 2 | |
| Saved 디렉토리 내 pak | 1 | |
| 기타 | 0 | 알파벳 순서와 무관 |

**pak 파일명은 반드시 `_PakOrder.pak`으로 끝나야** 기존 pak을 덮어쓸 수 있음.
- 컨텐츠 내용을 반영하도록 15자 이내로 작명 (예: `ControlRigOpt_PakOrder.pak`)
- `.sig` 파일도 같은 이름으로 함께 배포 필수

### 3. 결과 보고

- 성공/실패 여부
- pak 파일 크기
- 쿠킹된 에셋 수
