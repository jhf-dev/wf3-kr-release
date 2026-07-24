# 릴리즈 노트 (20260724-v7-release)

## 다운로드

- 배포 파일: `wind3-korean-patch-20260724-v7-release.zip`
- SHA-256: `8AF4B0CAD56B6AAB11DBE4C01486BD0041B565EE0BF5C9678E8D39DA159B33B1`
- 파일 크기: `25,526,727` bytes

## 20260702-v1-release 대비 주요 변경사항

### 런처 전면 개편

- Full·Lite 런처의 화면 구성과 기능 흐름을 전면적으로 정리하고, 각 런처가 독립적으로 실행되도록 개선했습니다.
- 게임 폴더 자동 감지와 화면·입력·자동 기능 설정 흐름을 정리하고, 설정과 게임 실행의 응답 속도를 개선했습니다.

### WindConfig 교체

- 패치 적용 시 기존 `windconfig.exe`를 `windconfig_original.exe`로 보존하고, 게임 실행·화면 설정·입력/자동 기능을 제공하는 새 경량 WindConfig를 설치합니다.
- Steam과 저해상도·저사양 환경에서 편하게 사용할 수 있도록 창 크기, 글꼴, 여백을 다듬었습니다.

### 폰트 렌더링 개선

- 한국어 글꼴의 크기·굵기·선명도를 재조정하고, 비표준 해상도에서 발생하던 글리프 경계 잔상과 일부 잘림을 개선했습니다.
- 글리프 누락과 표시 충돌을 줄여 UI와 대사 표시의 일관성을 높였습니다.

### 번역 품질 개선

- 대사, 고유명사, 아이템·스킬 설명과 시스템 UI 번역을 전반적으로 재검수했습니다.
- 문장 흐름과 표기 규칙을 통일하고, 남아 있던 일부 중국어·영문 UI를 한국어로 보강했습니다.

## 20260615-v1-release 대비 변경사항

* 대사·고유명사 표기 교정
  - 풀네임 구분자를 전각 마침표에서 CP949 안전 가운뎃점(·)으로 통일했습니다.
  - 캐논 표기를 정리했습니다: 파나엘, 히루타, 쉬라·베키도, 여상인, 아이슬링/아이슬링 그린, 크림슨/그린 등.

* 스킬 설명 정비
  - 스킬 설명 349건을 재검수해 효과 표현을 자연스럽게 다듬고, 전각 인용부호(『』)를 통일했습니다.

* 아이템 표기 교정
  - 도구 이름과 설명을 캐논 표기(라케시스비약)로 교정했습니다.

* 창모드 커서/카메라 수정
  - 창모드·테두리 없음 모드에서 전투 시작 시 커서가 화면 우하단으로 쏠려 카메라가 자동으로 밀리던 문제를 수정했습니다.
  - 게임 내부 논리 커서를 화면 중앙으로 고정해, 게임패드 사용 시에도 시작 시 카메라 쏠림이 발생하지 않습니다.

* 자동 기능(/ 키, 실험용) 수정
  - 총사 계열이 원거리 자동 공격을 발사하지 못하던 문제를 수정했습니다.
  - 턴 경계에서 입력이 누수되거나 원거리 공격 후 교착되던 문제를 수정했습니다.

* 패키지 검증
  - ZIP SHA-256: `55F11CFC84632D2CBEE8020B38EC44B10216015E5699AABD80A2E4B0AAE798B7`.
  - 깨끗한 임시 설치에 적용/복원하는 clean/temp install gate를 통과했습니다(payload `16`개, `status -> apply -> status -> apply -> save-apply -> save-restore -> restore` 모두 return code `0`, 원본 복원 검증 통과).
  - 적용된 root `d3d9.dll` SHA-256은 `3847B7D9D82688CCE2AD7D56073C548D17D9A6094F2A34DC8F1A6D9AC7D4D586`입니다.

## beta-20260609-v2 대비 변경사항

* 배포 런처 화면 정리
  - `게임 실행 / 화면`, `지원 / 업데이트` 그룹의 버튼 간격과 여백을 다듬어, 일부 버튼이 그룹 테두리에 닿던 부분을 정리했습니다.

