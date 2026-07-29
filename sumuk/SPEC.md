# 메모 앱 개발 명세서 (전체 기능 / 순서 기반)

> Claude Code용 단일 기준 문서. 프로젝트 루트에 `CLAUDE.md`로 두고 작업한다.
>
> **작업 규칙**
> 1. 일정 제한은 없다. 품질과 완성도를 우선한다.
> 2. **반드시 Phase 순서대로** 진행한다. 뒤 Phase를 먼저 손대지 않는다.
> 3. 각 Phase의 "완료 조건"을 전부 충족하기 전에 다음 Phase로 넘어가지 않는다.
> 4. 각 Phase 종료 시 커밋한다. 커밋 메시지: `[P{번호}] 내용`
> 5. 판단이 필요하면 "설계 원칙"을 우선하고, 애매하면 사용자에게 묻는다.

---

## 0. 프로젝트 개요

| 항목 | 값 |
|---|---|
| 프로젝트명 | **Sumuk (수묵)** |
| Bundle ID | `com.screening.sumuk` |
| 형태 | SwiftUI 멀티플랫폼 단일 타깃 + 확장 타깃 |
| 플랫폼 | iOS 26 / iPadOS 26 / macOS 26 |
| 동기화 | SwiftData + CloudKit (서버 없음, 운영비 0) |
| AI | FoundationModels (온디바이스, 과금 없음) |
| 디자인 | Figma → MCP로 토큰 추출 → SwiftUI |
| 수익 모델 | 전면 무료 |

### 제품 정의
유료 메모 앱의 모든 기능(마크다운·백링크·그래프·필기·잠금·버전관리·내보내기)을 갖추되,
서버가 필요 없는 구조와 온디바이스 AI로 **무료를 지속 가능하게** 만든 노트 앱.

### 설계 원칙
1. **사용자 데이터는 사용자 것** — 본문은 언제나 순수 마크다운. 독점 포맷 금지.
2. **시스템에 녹아든다** — 앱을 열지 않고도 쓸 수 있는 경로(공유·위젯·시리·Spotlight)를 항상 제공.
3. **애플의 원칙은 따르되 외형은 다르게** — 절제와 콘텐츠 우선은 유지, 시각적 정체성은 독자적으로.
4. **네트워크 의존 0** — 모든 기능이 오프라인에서 동작해야 한다.
5. 외부 SPM 의존성 **0개**.

---

## 1. 기술 스택

- Swift 6, SwiftUI, Observation, Swift Concurrency (strict mode)
- SwiftData (CloudKit 미러링)
- FoundationModels — 요약/태그
- AppIntents / WidgetKit / Share Extension / CoreSpotlight
- PencilKit (iPadOS)
- LocalAuthentication (잠금)
- 최소 배포 타깃: iOS 26.0 / iPadOS 26.0 / macOS 26.0

---

## Phase 0 · 환경 구축

### 0.1 Xcode 프로젝트
- [ ] Multiplatform App 생성, Swift 6 / strict concurrency 활성화
- [ ] Bundle ID 확정 및 적용
- [ ] 타깃 4개: `App` / `ShareExtension` / `Widget` / `Tests`
- [ ] Capability (App·ShareExtension·Widget **전부**에 적용)
  - iCloud → CloudKit, 컨테이너 `iCloud.com.screening.sumuk`
  - App Groups → `group.com.screening.sumuk`
  - Background Modes → Remote notifications
  - Keychain Sharing (잠금 기능용)
- [ ] 3플랫폼 빈 앱 빌드 성공

### 0.2 Figma MCP 연결
- [ ] 터미널에서 `claude plugin install figma@claude-plugins-official`
- [ ] Claude Code 재시작 → `/plugin` → Installed 탭 → `figma` 선택 → 브라우저에서 Allow access
- [ ] `/plugin`으로 `figma` 연결(초록) 확인
- [ ] 사용 가능 도구 확인: `get_code`, `get_image`, `get_variable_defs`, `get_code_connect_map`, 캔버스 쓰기 도구

