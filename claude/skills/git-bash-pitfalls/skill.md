---
name: git-bash-pitfalls
description: Git Bash (MSYS2) on Windows 함정 자동 감지 및 회피. bash 명령 실행 시 활성화.
version: 1.0.0
---

# Git Bash (MSYS2) on Windows Pitfalls

Git Bash 환경에서 Windows 명령 실행 시 알려진 함정들을 자동 회피.

## When to Activate

- Windows에서 Bash 도구로 명령 실행 시
- `/`로 시작하는 Windows 옵션 플래그 사용 시
- PowerShell/cmd 명령을 bash에서 호출할 때

## Pitfalls

### 1. MSYS Path Conversion — 슬래시 옵션이 경로로 변환됨

Git Bash(MSYS2)는 `/`로 시작하는 인수를 자동으로 Windows 경로로 변환함.

```bash
# WRONG — /PID가 'C:/Program Files/Git/PID'로 변환됨
taskkill /PID 12345 /F

# CORRECT — PowerShell로 우회
powershell -Command "Stop-Process -Id 12345 -Force"
```

영향받는 명령: `taskkill`, `net`, `sc`, `reg` 등 `/옵션` 형식 사용하는 모든 Windows CLI.

**우회법**: `MSYS_NO_PATHCONV=1 taskkill /PID 12345 /F` 또는 PowerShell 사용.