* 내부 처리 개선
  - 런타임에 표시되는 일부 텍스트(월드맵 지명, 세이브 제목 등)의 처리 방식을 정리해, 이후 번역 갱신이 더 매끄럽게 반영되도록 했습니다.
  - 사용자 화면에 보이는 동작과 텍스트는 이전 버전과 동일합니다.

* 패키지 검증
  - ZIP SHA-256: `10675F4C144D044870A55C41274C81B7A06310E708BBF9F8BC661CBCA15AD3DB`.
  - 깨끗한 임시 설치에 적용/복원하는 clean/temp install gate를 통과했습니다(payload `16`개, 원본 복원 검증 통과).
  - 적용된 root `d3d9.dll` SHA-256은 `FBD6F5212E47C798405497C32B9F8C2784C734C16AA1342CD05A5C3EAFB93F9C`입니다.

## beta-20260609-v1 대비 변경사항

* 버전 안내 단순화
  - `버전 안내` 버튼이 백엔드 EXE를 실행하지 않도록 변경했습니다.
  - 런처는 `launcher_version.json`만 읽어 현재 패키지 버전/tag를 표시합니다.
  - 버전 안내에서 `d3d9.dll`, `dinput8.dll`, launcher/updater 해시는 계산하지 않습니다.

* 오류 보고 ZIP 통합
  - 별도 `진단 정보 저장` 버튼을 제거하고 `오류 보고 ZIP` 버튼으로 합쳤습니다.
  - 오류 보고 ZIP에는 `diagnostics/wind3_release_diagnostics.txt`가 포함됩니다.
  - DLL 파일 본문은 계속 제외하고, DLL 식별에는 파일명, 크기, 수정 시각, SHA-256 메타데이터를 사용합니다.

* 패키지 검증
  - ZIP SHA-256: `0AADDB50D2F32C8483B5A57003419614F34123F750F9DE889DD14ACD3D1DC3E1`.
  - clean/temp install gate에서 `status -> apply -> status -> apply -> save-apply -> save-restore -> restore` 모두 return code `0`을 확인했습니다.
  - 빌드된 백엔드 `version-info` 출력이 파일 해시 목록 없이 버전 메타데이터만 표시함을 확인했습니다.
  - 빌드된 백엔드 `bug-report` ZIP에 `diagnostics/wind3_release_diagnostics.txt`가 포함되고 `.exe`/`.dll` 엔트리가 없음을 확인했습니다.
  - 원격 릴리즈 asset 다운로드 해시가 로컬 ZIP 해시와 일치함을 확인했습니다.

## beta-20260608-v4 대비 변경사항

* 오류 보고 ZIP 경량화
  - `오류 보고 ZIP`은 더 이상 DLL 파일 본문을 ZIP에 포함하지 않습니다.
  - `d3d9.dll`, `dinput8.dll` 등 DLL 식별에는 파일명, 크기, 수정 시각, SHA-256 메타데이터를 사용합니다.
  - DLL 메타데이터는 `bug_report_summary.txt`와 `bug_report_manifest.json`의 `metadata_only` 항목에 기록됩니다.
  - 로그, SAVE, runtime policy/manifest, selected analysis reports는 계속 포함합니다.
  - `WIND3.EXE`, 모든 `.exe`, `.zip`, DLL 파일 본문은 제외합니다.

* 패키지 검증
  - ZIP SHA-256: `3D997BA55DD40AB2F3BA6ADB3E5C6C31691D4ED64610634DE057011A0DFB4E86`.
  - clean/temp install gate에서 `status -> apply -> status -> apply -> save-apply -> save-restore -> restore` 모두 return code `0`을 확인했습니다.
  - 적용된 root `d3d9.dll` SHA-256은 `A1EF7723E7C3F70947EC656C49EC4E5DB927321A0647EE8E2D5E8EBF8412F5AF`입니다.

## beta-20260608-v3 대비 변경사항

* 런처 버전 안내 추가
  - `버전 안내` 버튼으로 현재 패키지 버전/tag, GitHub release repository, launcher/Lite/updater SHA-256, root `d3d9.dll`/`dinput8.dll`, `runtime_policy.ini` 해시를 확인할 수 있습니다.
  - 문제 제보 시 사용자가 설치한 패키지와 실제 적용 DLL 조합을 빠르게 대조할 수 있습니다.