> 원격 서버(`https://mcp.figma.com/mcp`)를 사용한다. 로컬 데스크톱 서버(`http://127.0.0.1:3845/mcp`)는
> 조직 보안 요건이 있을 때만. 응답이 호출당 약 20KB로 제한되므로 **큰 프레임을 통째로 요청하지 말 것.**

### 완료 조건
3플랫폼 빌드 성공 + Figma MCP 연결 확인.

---

## Phase 1 · 디자인 시스템 (Figma → SwiftUI)

> 모든 UI가 여기에 의존하므로 반드시 먼저 확정한다.

### 1.1 Figma 파일 준비
- 사용자가 Figma 파일을 제공하면 그것을 기준으로 한다.
- **디자인 파일이 없으면**, Claude Code가 캔버스 쓰기 도구로 Figma에 직접 생성한다:
  - 페이지: `Foundations` / `Components` / `Screens`
  - Foundations에 **Figma Variables**로 색상·간격·radius를 정의 (Variables로 만들어야 `get_variable_defs`가 토큰명을 반환한다. 로컬 스타일만 쓰면 값만 나오고 이름이 사라진다)

### 1.2 디자인 토큰 정의

**색상 — 먹/잉크 컨셉. 순정 메모의 노란색 계열 사용 금지.**

| 토큰 | 용도 |
|---|---|
| `ink` | 본문 텍스트. 짙은 청회색 |
| `ink/secondary` | 보조 텍스트 |
| `paper` | 편집 영역 배경. 미세하게 따뜻한 오프화이트 (다크: 완전 검정 아닌 짙은 회색) |
| `surface` | 사이드바·툴바 |
| `accent` | 강조색 **1개만** |
| `link` | `[[백링크]]` 텍스트 |
| `divider` | 구분선 |

**타이포**
- 본문: 세리프 — `.system(.body, design: .serif)`
- UI 크롬: 시스템 폰트
- 코드 블록: `.monospaced`
- **모두 Dynamic Type 대응** (고정 pt 금지)

**레이아웃**
- 간격 스케일: 4 / 8 / 12 / 16 / 24 / 32 / 48
- 편집 영역 최대 폭 680pt, 중앙 정렬
- 좌우 패딩: iPhone 20, iPad/Mac 32

### 1.3 시그니처 규칙
툴바·사이드바는 시스템 유리 재질을 따르고, **본문 편집 영역만 완전 불투명한 '종이'**로 처리한다.
이 대비가 앱의 시각적 정체성이다. 편집 영역에 투명도·블러를 넣지 말 것.

### 1.4 SwiftUI 변환 규칙 (중요)
Figma MCP의 `get_code`는 웹 프레임워크를 전제로 한 결과를 낸다. **그 출력을 그대로 쓰지 않는다.**
- `get_variable_defs`로 **토큰 이름과 값만** 가져온다 → `Assets.xcassets` Color Set + `DesignSystem.swift`로 변환
- 레이아웃은 프레임의 constraints/auto-layout 정보를 읽어 `VStack`/`HStack`/`Grid`로 **직접 작성**한다
- `get_image`는 시각적 검증용으로만 사용
- 색상 값을 코드에 하드코딩 금지 — 반드시 토큰 경유

### 1.5 산출물
- [ ] `Assets.xcassets` — 라이트/다크 Color Set 전체
- [ ] `Shared/DesignSystem.swift` — `Spacing`, `Typography`, `Radius`, `Layout` 열거형
- [ ] `Preview/DesignSystemGallery.swift` — 전 토큰을 한 화면에 보여주는 프리뷰

### 완료 조건
갤러리 프리뷰가 3플랫폼 × 라이트/다크에서 정상 렌더링되고, 이후 모든 UI가 이 토큰만 사용한다.

---

## Phase 2 · 데이터 모델 & 동기화

### 2.1 CloudKit 제약 (위반 시 런타임 크래시)
1. 모든 저장 속성은 **옵셔널이거나 기본값**을 가진다
2. `@Attribute(.unique)` **사용 불가**
3. 모든 관계는 옵셔널이며 **inverse 필수**
4. `deleteRule: .deny` 사용 불가

### 2.2 모델

