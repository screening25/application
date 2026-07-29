# 시작 가이드

> **갱신됨 (2026-07-29)** — 1번 폴더 준비 단계는 완료됐다. 문서는 `screening25/application` 저장소의
> `sumuk/` 하위 폴더에 커밋돼 있다. 앱 이름·Bundle ID·Figma 파일 유무도 전부 확정됐으므로
> 아래 프롬프트는 그에 맞게 수정돼 있다.

## 1. 폴더 준비 — 완료됨

```bash
git clone <repo> && cd application/sumuk
```

```
sumuk/
├─ CLAUDE.md            프로젝트 규칙 + 확정 식별자
├─ SPEC.md              전체 명세 (Phase 0~17)
├─ PROGRESS.md          진행 상태 — 세션 시작 시 먼저 읽는다
├─ PHASE0_RUNBOOK.md    Phase 0 Mac 실행 절차서
└─ KICKOFF.md           이 파일
```

Xcode 프로젝트는 이 폴더 안에 생성한다 (`sumuk/Sumuk.xcodeproj`).

## 2. Figma MCP 연결

```bash
claude plugin install figma@claude-plugins-official
```

- Claude Code를 재시작한다
- `/plugin` → 오른쪽 방향키로 **Installed** 탭 → `figma` 선택 → Enter
- 브라우저가 열리면 **Allow access**
- 다시 `/plugin`으로 `figma`가 연결(초록)인지 확인

## 3. Claude Code 실행

```bash
cd <repo>/sumuk
claude
```

---

## 4. 첫 프롬프트 (그대로 붙여넣기)

사전 확인 4개 항목은 이미 답이 나왔으므로(`CLAUDE.md` "확정 사항") 곧바로 Phase 0을 실행한다.

```
CLAUDE.md, PROGRESS.md, PHASE0_RUNBOOK.md를 읽어줘.

앱 이름·Bundle ID·Figma 파일 유무·Apple Developer 계정은 이미 확정됐으니 다시 묻지 마.
PHASE0_RUNBOOK.md를 따라 Phase 0을 실행해줘.
- Xcode 프로젝트 생성 시 Storage는 반드시 None (이유는 런북에 있음)
- Capability는 런북의 타깃별 표를 그대로 따를 것
- 런북 끝의 완료 판정 체크리스트 12개를 하나씩 짚어가며 검증하고,
  각 항목을 "무엇을 어떻게 확인했는지"와 함께 보고해줘

Phase 0이 끝나기 전까지 Phase 1 이후의 코드는 절대 작성하지 마.
```

## 5. Phase 전환 프롬프트

각 Phase가 끝날 때마다 사용한다.

```
Phase {N} 완료 조건을 하나씩 짚어가며 실제로 충족했는지 검증해줘.
미충족 항목이 있으면 그것부터 마무리해.
전부 충족했으면 PROGRESS.md를 갱신하고 [P{N}] 커밋한 뒤,
Phase {N+1}의 작업 목록을 보여주고 내 승인을 받고 시작해.
```

## 6. Figma 작업 프롬프트 (Phase 1)

**디자인 파일은 없는 것으로 확정됐다.** 아래 프롬프트를 쓴다 (기존 파일에서 읽어오는 경로는 해당 없음).

```
Figma에 새 파일을 만들고 SPEC.md Phase 1의 토큰 체계를 캔버스에 구성해줘.
- 페이지: Foundations / Components / Screens
- 색상·간격·radius는 반드시 Figma Variables로 정의 (로컬 스타일 금지 — 이름이 유실된다)
- 색상은 SPEC 1.2의 먹/잉크 컨셉: ink, ink/secondary, paper, surface, accent, link, divider
  라이트/다크 두 모드를 Variable Mode로 구성할 것. 순정 메모의 노란색 계열 금지
- 간격 스케일 4/8/12/16/24/32/48, 편집 영역 최대 폭 680
- Foundations에 토큰 팔레트를 시각적으로 배치

만든 뒤 get_variable_defs로 되읽어서 Assets.xcassets Color Set과
Shared/DesignSystem.swift(Spacing, Typography, Radius, Layout)를 생성해줘.
응답 20KB 제한이 있으니 프레임을 통째로 요청하지 말고 컴포넌트 단위로 나눠서 요청해.
```

## 7. 세션이 길어졌을 때

컨텍스트가 흐려지면 `/compact` 후 다음을 붙여넣는다.

```
CLAUDE.md와 PROGRESS.md를 다시 읽고 현재 Phase와 남은 작업을 확인한 뒤 이어서 진행해줘.
```

## 8. 자주 막히는 지점

| 증상 | 원인 / 조치 |
|---|---|
| `/plugin`에 figma가 없음 | Claude Code 완전 재시작. MCP는 시작 시 초기화된다 |
| Figma 응답이 잘림 | 프레임이 큼. 컴포넌트 단위로 선택해 다시 요청 |
| 토큰 이름 없이 색상값만 나옴 | Figma에서 로컬 스타일이 아닌 **Variables**로 정의해야 함 |
| SwiftData 저장 시 크래시 | CLAUDE.md의 CloudKit 제약 5개 위반 여부 확인 |
| 확장에서 데이터가 안 보임 | ShareExtension·Widget 타깃에도 App Group 체크했는지 확인 |
| 시뮬레이터에서 동기화 안 됨 | 정상. 실기기 2대로 검증할 것 |
