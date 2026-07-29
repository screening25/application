# Phase 0 실행 런북 · 환경 구축

> `SPEC.md` Phase 0을 Mac에서 그대로 실행하기 위한 절차서.
> 이 문서는 원격 세션(Linux, Xcode·Figma MCP 없음)에서 작성됐고, **실행과 완료 판정은 Mac에서 한다.**
>
> 확정값은 `CLAUDE.md`의 "확정 식별자" 표가 유일한 기준이다. 아래에 나오는 값은 전부 그 표에서 왔다.

## 사전 조건

| 항목 | 상태 |
|---|---|
| 유료 Apple Developer 계정 | 확보됨 (2026-07-29 확인) |
| Xcode | 26.x — iOS/iPadOS 26, macOS 26 SDK 포함 |
| Mac | macOS 26 이상 (macOS 26 타깃 빌드에 필요) |
| 실기기 | Phase 2 동기화 검증에 **2대** 필요. Phase 0에서는 불필요 |

시작 전 확인:

```bash
xcodebuild -version          # Xcode 26.x
xcrun simctl list runtimes   # iOS 26.x 런타임 존재 확인
```

---

## 0.1 Xcode 프로젝트

### ① 프로젝트 생성

File → New → Project → **Multiplatform → App**

| 필드 | 값 | 비고 |
|---|---|---|
| Product Name | `Sumuk` | |
| Team | (본인 팀 선택) | 여기서 Team이 잡혀야 다음 단계 Capability가 컨테이너를 만들 수 있다 |
| Organization Identifier | `com.screening` | Bundle ID가 `com.screening.sumuk`으로 자동 조합된다 |
| Interface | SwiftUI | |
| Language | Swift | |
| Storage | **None** | ⚠️ SwiftData를 고르지 말 것 |
| Testing System | Swift Testing | |
| Include Tests | 체크 | 이게 4번째 타깃(`SumukTests`)이 된다 |

> **Storage를 None으로 두는 이유**
> `Storage: SwiftData`를 고르면 Xcode가 `Item` 모델과 `ModelContainer` 생성 코드를 `SumukApp.swift`에 직접 넣는다.
> 이는 `CLAUDE.md` 코드 컨벤션 —
> "`ModelContainer` 생성 코드는 `Shared/PersistenceController.swift` **한 곳에만** 존재한다" — 를 정면으로 위반한다.
> SwiftData는 Phase 2에서 `PersistenceController.swift`로 직접 도입한다.

### ② Swift 6 / strict concurrency

Project → 각 타깃 → Build Settings:

| 설정 | 값 |
|---|---|
| Swift Language Version (`SWIFT_VERSION`) | `6.0` |
| Strict Concurrency Checking (`SWIFT_STRICT_CONCURRENCY`) | `complete` |

Swift 6 언어 모드에서는 `complete`가 사실상 기본이지만, **명시적으로 설정한다.**
나중에 타깃을 추가할 때 새 타깃이 조용히 Swift 5 모드로 생기는 일을 막기 위해서다.
프로젝트 레벨(Project → Build Settings)에 설정하고 타깃은 상속받게 두면 관리가 쉽다.

### ③ 배포 타깃

| 플랫폼 | 값 |
|---|---|
| iOS / iPadOS (`IPHONEOS_DEPLOYMENT_TARGET`) | `26.0` |
| macOS (`MACOSX_DEPLOYMENT_TARGET`) | `26.0` |

### ④ 확장 타깃 2개 추가

File → New → Target:

| 타깃 | 템플릿 | Bundle ID |
|---|---|---|
| `ShareExtension` | Share Extension | `com.screening.sumuk.ShareExtension` |
| `Widget` | Widget Extension | `com.screening.sumuk.Widget` |

- Widget Extension 생성 시 **"Include Live Activity" 체크 해제** — 명세에 없다.
- "Embed in Application"이 `Sumuk`으로 잡혀 있는지 확인.
- 확장의 배포 타깃도 26.0으로 맞춘다 (템플릿이 낮게 잡는 경우가 있다).