```swift
@Model final class Note {
    var id: UUID = UUID()
    var title: String = ""
    var body: String = ""              // 순수 마크다운 원본
    var normalizedTitle: String = ""   // lowercased, 링크 매칭용
    var createdAt: Date = Date()
    var updatedAt: Date = Date()
    var summary: String?               // AI 생성
    var tags: [String] = []
    var isPinned: Bool = false
    var isTrashed: Bool = false
    var isLocked: Bool = false
    var drawingData: Data?             // PencilKit
    var folder: Folder?                // inverse: folder.notes
}

@Model final class Folder {
    var id: UUID = UUID()
    var name: String = ""
    var sortIndex: Int = 0
    var parent: Folder?                // inverse: children
    var children: [Folder]? = []
    var notes: [Note]? = []
}

@Model final class NoteLink {
    var id: UUID = UUID()
    var sourceNoteID: UUID = UUID()
    var targetTitle: String = ""       // 정규화된 제목
}

@Model final class NoteVersion {
    var id: UUID = UUID()
    var noteID: UUID = UUID()
    var body: String = ""
    var savedAt: Date = Date()
}
```

**설계 의도**
- 백링크는 SwiftData 관계가 아닌 **문자열 기반 느슨한 연결**. 아직 존재하지 않는 노트도 링크할 수 있어야 하기 때문.
- `tags: [String]`에 대해 `#Predicate` 필터링 금지 (CloudKit 배열 속성에서 불안정). 태그 필터는 메모리에서 처리.

### 2.3 공유 컨테이너
```swift
let config = ModelConfiguration(
    groupContainer: .identifier("group.com.screening.sumuk"),
    cloudKitDatabase: .private("iCloud.com.screening.sumuk")
)
```
이 코드는 `Shared/PersistenceController.swift` **한 곳에만** 존재하고 앱·확장·위젯이 공유한다.

### 완료 조건
- [ ] 실기기 **2대**에서 노트 생성/수정/삭제가 양방향 동기화됨 (시뮬레이터 결과 신뢰 금지)
- [ ] 앱 강제종료 후 재실행 시 데이터 유지

---

## Phase 3 · 기본 CRUD & 내비게이션

- [ ] `NavigationSplitView` 3단: 사이드바(폴더/태그) — 목록 — 에디터
- [ ] iPhone은 2단으로 자동 축소
- [ ] 노트 생성·삭제(휴지통 플래그)·복원·완전삭제
- [ ] 목록 정렬: 수정일/생성일/제목, 고정(pin) 상단
- [ ] 자동 저장 (0.5초 디바운스)
- [ ] 키보드 단축키: ⌘N 새 노트, ⌘F 검색, ⌘⌫ 삭제, ⌘1/2/3 사이드바 토글
- [ ] 빈 상태(Empty State) 화면

### 완료 조건
3플랫폼에서 노트 생성부터 삭제까지 전체 흐름이 크래시 없이 동작.

---

## Phase 4 · 마크다운 에디터

- [ ] 제목 `TextField` + 본문 `TextEditor` 분리
- [ ] **편집 모드**: 순수 텍스트 + 문법 하이라이팅 (`#`, `**`, `-`, `>`, 코드펜스)
- [ ] **미리보기 모드**: 렌더링 뷰. 토글 버튼으로 전환
- [ ] 지원 문법: 제목 1~6, 굵게/기울임/취소선, 순서·비순서 목록, 체크박스, 인용, 코드(인라인·블록), 구분선, 표, 링크, 이미지
- [ ] 마크다운 툴바 (iOS 키보드 상단 / macOS 툴바): 굵게·기울임·목록·체크박스·코드·링크
- [ ] 체크박스는 미리보기에서 **탭으로 토글** → 원본 텍스트에 반영
- [ ] 이미지 첨부 (붙여넣기·드래그앤드롭), 본문에는 마크다운 이미지 문법으로 삽입

> 위지윅(입력과 동시에 서식이 사라지는 방식)은 구현하지 않는다. 편집/미리보기 2모드로 간다.

---

## Phase 5 · 백링크