* 오류 보고 ZIP 추가
  - `오류 보고 ZIP` 버튼은 package `_runtime/logs/wind3_bug_report_*.zip`을 생성합니다.
  - 포함: 로그, SAVE, DLL, runtime policy/manifest, selected analysis reports.
  - 제외: `WIND3.EXE`와 모든 `.exe` 파일.

* 세이브 검사/복구 UI 추가
  - `세이브 검사`는 현재 세이브가 현 버전 형식으로 읽히는지 검증합니다.
  - `세이브 복구`는 백업 기반 복원이 아니라 현재 세이브를 기준으로 현 버전 텍스트/아이템 이름 형식에 맞춰 동기화합니다.
  - 구조적으로 손상되거나 읽을 수 없는 세이브는 현재 세이브만으로 재구축하지 않고 중단합니다.

* 패키지 검증
  - ZIP SHA-256: `E7A584D06CF7F977D232BB7ADDB76858DA654CD3751593E4102BE8087654FEAF`.
  - clean/temp install gate에서 `status -> apply -> status -> apply -> save-apply -> save-restore -> restore` 전부 return code `0`을 확인했습니다.
  - 적용된 root `d3d9.dll` SHA-256은 `A1EF7723E7C3F70947EC656C49EC4E5DB927321A0647EE8E2D5E8EBF8412F5AF`입니다.

## beta-20260608-v2 대비 변경사항

* 런처 업데이트 handoff 보강
  - 런처의 `런처 업데이트` 버튼은 런처가 먼저 종료를 시작한 뒤 업데이터를 실행하도록 변경했습니다.
  - 기존 방식은 업데이터가 실행 중인 런처 EXE를 교체해야 해서 수정일자가 그대로 남거나 교체 실패가 애매하게 보일 수 있었습니다.

* 배포 bundle 전체 갱신
  - v3 업데이터는 원격 ZIP에서 런처 EXE 하나만 추출하지 않고 `wind3_korean_patch/` 전체를 임시 폴더에 풀어 `_runtime`, launcher, Lite launcher, README, `launcher_version.json`까지 갱신합니다.
  - 실행 중인 업데이터 EXE 자체는 직접 덮어쓸 수 없으므로 새 업데이터는 `.new` 파일로 남깁니다. 다음 전체 ZIP 설치부터는 updater도 최신 상태가 됩니다.
  - v1/v2 업데이터는 이 전체 bundle 갱신 로직이 없으므로, 이미 v1/v2를 받은 사용자는 v3 ZIP을 직접 다운로드해 한 번 새로 풀어 적용하는 것을 권장합니다.

* 런처 설정 보존
  - `패치 적용`이 `_runtime_patch/runtime_policy.ini`를 다시 설치할 때 기존 게임 폴더의 `window`, `input`, `automation`, `auto_action` 설정을 보존합니다.
  - 따라서 `자동 기능 사용 (/ 키, 실험용)`을 켜둔 뒤 패치를 다시 적용해도 `execute_enabled=1`, `execution_mode=auto_decide_ai_attack_score_probe`, `attack_select_enabled=1` 설정이 기본 OFF로 되돌아가지 않습니다.

* 패키지 검증
  - clean/temp install apply 검증에서 `d3d9.dll` SHA-256 `A1EF7723E7C3F70947EC656C49EC4E5DB927321A0647EE8E2D5E8EBF8412F5AF`, `dinput8.dll` 설치, `camera_down_key=K` 정책을 확인했습니다.
  - 기존 `auto_action` ON 정책을 가진 임시 설치에서 `패치 적용`을 재실행해 `Existing launcher runtime settings preserved.`와 ON 정책 유지, return code `0`을 확인했습니다.
  - v3 업데이터의 ZIP 추출/전체 bundle 교체 경로를 reflection으로 호출해 launcher, Lite launcher, `_runtime/release_runtime_backend.exe`, `launcher_version.json` 교체를 확인했습니다.
  - focused tests는 런처/업데이터 테스트 `95`개 OK, `1` skipped로 통과했고, launcher/updater C# 컴파일을 확인했습니다.