여기까지 하면 타깃 4개: `Sumuk` / `ShareExtension` / `Widget` / `SumukTests`.

---

## 0.2 Capability

Signing & Capabilities 탭에서 설정한다. **어느 타깃에 무엇을 적용하는지가 핵심이다.**

| Capability | Sumuk | ShareExtension | Widget |
|---|:---:|:---:|:---:|
| iCloud → CloudKit (`iCloud.com.screening.sumuk`) | ✅ | ✅ | ✅ |
| App Groups (`group.com.screening.sumuk`) | ✅ | ✅ | ✅ |
| Keychain Sharing (`com.screening.sumuk.shared`) | ✅ | ✅ | ✅ |
| Background Modes → Remote notifications | ✅ | ❌ | ❌ |

> **⚠️ 명세와의 차이 — Background Modes**
> `SPEC.md` 0.1은 Capability 4종을 "App·ShareExtension·Widget **전부**에 적용"이라고 적었지만,
> **Background Modes는 앱 확장 타깃에 존재하지 않는 Capability다.** Xcode의 Capability 목록에 나타나지 않는다.
> 확장은 호스트 앱이 깨워주는 단명(短命) 프로세스라 백그라운드 모드를 스스로 선언할 수 없다.
> 따라서 Remote notifications는 **App 타깃에만** 적용한다. 나머지 3종은 명세대로 세 타깃 전부에 적용한다.
> CloudKit 원격 변경 알림은 App 타깃이 받아 처리하고, 확장은 App Group 공유 컨테이너를 통해 같은 저장소를 본다 —
> 기능적 손실은 없다.

### 순서 주의

1. **App 타깃에서 먼저** iCloud → CloudKit을 켜고 `+` 로 컨테이너 `iCloud.com.screening.sumuk`을 **새로 생성**한다.
2. 그 다음 ShareExtension·Widget에서 같은 컨테이너를 **체크만** 한다 (새로 만들지 말 것 — 이름이 겹쳐 실패하거나 별도 컨테이너가 생긴다).
3. App Group도 동일하게 App에서 생성 → 확장에서 체크.

### 검증 — entitlements 파일

세 타깃의 `.entitlements`가 아래를 포함해야 한다. 하나라도 빠지면 확장이 앱 DB를 못 본다
(`SPEC.md` 부록 B의 "Share Extension이 앱 DB를 못 봄" 함정).

```xml
<key>com.apple.developer.icloud-container-identifiers</key>
<array><string>iCloud.com.screening.sumuk</string></array>
<key>com.apple.developer.icloud-services</key>
<array><string>CloudKit</string></array>
<key>com.apple.security.application-groups</key>
<array><string>group.com.screening.sumuk</string></array>
<key>keychain-access-groups</key>
<array><string>$(AppIdentifierPrefix)com.screening.sumuk.shared</string></array>
```

App 타깃에만 추가로:

```xml
<key>com.apple.developer.aps-environment</key>
<string>development</string>
```

명령행에서 한 번에 확인:

```bash
grep -l "application-groups" Sumuk*/*.entitlements ShareExtension/*.entitlements Widget/*.entitlements
```

세 파일이 전부 나와야 한다.

---

## 0.3 3플랫폼 빌드 검증

Phase 0의 완료 조건이다. **세 개가 전부 통과해야 한다.**

```bash
# iOS
xcodebuild -scheme Sumuk -destination 'generic/platform=iOS' build

# iPadOS (iOS와 같은 SDK — 시뮬레이터로 실제 실행 확인까지 권장)
xcodebuild -scheme Sumuk -destination 'platform=iOS Simulator,name=iPad Pro 13-inch (M4)' build

# macOS
xcodebuild -scheme Sumuk -destination 'generic/platform=macOS' build
```

`generic/platform=iOS`는 서명까지 태우므로 Capability 설정 오류가 여기서 드러난다.
서명 문제로 막히면 `-allowProvisioningUpdates`를 붙인다.

