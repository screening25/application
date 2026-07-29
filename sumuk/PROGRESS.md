# PROGRESS.md

> Claude Code는 세션 시작 시 이 파일을 먼저 읽는다.
> Phase 완료 시 체크박스를 갱신하고 "현재 위치"를 수정한 뒤 커밋한다.

## 현재 위치

**진행 중: Phase 0 — 환경 구축** (착수 대기 — Mac에서 실행 필요)

사전 확인 사항 — **전부 해결됨 (2026-07-29)**:
- [x] 앱 이름 확정 — **Sumuk (수묵)**
- [x] Bundle ID 확정 — `com.screening.sumuk` (파생 식별자는 `CLAUDE.md` "확정 식별자" 표 참조)
- [x] Figma 디자인 파일 유무 — **없음.** Phase 1에서 캔버스 쓰기 도구로 신규 생성 (Variables 필수)
- [x] 유료 Apple Developer 계정 / iCloud 컨테이너 생성 권한 — **있음**

### 다음에 할 일

`PHASE0_RUNBOOK.md`를 따라 **Mac에서** Phase 0을 실행한다.
런북 끝의 완료 판정 체크리스트 12개를 전부 충족한 뒤에만 아래 P0 체크박스를 켠다.

> ⚠️ Phase 0은 아직 **완료가 아니다.** Xcode 프로젝트 생성·Capability 설정·3플랫폼 빌드·Figma MCP 연결은
> 원격 Linux 세션에서 수행·검증할 수 없다 (Xcode·macOS·Figma MCP 부재).
> 원격 세션은 문서와 설계 산출물까지만 다룬다 — `CLAUDE.md`의 "작업 환경" 항목 참조.

## Phase 체크리스트

- [ ] **P0 · 환경 구축** — Xcode 프로젝트, 4개 타깃, Capability, Figma MCP 연결
  - 완료 조건: 3플랫폼 빈 앱 빌드 성공 + Figma MCP 연결 확인
- [ ] **P1 · 디자인 시스템** — Figma 토큰 → Assets + DesignSystem.swift
  - 완료 조건: 토큰 갤러리 프리뷰가 3플랫폼 × 라이트/다크 정상 렌더링
- [ ] **P2 · 데이터 모델 & 동기화** — Note/Folder/NoteLink/NoteVersion, App Group 컨테이너
  - 완료 조건: 실기기 2대 양방향 동기화 확인
- [ ] **P3 · 기본 CRUD & 내비게이션**
  - 완료 조건: 생성~삭제 전체 흐름 3플랫폼 무크래시
- [ ] **P4 · 마크다운 에디터** — 편집/미리보기 2모드, 툴바, 체크박스 토글
- [ ] **P5 · 백링크** — 파서, 자동완성, 역링크 섹션
- [ ] **P6 · 그래프 뷰** — Canvas 기반, 로컬 그래프
- [ ] **P7 · 폴더·태그·검색 + Spotlight 색인**
- [ ] **P8 · 온디바이스 AI** — 요약·태그 (버튼 실행)
- [ ] **P9 · 빠른 캡처** — Share Extension, 위젯, App Intents/시리
- [ ] **P10 · Apple Pencil** (iPadOS)
- [ ] **P11 · 메모 잠금**
- [ ] **P12 · 버전 히스토리**
- [ ] **P13 · .md 폴더 미러링**
- [ ] **P14 · 내보내기** — MD/PDF/HTML/DOCX/백업
- [ ] **P15 · 테마**
- [ ] **P16 · 플랫폼 마감** — macOS 메뉴바, iPad 다중창, 핸드오프, Quick Look
- [ ] **P17 · 품질** — 접근성, 현지화, 성능, 테스트, 아이콘

## 작업 로그

### 착수 준비 (2026-07-29)
- 한 일:
  - 사전 확인 4개 항목 확정 (앱 이름 Sumuk / Bundle ID `com.screening.sumuk` / Figma 파일 없음 / 유료 계정 있음)
  - `SPEC.md`의 `<team>`·`memoapp` 플레이스홀더를 확정값으로 치환 (Bundle ID, CloudKit 컨테이너, App Group, URL 스킴 `sumuk://`, 파일 구조 `Sumuk/`, `SumukApp.swift`)
  - `CLAUDE.md`에 "확정 식별자" 표 + "작업 환경" 규칙 추가, "물어볼 것" 절을 "확정 사항"으로 교체
  - `PHASE0_RUNBOOK.md` 작성 — Phase 0의 Mac 실행 절차서
- 검증 방법:
  - `SPEC.md` 전문에서 `<team>` / `memoapp` / `MemoApp` 잔존 0건 확인
- 남은 이슈 / 판단이 필요했던 것:
  - **Background Modes**: `SPEC.md` 0.1은 Capability 4종을 세 타깃 전부에 적용하라고 적었으나, Background Modes는 앱 확장에 존재하지 않는 Capability다. Remote notifications는 App 타깃에만 적용하기로 하고 런북에 근거를 명시했다. 기능 손실 없음(확장은 App Group 공유 컨테이너로 같은 저장소를 본다).
  - **Xcode 템플릿 Storage 옵션**: `Storage: SwiftData`를 고르면 `ModelContainer` 생성 코드가 `SumukApp.swift`에 박혀 `CLAUDE.md` 코드 컨벤션을 위반한다. `None`으로 생성하고 Phase 2에서 `PersistenceController.swift`로 도입하도록 런북에 명시했다.
  - Phase 0 자체는 미실행 — Mac 세션에서 런북대로 수행할 것.

<!-- Phase 완료 시 아래에 추가:
### P0 완료 (YYYY-MM-DD)
- 한 일:
- 검증 방법:
- 남은 이슈:
-->
