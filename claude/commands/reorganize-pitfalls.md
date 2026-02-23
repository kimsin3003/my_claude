# Reorganize Pitfalls

`*-pitfalls` skill 파일들을 감사하고 재구조화한다.

## Procedure

### 1. 전체 스캔

`~/.claude/skills/*-pitfalls/SKILL.md` 전부 읽고 다음을 수집:
- skill별 엔트리 수
- 각 엔트리의 도메인 태그 (제목 + 내용 기반)

### 2. 문제 탐지

| 문제 | 기준 | 조치 |
|------|------|------|
| **비대화** | 엔트리 20개 초과 | 하위 도메인으로 분리 제안 |
| **중복** | 2개 이상 skill에 유사 내용 | 하나로 통합 제안 |
| **잘못된 분류** | 엔트리가 다른 skill 도메인에 더 적합 | 이동 제안 |
| **폐기** | 더 이상 유효하지 않은 pitfall (버전 업 등) | 삭제 제안 |
| **영세 skill** | 엔트리 2개 이하 + 6개월 이상 변경 없음 | 상위 skill에 흡수 제안 |

### 3. 재구조화 계획 출력

변경 사항을 테이블로 정리:
```
[재구조화 계획]
1. ue-python-pitfalls 분리 → ue-python-pitfalls (core API), ue-material-pitfalls (Material 관련)
2. git-pitfalls #3 → perforce-pitfalls로 이동 (P4 관련 내용)
3. ue-python-pitfalls #7 삭제 (UE 5.7에서 수정됨)
4. mcp-pitfalls 흡수 → ue-python-pitfalls (엔트리 1개, MCP 경유 Python)
```

### 4. 사용자 승인 후 실행

- 승인된 항목만 실행
- 분리 시: 새 skill 생성 + 엔트리 이동 + 번호 재정렬
- 통합 시: 대상 skill에 추가 + 원본에서 삭제
- 삭제 시: 엔트리 제거 + 번호 재정렬
- capture-failure의 도메인 매핑 테이블도 업데이트

### 5. 결과 보고

```
[reorganize-pitfalls] 완료
  분리: 1건 (ue-python-pitfalls → +ue-material-pitfalls)
  이동: 1건
  삭제: 1건
  흡수: 1건
  총 skill: 3개 → 3개
  총 엔트리: 45개 → 42개
```