경고 0을 목표로 한다 (`CLAUDE.md` 작업 규칙 6 — 빌드가 깨진 상태로 Phase를 종료하지 않는다).

---

## 0.4 Figma MCP 연결

디자인 파일이 **없으므로**, Phase 1에서 캔버스 쓰기 도구로 직접 만든다.
따라서 읽기 도구뿐 아니라 **쓰기 도구까지 붙어 있어야** Phase 1을 시작할 수 있다.

```bash
claude plugin install figma@claude-plugins-official
```

1. Claude Code를 **완전히 종료 후 재시작** (MCP는 시작 시에만 초기화된다)
2. `/plugin` → 오른쪽 방향키로 **Installed** 탭 → `figma` → Enter
3. 브라우저에서 **Allow access**
4. 다시 `/plugin` → `figma`가 **초록**인지 확인

### 도구 확인

아래가 전부 보여야 한다:

| 도구 | 용도 |
|---|---|
| `get_variable_defs` | 토큰 이름+값 추출 — **Phase 1의 핵심** |
| `get_code` | 참고용. 웹 코드라 그대로 쓰지 않는다 |
| `get_image` | 시각적 검증 전용 |
| `get_code_connect_map` | |
| 캔버스 쓰기 도구 | **디자인 파일을 새로 만들어야 하므로 필수** |

---

## 완료 판정 체크리스트

`SPEC.md` Phase 0 완료 조건 = "3플랫폼 빌드 성공 + Figma MCP 연결 확인".

- [ ] 타깃 4개 존재: `Sumuk` / `ShareExtension` / `Widget` / `SumukTests`
- [ ] 네 타깃 전부 Swift Language Version 6.0, Strict Concurrency `complete`
- [ ] 배포 타깃 iOS 26.0 / macOS 26.0
- [ ] Bundle ID 3종이 확정 식별자 표와 일치
- [ ] entitlements 3개 파일에 CloudKit·App Group·Keychain 그룹 전부 존재
- [ ] Background Modes → Remote notifications가 App 타깃에 적용 (확장은 해당 없음 — 위 주석 참조)
- [ ] `xcodebuild` iOS 빌드 성공
- [ ] `xcodebuild` iPadOS 빌드 성공
- [ ] `xcodebuild` macOS 빌드 성공
- [ ] 빌드 경고 0
- [ ] `/plugin`에서 `figma` 초록
- [ ] `get_variable_defs` + 캔버스 쓰기 도구 확인

전부 충족하면 `PROGRESS.md`의 P0 체크박스를 갱신하고 커밋한다:

```bash
git commit -m "[P0] Xcode 프로젝트 4개 타깃 + Capability 구성, 3플랫폼 빌드 확인"
```

---

## 이 Phase에서 자주 막히는 지점

| 증상 | 원인 / 조치 |
|---|---|
| 확장에서 앱 데이터가 안 보임 | ShareExtension·Widget 타깃에 App Group 체크 누락. entitlements 3개 전부 확인 |
| CloudKit 컨테이너 생성 실패 | Team 미선택 상태로 Capability를 켰다. Signing에서 Team 먼저 지정 |
| 컨테이너가 두 개 생김 | 확장에서 `+`로 새로 만들었다. 삭제 후 기존 컨테이너를 체크만 |
| 새 타깃이 Swift 5로 생성됨 | 프로젝트 레벨에 `SWIFT_VERSION = 6.0` 설정하고 타깃은 상속받게 둔다 |
| 확장 배포 타깃이 낮게 잡힘 | 템플릿 기본값. 26.0으로 수동 수정 |
| `/plugin`에 figma가 없음 | Claude Code 완전 재시작. MCP는 시작 시 초기화된다 |
| 토큰 이름 없이 색상값만 나옴 | Phase 1에서 로컬 스타일이 아닌 **Variables**로 정의해야 한다 |