### 5.1 파서 `Shared/LinkParser.swift`
- 정규식: `\[\[([^\[\]\n]+)\]\]`
- 공백 트림 → `lowercased()` → 중복 제거
- 단위 테스트: 중첩, 개행 포함, 빈 링크, 코드블록 내부 무시, 중복

### 5.2 링크 동기화
저장 디바운스와 **동일 시점에 1회만** 실행:
1. 해당 노트의 기존 `NoteLink` 전부 삭제
2. 파서 결과로 재생성

### 5.3 UI
- [ ] 본문에서 `[[` 입력 시 자동완성 팝오버 — 제목 prefix 매칭 상위 5개 + "새 노트 만들기: OOO"
- [ ] 링크 탭 → 대상 노트 이동. 없으면 그 제목으로 생성 후 이동
- [ ] 에디터 하단 **역링크 섹션** — "이 노트를 링크한 노트" 목록 + 해당 문장 미리보기
- [ ] 존재하지 않는 링크는 시각적으로 구분 (점선 밑줄 등)

---

## Phase 6 · 그래프 뷰

- [ ] `Canvas`로 노드-엣지 렌더링 (외부 라이브러리 금지)
- [ ] 힘 기반 레이아웃 시뮬레이션 (간단한 spring + repulsion, `TimelineView`로 구동)
- [ ] 노드 크기 = 역링크 수, 색상 = 태그
- [ ] 확대/축소/팬, 노드 탭 → 노트 이동
- [ ] **로컬 그래프**: 에디터에서 현재 노트 기준 1~2단계 이웃만 표시
- [ ] 노트 500개 기준 60fps 유지. 미달 시 노드 수 상한 + LOD 적용

---

## Phase 7 · 폴더 · 태그 · 검색

- [ ] 폴더 계층 (드래그로 이동, 무한 depth, 순환 참조 방지)
- [ ] 태그: 본문 `#태그` 자동 인식 + 수동 편집. 사이드바에 태그 목록 + 개수
- [ ] 전문 검색: 제목·본문·태그. 결과에 매칭 문맥 하이라이트
- [ ] 검색 필터: 폴더, 태그, 기간, 고정 여부
- [ ] **CoreSpotlight 색인** — 시스템 검색에서 본문이 잡히고, 결과 탭 시 해당 노트로 딥링크
- [ ] 노트 저장/삭제 시 색인 갱신, 최초 실행 시 전체 재색인

---

## Phase 8 · 온디바이스 AI

```swift
@Generable
struct NoteInsight {
    @Guide(description: "메모를 2문장 이내로 요약. 사용자가 쓴 언어와 동일한 언어로 작성")
    let summary: String
    @Guide(description: "메모를 분류하는 태그 1~3개. 각 태그는 두 단어 이내")
    let tags: [String]
}
```

규칙:
- [ ] `SystemLanguageModel.default.availability` 확인 → `.available`이 아니면 관련 UI를 **숨긴다** (경고문 표시 금지)
- [ ] **자동 실행 금지.** 사용자가 버튼을 눌렀을 때만 실행 (배터리·발열 리뷰 리스크 제거)
- [ ] 프롬프트에 기존 태그 상위 30개를 함께 전달하고 "가능하면 재사용" 지시 → 태그 무한 증식 방지
- [ ] 결과는 시트로 먼저 보여주고 "적용" 버튼으로 확정. 자동 덮어쓰기 금지
- [ ] 본문 200자 미만이면 버튼 비활성화
- [ ] 에러 시 조용히 실패 + 토스트. 크래시 절대 금지

---

## Phase 9 · 빠른 캡처

### 9.1 Share Extension
- [ ] 받는 타입: `public.plain-text`, `public.url`, `public.image`
- [ ] UI: 제목 + 본문 미리보기 + 폴더 선택 + 저장
- [ ] URL이면 첫 줄에 링크 삽입
- [ ] 저장 후 `WidgetCenter.shared.reloadAllTimelines()`

