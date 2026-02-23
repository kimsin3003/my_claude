# Xbox Series 디버깅 환경 설정

Xbox Series 패키지를 사용하여 Visual Studio 디버깅 환경을 설정합니다.

## 필수 인자
- $ARGUMENTS: Xbox 패키지 경로 (예: F:\builds\trunk\2026.1.15.2)

## 설정 단계

### 1. 패키지 경로 확인
제공된 패키지 경로에서 XboxSeries 폴더 존재 여부를 확인합니다.

### 2. TslGame.vcxproj.user 설정
`Tsl/Intermediate/ProjectFiles/TslGame.vcxproj.user` 파일에 Xbox Series 디버깅 설정을 추가합니다:

```xml
<!-- Xbox Series Debug Settings -->
<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Development_Game|Gaming.Xbox.Scarlett.x64'">
  <DebuggerFlavor>XboxGamingVCppDebugger</DebuggerFlavor>
  <LocalDebuggerCommandArguments>${ServerIP} -nosteam -noeos -Messaging</LocalDebuggerCommandArguments>
</PropertyGroup>
```

ServerIP는 사용자 PC의 IP 주소를 `ipconfig` 명령으로 확인하여 Xbox devkit과 같은 네트워크 대역의 IP를 사용합니다.

### 3. 심볼릭 링크 설정
Loose 폴더에 패키지의 TslGame 폴더를 junction으로 연결합니다:

```powershell
# 기존 TslGame 폴더 삭제 (있는 경우)
Remove-Item -Recurse -Force "Tsl\Saved\XboxSeries\Layout\Image\Loose\TslGame"

# Junction 생성
New-Item -ItemType Junction -Path "Tsl\Saved\XboxSeries\Layout\Image\Loose\TslGame" -Target "${패키지경로}\XboxSeries\TslGame"
```

### 4. NMake Output 설정 (수동)
Visual Studio에서 TslGame 프로젝트 Property Page를 열고:
- NMake → Output 경로를 다음으로 변경:
  `..\..\Saved\XboxSeries\Layout\Image\Loose\TslGame\Binaries\XboxSeries\TslGame.exe`

## 설정 확인
- Xbox devkit IP (RemoteAddress)가 올바른지 확인
- Loose 폴더의 TslGame이 junction 링크인지 확인
- Visual Studio에서 Platform을 `Gaming.Xbox.Scarlett.x64`로 선택 가능한지 확인

## 실행 지침
위 단계를 순서대로 수행하여 Xbox 디버깅 환경을 구성하세요.
