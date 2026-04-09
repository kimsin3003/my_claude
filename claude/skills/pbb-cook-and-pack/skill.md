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
- **에디터 실행 중**: 포트 충돌 경고가 나올 수 있으나 쿡 자체에는 영향 없음

### 2. 결과

- pak 파일: `Game/Saved/StagedBuilds/WindowsClient/Game/Content/Paks/Game-WindowsClient.pak`
- **pak 파일명**: 컨텐츠 내용을 반영하도록 15자 이내로 리네임할 것 (예: `ControlRigOpt.pak`, `CSSCacheOpt.pak`)
- CompileBuild의 `WindowsClient/Game/Content/Paks/` 또는 `WindowsServer/Game/Content/Paks/`에 복사하면 기존 pak보다 우선 로딩됨

### 3. 결과 보고

- 성공/실패 여부
- pak 파일 크기
- 쿠킹된 에셋 수