### 9.2 위젯
- [ ] `.systemSmall` — 최근 노트 1개 + 새 노트 버튼
- [ ] `.systemMedium` — 최근 노트 3개
- [ ] `.systemLarge` — 최근 6개 + 고정 노트
- [ ] **인터랙티브 위젯** — `AppIntent` 연결로 체크박스 토글을 위젯에서 직접 처리
- [ ] **잠금화면 위젯** (`.accessoryRectangular`, `.accessoryCircular`)
- [ ] 딥링크: `sumuk://new`, `sumuk://note/<uuid>`

### 9.3 App Intents / 시리
- [ ] `CreateNoteIntent` (`openAppWhenRun = false`) — 백그라운드 저장
- [ ] `AppendToNoteIntent`, `SearchNotesIntent`, `OpenNoteIntent`
- [ ] `AppShortcutsProvider`에 자연어 문구 각 3개 이상 등록
- [ ] `AppEntity` 채택으로 단축어 앱에서 노트를 파라미터로 선택 가능하게
- [ ] 실기기에서 시리 음성 호출 테스트

---

## Phase 10 · Apple Pencil (iPadOS)

- [ ] `PencilKit` 캔버스를 노트에 첨부 (`drawingData`)
- [ ] 손가락/펜슬 입력 구분 설정
- [ ] 도구 팔레트(`PKToolPicker`)
- [ ] Scribble 지원 (텍스트 필드에서 필기 입력)
- [ ] iPhone/Mac에서는 필기를 **읽기 전용 이미지**로 표시
- [ ] 필기 데이터도 CloudKit 동기화 확인 (용량 주의 — 노트당 상한 설정)

---

## Phase 11 · 메모 잠금

- [ ] `LocalAuthentication` — Face ID / Touch ID / 암호
- [ ] 잠긴 노트는 목록에서 제목만 표시, 본문·미리보기·검색 결과에서 제외
- [ ] 앱이 백그라운드로 가면 자동 재잠금 (지연 시간 설정 가능)
- [ ] 위젯·Spotlight·시리에서 잠긴 노트 내용 노출 금지
- [ ] 생체인증 미지원 기기 폴백 처리

---

## Phase 12 · 버전 히스토리

- [ ] 의미 있는 변경 시 `NoteVersion` 스냅샷 저장 (5분 간격 또는 200자 이상 변경 시)
- [ ] 버전 목록 + 현재본과의 **diff 하이라이트**
- [ ] 특정 버전으로 복원 (복원 직전 상태도 버전으로 저장)
- [ ] 노트당 최대 50개 보관, 초과 시 오래된 것부터 정리

---

## Phase 13 · 파일 시스템 통합 (.md 폴더 미러링)

> 가장 까다로운 Phase. 앞 기능이 모두 안정화된 뒤에 착수한다.

- [ ] 설정에서 사용자가 폴더 선택 (`fileImporter` + security-scoped bookmark)
- [ ] 노트 ↔ `.md` 파일 양방향 동기화, 폴더 구조 = 앱 내 폴더 구조
- [ ] 프론트매터(YAML)로 id·tags·createdAt 보존
- [ ] `NSFileCoordinator` + `NSFilePresenter`로 외부 변경 감지
- [ ] **충돌 처리**: 양쪽이 모두 바뀐 경우 `파일명 (충돌 2026-07-30).md` 생성 후 사용자에게 알림. 자동 병합 금지
- [ ] 미러링은 **선택 기능**. 끄면 앱 내부 저장만 사용
- [ ] macOS에서 먼저 구현 → iOS/iPadOS 순으로 확장

---

## Phase 14 · 내보내기

- [ ] 마크다운 (.md) — 단일 / 다중(zip)
- [ ] PDF — 미리보기 렌더링 기반, 페이지 여백·머리말 설정
- [ ] HTML — 인라인 CSS 포함 단일 파일
- [ ] DOCX — 제목·목록·굵게/기울임·코드·표 매핑
- [ ] 전체 백업 내보내기/가져오기 (JSON + 첨부 파일 zip)
- [ ] 공유 시트 연동, macOS는 저장 패널

---

## Phase 15 · 테마

