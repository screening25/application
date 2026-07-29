# CLAUDE.md

이 파일은 Claude Code가 매 세션 자동으로 읽는 프로젝트 규칙이다.

## 프로젝트

**Sumuk (수묵)** — 무료 마크다운 노트 앱. iOS 26 / iPadOS 26 / macOS 26 동시 지원.
유료 메모 앱의 기능 전체(마크다운·백링크·그래프·필기·잠금·버전관리·내보내기)를 갖추되,
서버 없는 구조(SwiftData+CloudKit)와 온디바이스 AI(FoundationModels)로 무료를 지속 가능하게 만든다.

- 전체 명세: `SPEC.md`
- 진행 상태: `PROGRESS.md`
- Phase 0 실행 절차: `PHASE0_RUNBOOK.md`

### 확정 식별자 (변경 금지)

이 값들은 CloudKit 컨테이너·App Group·Keychain 그룹이 전부 파생되는 뿌리다.
바꾸면 컨테이너를 재생성해야 하고 기존 동기화 데이터가 끊긴다. **하드코딩하지 말고 아래 표를 기준으로만 쓴다.**

| 항목 | 값 |
|---|---|
| 앱 이름 | `Sumuk` (표시명 수묵) |
| App Bundle ID | `com.screening.sumuk` |
| ShareExtension | `com.screening.sumuk.ShareExtension` |
| Widget | `com.screening.sumuk.Widget` |
| CloudKit 컨테이너 | `iCloud.com.screening.sumuk` |
| App Group | `group.com.screening.sumuk` |
| Keychain 그룹 | `com.screening.sumuk.shared` |
| URL 스킴 | `sumuk://` |

### 작업 환경

이 프로젝트는 두 환경에 걸쳐 진행된다. 세션 시작 시 **자신이 어느 쪽인지 먼저 판단한다.**

- **Mac 로컬 세션** — Xcode·시뮬레이터·실기기·Figma MCP 사용 가능. Phase의 실제 구현과 완료 판정은 전부 여기서 한다.
- **원격/컨테이너 세션** (Linux, Xcode·Figma MCP 없음) — 빌드·실기기 검증이 불가능하다.
  문서·명세·설계 산출물까지만 다루고, **어떤 Phase도 "완료"로 표시하지 않는다.**
  `swift`/`xcodebuild`가 PATH에 없으면 이 환경이다.

## 작업 규칙 (반드시 지킬 것)

1. **세션 시작 시 `PROGRESS.md`를 먼저 읽고 현재 Phase를 확인한다.** 임의로 다른 Phase를 건드리지 않는다.
2. **Phase는 순서대로만 진행한다.** 완료 조건을 전부 충족하기 전에 다음으로 넘어가지 않는다.
3. 일정 압박은 없다. 임시방편·주석 처리된 미구현(`TODO: later`)을 남기지 않는다.
4. 한 Phase가 끝나면 `PROGRESS.md`의 체크박스를 갱신하고 커밋한다. 메시지: `[P{번호}] 내용`
5. 명세에 없는 기능을 임의로 추가하지 않는다. 필요해 보이면 먼저 사용자에게 묻는다.
6. 빌드가 깨진 상태로 Phase를 종료하지 않는다.
7. 설계 판단이 갈리면 `SPEC.md`의 "설계 원칙"을 기준으로 삼는다.

## 기술 제약

- Swift 6, strict concurrency. SwiftUI + Observation.
- **외부 SPM 의존성 0개.** 라이브러리 추가 금지.
- 최소 배포 타깃 iOS/iPadOS 26.0, macOS 26.0.
- `#if os(...)` 분기는 최소화한다. 허용: NavigationSplitView 구성, 키보드 단축키, 툴바 배치, Pencil, 메뉴바.

## 코드 컨벤션

- 색상·간격·글꼴은 **반드시 `DesignSystem.swift` 토큰 경유**. 하드코딩 금지.
- 모든 뷰에 `#Preview` 작성. 라이트/다크 두 개.
- `ModelContainer` 생성 코드는 `Shared/PersistenceController.swift` **한 곳에만** 존재한다.
- 비동기는 async/await만. 완료 핸들러 패턴 금지.
- 강제 언래핑(`!`) 금지. `fatalError`는 프로그래머 오류에만.
- 사용자에게 보이는 문자열은 전부 `String Catalog` 경유 (한국어/영어).

## SwiftData + CloudKit 제약 (위반 시 런타임 크래시)

1. 모든 저장 속성은 옵셔널이거나 기본값을 가진다
2. `@Attribute(.unique)` 사용 불가
3. 모든 관계는 옵셔널 + inverse 필수
4. `deleteRule: .deny` 사용 불가
5. 배열 속성(`[String]`)에 `#Predicate` 필터링 금지 — 메모리에서 처리

## Figma 사용 규칙

- 토큰 추출은 `get_variable_defs`. 색상은 Figma **Variables**로 정의돼 있어야 이름이 넘어온다.
- `get_code` 출력은 웹 기준이므로 **그대로 쓰지 않는다.** 값과 레이아웃 구조만 참고하고 SwiftUI는 직접 작성한다.
- 호출당 응답 약 20KB 제한. 큰 프레임 통째로 요청 금지, 컴포넌트 단위로 선택해 요청한다.
- `get_image`는 시각적 검증용으로만.

## 검증 규칙

- CloudKit 동기화는 **실기기 2대**로 확인한다. 시뮬레이터 결과를 신뢰하지 않는다.
- 시리(App Intents)는 실기기 음성 호출로 확인한다.
- Phase 완료 보고 시 "무엇을 어떻게 확인했는지"를 함께 적는다.

## 확정 사항 (2026-07-29 사용자 확인 완료)

착수 전 확인해야 했던 항목은 전부 답을 받았다. 다시 묻지 않는다.

- **앱 이름 / Bundle ID** — `Sumuk` / `com.screening.sumuk`. 위 "확정 식별자" 표 참조.
- **Figma 디자인 파일** — **없다.** Phase 1은 `SPEC.md` 1.1의 "디자인 파일이 없으면" 경로를 탄다:
  캔버스 쓰기 도구로 `Foundations` / `Components` / `Screens` 페이지를 만들고,
  색상·간격·radius를 **Figma Variables로** 정의한 뒤 `get_variable_defs`로 되읽어 `DesignSystem.swift`를 생성한다.
  (로컬 스타일로 만들면 토큰명이 유실된다.)
- **유료 Apple Developer 계정** — 있다. CloudKit 컨테이너·App Group·위젯 생성 권한 확보됨.
  Phase 0의 Capability 설정을 우회 없이 그대로 진행한다.
