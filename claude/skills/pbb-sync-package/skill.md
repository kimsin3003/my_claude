---
name: pbb-sync-package
description: PBB 패키지 최신화 — \\pubg-pds\PBB\Builds에서 최신 DEV game_dev 패키지를 찾아 복사하고, P4를 해당 리비전에 sync한다.
version: 1.0.0
user_invocable: true
---

# PBB Sync Package

`\\pubg-pds\PBB\Builds`에서 최신 CompileBuild를 찾아 로컬에 복사하고, P4 워크스페이스를 해당 리비전에 맞춘다.

## Arguments

- `<stream>` — 스트림 이름 (기본: `game_dev`). 예: `game`, `game_dev`, `exp_ctu_optimization`
- `<config>` — 빌드 설정 (기본: `DEV`). 예: `DEV`, `TEST`

## Procedure

### 1. 패키지 검색

빌드 네트워크 경로에서 해당 스트림/설정의 패키지 목록을 조회한다:

```bash
ls "//pubg-pds/PBB/Builds/" | grep "CompileBuild_<config>_<stream>_SEL" | sort -t'r' -k3 -n
```

패턴: `CompileBuild_<config>_<stream>_SEL<id>_r<CL>/`

### 2. 클라이언트/서버 검증

최신 패키지부터 역순으로, 클라+서버 바이너리 존재 여부 확인:
- Client: `WindowsClient/Game/Binaries/Win64/Client.exe`
- Server: `WindowsServer/Game/Binaries/Win64/Server.exe`

둘 다 있는 최신 패키지 선택.

### 3. 패키지 복사

```bash
robocopy '<네트워크경로>' 'C:\Users\taewoo\Desktop\<패키지명>' /E /MT:16 /NFL /NDL /NJH /NP
```

기존에 같은 이름 폴더가 있으면 복사 생략.

### 4. P4 Sync

패키지 이름에서 CL 번호 추출 (`r<CL>` 부분) 후 sync:

```
p4 sync //P2/<stream>/...@<CL>
```

### 5. basedir 업데이트 안내

pbb-build-run skill의 `-basedir` 경로가 새 패키지를 가리키도록 MEMORY.md의 basedir 경로를 업데이트한다.

새 basedir: `C:\Users\taewoo\Desktop\<패키지명>\WindowsClient\Game\Binaries\Win64`

### 6. 빌드 (선택)

사용자가 빌드도 요청한 경우 `/pbb-build-run build` 실행.

### 7. 서버 실행 (선택)

사용자가 서버 실행을 요청한 경우:

```bash
cd "C:\Users\taewoo\Desktop\<패키지명>" && start Server.bat
```

### 8. 결과 보고

- 선택된 패키지: 이름, CL 번호
- 복사 상태
- P4 sync 상태
- basedir 경로 변경 여부