- [ ] 프리셋 테마 4~5종 (Phase 1의 토큰 세트를 교체하는 방식)
- [ ] 본문 글꼴 선택 (세리프/산세리프/모노), 글자 크기·행간·단락 간격
- [ ] 편집 영역 폭 조절
- [ ] 라이트/다크/시스템 따름
- [ ] 테마 설정은 기기별 로컬 저장 (CloudKit 동기화 대상 아님)

---

## Phase 16 · 플랫폼 마감

**macOS**
- [ ] `MenuBarExtra` 상주 — 어디서든 빠른 캡처
- [ ] 전역 단축키 등록 (사용자 지정 가능)
- [ ] 메뉴바 메뉴 전체 구성 (파일/편집/보기/윈도우)
- [ ] 다중 윈도우, 노트 개별 창으로 열기

**iPadOS**
- [ ] 다중 윈도우 / Stage Manager
- [ ] 외장 키보드 단축키 전체
- [ ] 드래그앤드롭 (앱 간 텍스트·이미지)

**공통**
- [ ] 핸드오프(`NSUserActivity`) — 기기 간 편집 이어하기
- [ ] Quick Look 확장 (.md 미리보기)
- [ ] Focus Filter 연동 (집중 모드별 폴더 필터)

---

## Phase 17 · 품질

- [ ] 접근성: VoiceOver 라벨 전체, Dynamic Type 최대 크기 검증, 명암비 4.5:1 이상, 모션 감소 대응
- [ ] 현지화: 한국어 + 영어 (`String Catalog`)
- [ ] 성능: 노트 1000개 기준 목록 스크롤 60fps, 앱 시작 1초 이내
- [ ] 단위 테스트: 파서, 링크 동기화, 마크다운 렌더링, 충돌 처리
- [ ] 3플랫폼 전체 시나리오 수동 QA
- [ ] 크래시·경고 0
- [ ] 온보딩 화면, 앱 아이콘 (Figma에서 추출)

---

## 부록 A · 파일 구조

```
Sumuk/
├─ Shared/
│  ├─ PersistenceController.swift
│  ├─ DesignSystem.swift
│  ├─ Models/          Note, Folder, NoteLink, NoteVersion
│  ├─ Markdown/        Parser, Renderer, Highlighter
│  ├─ LinkParser.swift
│  ├─ NoteStore.swift
│  └─ Export/          MarkdownExporter, PDFExporter, HTMLExporter, DocxExporter
├─ App/
│  ├─ SumukApp.swift
│  ├─ Views/           Sidebar, NoteList, Editor, Preview, Backlinks,
│  │                   Graph, Search, Settings, Themes, VersionHistory
│  ├─ Intents/
│  ├─ AI/
│  ├─ Pencil/
│  ├─ Lock/
│  └─ FileSync/
├─ ShareExtension/
├─ Widget/
└─ Tests/
```

## 부록 B · 함정 목록

| 함정 | 대응 |
|---|---|
| SwiftData+CloudKit 스키마 제약 위반 | Phase 2.1의 4개 규칙을 모델 작성 전 확인 |
| 시뮬레이터에서 CloudKit 동기화 미작동 | 실기기 2대 필수 |
| Share Extension이 앱 DB를 못 봄 | 확장 타깃에도 App Group 체크 확인 |
| Figma MCP 응답 20KB 초과 | 큰 프레임을 통째로 요청하지 말고 컴포넌트 단위로 선택 |
| Figma `get_code` 출력이 웹 코드 | 토큰·레이아웃 값만 취하고 SwiftUI는 직접 작성 |
| Figma 로컬 스타일만 사용 시 토큰명 유실 | Variables로 정의해야 `get_variable_defs`가 이름을 반환 |
| 백링크 재생성이 매 입력마다 실행 | 저장 디바운스와 동일 시점 1회 |
| 위젯 미갱신 | 저장 시 `reloadAllTimelines()` |
| 파일 미러링 무한 루프 | 앱이 쓴 변경은 무시하도록 write-token 처리 |
| PencilKit 데이터로 CloudKit 용량 초과 | 노트당 상한 + 압축 |
| FoundationModels 미지원 기기 | availability 체크 후 UI 숨김 |