## beta-20260608-v1 대비 변경사항

* 새 PC 적용 패키지 누락 보강
  - 자동행동 포함 `d3d9.dll`을 final bundle과 런처 배포 자산에 다시 승격했습니다.
  - clean/temp install apply 검증에서 설치 후 `d3d9.dll` SHA-256이 `A1EF7723E7C3F70947EC656C49EC4E5DB927321A0647EE8E2D5E8EBF8412F5AF`임을 확인했습니다.
  - 입력 리맵 프록시 `dinput8.dll`이 설치되고, 기본 정책에 `keyboard_remap_enabled=1`, `camera_down_key=K`가 포함됨을 확인했습니다.

* `/` 자동행동 설정 저장 보강
  - 런처의 `자동 기능 사용 (/ 키, 실험용)` 체크박스를 켜면 `execution_mode=auto_decide_ai_attack_score_probe`, `execute_enabled=1`, `skill_record_noshow_execute_enabled=1`, `attack_select_enabled=1`까지 함께 저장합니다.
  - 체크박스를 끄면 자동행동 실행 계열 키가 다시 꺼지고 `execution_mode=dry_run`으로 돌아갑니다.
  - `[auto_action]`, `[automation]`, `[runtime_features]` 섹션을 고정 줄 번호가 아니라 섹션 prefix 기준으로 작성해 정책 파일 섹션이 겹쳐 쓰이지 않도록 했습니다.

* 패키지 검증
  - 새 ZIP을 깨끗한 임시 게임 폴더에 풀고 release backend `apply`를 실행해 return code `0`을 확인했습니다.
  - 빌드된 런처 EXE의 `RuntimePolicy.SetAutoActionEnabled(true/false)`를 reflection으로 호출해 실제 저장 결과를 확인했습니다.
  - focused tests는 런처 테스트 `95`개 OK, `1` skipped, 자동행동 정책 테스트 `35`개 OK, span guard 테스트 `51`개 OK로 통과했습니다.
  - Phase1C promotion asset 검증에서 `3`개 promotion asset이 `2031`개 description-control marker를 포함함을 확인했습니다.

## beta-20260604-v2 대비 변경사항

* 런처 업데이트 기능 추가
  - 별도 실행 파일 `Wind3 Korean Patch Updater.exe`를 배포 패키지에 포함했습니다.
  - 구버전 런처 사용자도 업데이터 EXE를 직접 실행해 새 런처를 받을 수 있습니다.
  - normal/Lite 런처에 `실험 버전 포함` 체크박스와 `런처 업데이트` 버튼을 추가했습니다.
  - 체크박스를 켜면 pre-release까지 포함한 최신 배포를 확인하고, 끄면 GitHub latest 배포를 확인합니다.

* 자동 기능 설정 노출
  - 런처 설정에 실험용 `자동 기능 사용 (/ 키, 실험용)` 체크박스를 포함했습니다.
  - 기본값은 꺼짐이며, 켜면 런처가 `[auto_action]` 정책을 작성합니다.
  - 자동 기능은 실험용 opt-in 기능이라 일반 실행 기본값은 바꾸지 않습니다.

* 버전 확인 정책 보강
  - `launcher_version.json`에 버전, 배포 저장소, asset 패턴, normal/Lite 런처 해시, 업데이터 해시를 기록합니다.
  - 현재 런처 버전을 신뢰할 수 없으면 다운로드 전에 사용자 확인을 받습니다.
  - 현재 버전이 최신이면 다운로드를 시도하지 않고 최신 상태 메시지만 표시합니다.
  - `launcher_version.json`이 없는 구버전 원격 ZIP은 업데이트 성공으로 처리하지 않습니다.
  - GitHub REST releases 응답 순서와 무관하게 non-draft 릴리즈 중 가장 높은 버전/날짜를 선택하도록 보정했습니다.

* 패키지 검증
  - 릴리즈 ZIP 안에 `launcher_version.json`, `Wind3 Korean Patch Updater.exe`, normal/Lite 런처가 포함되어 있음을 확인했습니다.
  - 업데이터/릴리즈 빌더 focused test를 통과했습니다.
