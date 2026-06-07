# 릴리즈 노트 (beta-20260608-v3)

## 다운로드

- 배포 파일: `wind3-korean-patch-beta-20260608-v3.zip`
- SHA-256: `43EF5C0B0F95440FA96828DFA4BEFFF21F057DCD77B1445F19959A6AA0267BD8`
- 파일 크기: `22,838,458` bytes

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

## beta-20260604-v1 대비 변경사항

* 진단 로그 명령줄 노출 완화
  - `진단 정보 저장`이 Windows Application 이벤트 로그를 수집할 때 `CmdLine` / `CommandLine` 원문을 `<redacted>`로 가립니다.
  - 로컬 검증이나 채팅 도구가 남긴 reflection 검사 명령이 이벤트 로그에 있어도 진단 파일에 그대로 복사되지 않도록 했습니다.
  - `Assembly]::LoadFile`, `GetAssignableInputKeyOptions`, `IsAssignableInputKeyName`가 들어간 로컬 reflection 검증 이벤트는 진단 로그에서 제외합니다.
  - 이 변경은 런처가 해당 PowerShell 명령을 실행한다는 의미가 아니라, 외부 이벤트 로그 원문을 진단 파일에 담을 때 생길 수 있는 오해와 민감 정보 노출 가능성을 줄이기 위한 보강입니다.

* 패키지 검증
  - 최종 공개 패키지 빌드 audit에서 `patch_count=15`, `payload_count=15`, `exact_patched_count=15`, `missing_count=0`을 확인했습니다.
  - clean/temp install gate는 `status -> apply -> status -> apply -> save-apply -> save-restore -> restore` 순서로 모두 return code `0`을 확인했습니다.
  - 최종 focused suite는 `98` tests OK, `1` skipped로 통과했습니다.

## beta-20260602-v3 대비 변경사항

* 키 설정 추가
  - normal launcher와 Lite Launcher에 `키 설정` 버튼을 추가했습니다.
  - 텐키리스 키보드에서도 카메라 이동, 확대/축소, 좌우 회전, 기울임을 설정할 수 있습니다.
  - 기본값은 이동 `I/J/K/L`, 확대/축소 `=`/`-`, 좌우 회전 `U/O`, 기울임 `[`, `]`, `;`, `'`입니다.
  - 이미 다른 기능에 배정된 키를 선택하면 기존 기능의 배정은 자동으로 해제됩니다.
  - 각 항목에는 `해제` 버튼이 있어 해당 기능의 추가 키 매핑을 비울 수 있습니다.

* 전투 HUD 인물명 보강
  - 전투 HUD에서 `賽連軍`이 고정폭 DATA 한계 때문에 그대로 보이던 문제를 보강했습니다.
  - 이제 `PersonName` getter의 engine `SetString` 경로를 통해 `세이렌군`으로 표시됩니다.
  - 이 경로는 exact old-byte 확인 후에만 적용되도록 제한했습니다.

* 배포 런처와 런타임 패키지 보강
  - 배포 런처의 입력 설정, Lite Launcher, README, runtime policy 기본값을 같은 패키지 기준으로 동기화했습니다.
  - 배포 백엔드 출력은 UTF-8 우선, CP949 fallback으로 읽어 한국어 로그가 깨질 가능성을 줄였습니다.
  - 복원 상태 파일과 세이브 보정 manifest의 UTF-8 BOM 처리 경로를 보강했습니다.
  - `dinput8.dll` 입력 프록시가 카메라 이동 외에 확대/축소, 좌우 회전, 기울임 키까지 런처 정책에서 읽어 리매핑합니다.

* 텍스트/세이브 보정 누적 반영
  - person/job native map split, battle unit `PersonName` native route, shop description getter route, NPC/person-name cache 보정, save/worldmap cache 보정 경로를 현재 패키지 기준으로 반영했습니다.
  - 일부 기존 세이브에 남을 수 있는 저장 제목, 아이템명, 월드맵 지명, NPC 라벨 캐시 보정 경로를 유지합니다.
  - `d3d9.dll` 런타임 payload는 SHA-256 `D77D87690414F2E628CCF3EAD50F5FEEB377B511CDD1ED0E3A0015D85FED3073` 기준입니다.

* 패키지 검증
  - 최종 공개 패키지 빌드 audit에서 `patch_count=15`, `payload_count=15`, `exact_patched_count=15`, `missing_count=0`을 확인했습니다.
  - clean/temp install gate는 `status -> apply -> status -> apply -> save-apply -> save-restore -> restore` 순서로 모두 return code `0`을 확인했습니다.
  - 최종 focused suite는 `98` tests OK, `1` skipped로 통과했습니다.
  - 릴리즈 ZIP 안의 README에 `키 설정`, `Lite Launcher`, `텐키리스` 안내가 들어있는 것을 확인했습니다.

## beta-20260602-v2 대비 변경사항

* 배포 런처 레이아웃 개선
  - 이미지가 포함된 네이티브 EXE 런처 화면으로 정리했습니다.
  - 게임 실행 버튼을 더 우선적으로 배치하고, 세이브 관리와 지원 기능은 기능 그룹을 유지한 채 재배치했습니다.

* 저해상도용 Lite Launcher 추가
  - 낮은 해상도 환경에서도 주요 버튼을 누를 수 있도록 `Wind3 Korean Patch Lite Launcher.exe`를 추가했습니다.
  - 라이트 런처는 버튼 중심의 밀도 높은 화면으로 구성했습니다.

* 진단 정보 저장 보강
  - 진단 보고서에 런처 오류, 백엔드 stdout/stderr, 패치 상태, 주요 파일 해시, runtime_policy.ini, hook 로그, Windows Application 이벤트 로그가 함께 기록됩니다.
  - 오류 제보 시 단순 설정 기록보다 실제 실행 실패 원인을 확인하기 쉬워졌습니다.

* 실행 로그 자동 정리
  - 실행별 로그가 무한정 쌓이지 않도록 최근 실행/오류/진단 로그만 보존합니다.
  - 오래된 로그는 런처 실행 및 진단 정보 저장 과정에서 자동으로 정리됩니다.

## beta-20260602-v1 대비 변경사항

* 전투 시작 전 안내 문구 축약
  - 출격 인물 선택 안내가 화면을 넘지 않도록 짧게 다듬었습니다.
  - 화면에는 `출격 인물을 선택하고 Go!!를 누르세요.` 기준으로 표시됩니다.

* 직업 표기 개선
  - 베리카의 직업 표기 `낫소녀`를 `사신소녀`로 정리했습니다.
  - 짧게 축약되던 `늑인`, `충족`, `보물` 표기는 각각 `늑대인간`, `곤충족`, `보물상자`로 보이도록 보강했습니다.

## beta-20260526-v1 대비 변경사항

* 런처 실행 파일 변경
  - 압축 해제 후 실행 파일이 `Wind3 Korean Patch Launcher.cmd`에서 `Wind3 Korean Patch Launcher.exe`로 바뀌었습니다.
  - 패치 적용 시 세이브 패치가 자동으로 함께 실행됩니다. 필요하면 런처에서 세이브 패치와 세이브 복원을 따로 다시 실행할 수도 있습니다.

* 월드맵과 시나리오 지명 표기 정리
  - 월드맵 라벨과 시나리오 안의 지명 표기를 같은 기준으로 맞췄습니다.
  - `성아리온성` / `성아리온평원`은 `성 아리온 성` / `성 아리온 평원`으로 띄어쓰기를 정리했습니다.
  - `요시아북광산` / `요시아남광산`은 `요시아 북광산` / `요시아 남광산`으로 정리했습니다.
  - `우드삼림`은 `우드 숲`, `웨디진`은 `비디 마을`, `니시므`는 `니시무 마을`, `헤미촌`은 `헤르미 마을`로 정리했습니다.
  - `샛별성당`, `심수미궁`, `적갈사막`, `장마굴`, `세렌`, `레나`, `조음안`, `설랑애`, `흑우화산` 등은 각각 `샛별 성당`, `심연의 미궁`, `붉은전갈 사막`, `봉마굴`, `세이렌`, `레이나`, `파도소리 해안`, `설랑 절벽`, `흑익 화산`처럼 더 자연스러운 표기로 정리했습니다.
  - 그 외 성, 항구, 산길, 마을, 해변, 습지, 다리 이름의 띄어쓰기와 접미사 표기를 함께 다듬었습니다.

* 저장/불러오기 화면 제목 보강
  - 저장/불러오기 화면의 챕터 제목과 전투 제목을 더 자연스러운 문장형 표기로 정리했습니다.
  - 예: `서장  최후원죄휘장` 계열은 `서장  마지막 원죄의 휘장`, `5장  빙화전쟁` 계열은 `5장  얼음과 불의 전쟁`, `최종장  선택` 계열은 `6장  선택` 기준으로 정리됩니다.
  - `세렌해방전선` / `세련해방전선`, `흑깃 화산`, `프니`, `요염의 해역의 사신`처럼 이전 저장 데이터에 남을 수 있던 제목 표현도 새 표기로 보정됩니다.
  - 로드 화면의 전투 행 접두사는 기존 `전투 N` 표기에서 게임의 저장 행과 맞는 `Battle N` 표기로 통일했습니다.

* 아이템/장비/스킬/보석 텍스트 갱신
  - 무기, 방어구, 도구, 스킬, 보석 데이터의 한국어 이름과 설명을 최신 검수본으로 갱신했습니다.
  - 기존 세이브에 저장된 보유 아이템 이름도 패치 적용 시 현재 번역 기준으로 함께 보정됩니다.

* 상태/정보 화면 문구 보강
  - 상태/정보 화면에서 보이는 일부 고정 UI 문구가 배포 패키지에 포함되었습니다.

* 글꼴과 이미지형 텍스트 자산 갱신
  - 한글 글꼴과 이미지형 텍스트 자산을 현재 번역 데이터에 맞춰 갱신했습니다.
  - 챕터/전투/지도 주변에서 이미지나 텍스처로 표시되는 일부 텍스트가 최신 패키지 기준으로 맞춰졌습니다.

## beta-20260520-v1 대비 변경사항

* 아이템 텍스트 확장 경로 배포 반영
  - 라이브에서 확인한 아이템 이름과 설명 확장 surface를 durable source, 빌드 DLL, launcher asset, release ZIP 검증 경로로 승격했습니다.
  - item Name SetString 경로와 description/control 경로를 분리해 검증합니다.
  - trailing space padding이 있는 설명 surface는 임의로 trim하지 않고 exact-byte variant로 보존합니다.

* 창모드 멀티태스킹 개선
  - 전체 창모드와 창 모드에서 Alt+Tab 이후 작업표시줄 뒤로 밀리는 문제를 줄였습니다.
  - 게임 창이 비활성일 때 마우스 중심점 고정, ClipCursor, SetCursor 계열 점유 동작을 완화했습니다.
  - 포커스 복귀 직후 큰 마우스 delta가 들어가지 않도록 중심점 재동기화 보정을 추가했습니다.

* 비활성 상태 화면 갱신 옵션
  - `runtime_policy.ini`의 `inactive_pause_enabled=0` 설정으로 게임 창이 비활성일 때도 렌더 루프가 계속 돌도록 하는 런타임 보정을 추가했습니다.

* 해상도 설정 정리
  - 런처에서 전체 창모드, 창 모드, 독점 전체화면을 선택하고 해상도를 저장할 수 있게 했습니다.
  - 전체 창모드는 4:3 기준의 integer 스케일과 fit 스케일을 선택할 수 있습니다.
  - 창 모드는 현재 모니터 작업 영역 안에 들어가는 주요 4:3 해상도 프리셋을 제공합니다.
  - WindConfig 호환 레지스트리 값(`IsFullscreen`, `CreationWidth`, `CreationHeight`)을 런처 실행 전에 반영합니다.

* 배포 런처 UI 정리
  - 배포용 런처에서는 개발용 런타임 수동 제어를 숨기고, 게임 실행, 해상도 설정, 진단 정보 저장 중심으로 정리했습니다.
  - 개발용 런처에는 기존 고급 런타임 설정을 남겨 실험과 회귀 확인이 가능하도록 했습니다.

* 로드 직전 멈춤 완화
  - 기본 safe 런타임에서는 source-text 복구용 `prepare-load`를 실행하지 않도록 조정했습니다.
  - 로드 직전 오래 대기하던 경로를 줄이고, 로드 후 필요한 UI 라벨 재적용만 다시 예약합니다.

* 런타임 라벨 적용 비용 축소
  - 캐릭터 정보창과 스킬 화면 라벨을 적용한 뒤 같은 영역을 다시 dry-run 검증하던 중복 스캔을 릴리즈 기본 경로에서 제거했습니다.
  - 라벨 적용 보고와 패키지 검증은 유지하면서, 실제 실행 중 로드 후 처리량을 줄이는 쪽으로 정리했습니다.

* 배포 환경 런타임 helper 경로 수정
  - 깨끗한 설치 환경에서 런타임 패치 helper가 개발용 `analysis_out` 폴더를 찾다가 실패하던 문제를 수정했습니다.
  - 이제 패키지에 포함된 `_runtime/worker/analysis_out`의 helper 실행 파일을 사용합니다.

* 스킬/정보창 잔여 라벨 적용 경로 보강
  - 스킬 화면의 `잔여점수`, 캐릭터 정보창의 `설명`, `소유물품` 라벨이 기본 safe 런타임 패치 경로에 포함되도록 보강했습니다.
  - 캐릭터 정보창의 스탯/장비 슬롯 라벨이 일부 환경에서 원문으로 남던 문제를 여러 차례 보강했습니다.

* 진단 로그 수집 범위 확대
  - `진단 정보 저장` 결과에 startup bridge 내부 로그, 런타임 패치 cycle report, worker stdout/stderr 로그를 추가했습니다.
  - 다른 PC에서만 실패하는 경우에도 어느 적용 단계에서 실패했는지 더 빨리 확인할 수 있습니다.

* 다른 PC에서의 런타임 DLL 로드 안정성 보강
  - 패치용 `d3d9.dll`의 외부 C 런타임 의존성을 제거해, PC 환경 차이로 DLL이 로드되지 않을 가능성을 줄였습니다.

* 런타임 기능 설정 방식 개선
  - `runtime_policy.ini`의 `[runtime_features]` 섹션에서 owner trace/rewrite, 모듈 UI 패치, 진단용 프로브 같은 런타임 기능을 제어할 수 있게 했습니다.
  - 같은 종류의 기능 전환을 위해 매번 DLL을 새로 빌드해야 하는 부담을 줄였습니다.

* 릴리즈 패키징 검증 강화
  - 릴리즈 빌더가 의도한 런타임 DLL인지 확인한 뒤 패키징하도록 검증을 추가했습니다.
  - live에서 성공한 surface가 durable source, 빌드 DLL, launcher asset, release ZIP에 같은 old/new byte와 site 경로로 들어갔는지 확인하는 기준을 강화했습니다.

* 번역 품질과 미번역 대응
  - 주요 대사의 표현, 말투, 용어를 1차로 정리해 읽기 흐름을 개선했습니다.
  - 플레이 중 노출되던 UI, 이름, 항목 텍스트 일부에 한국어 대응을 추가했습니다.
  - 이미지로 표시되는 챕터 제목 일부를 한국어로 교체했습니다.
  - Steam 설치 경로의 `Wind Fantasy 3` 폴더를 자동 감지하는 기능을 추가했습니다.

## 사용 전 주의사항

- 이 배포 파일은 게임 본편이나 원본 게임 리소스를 포함하지 않습니다. 사용자가 보유한 Wind Fantasy 3 설치본이 필요합니다.
- 스팀 클라이언트 기준 2025-08-12 버전을 기반으로 개발했습니다. 이외 버전에서는 패치 적용 및 동작을 보장하지 않습니다.
- 패치 적용 전에는 게임을 완전히 종료해 주세요. 게임이 실행 중이면 일부 파일 교체가 실패하거나 적용 결과가 일관되지 않을 수 있습니다.
- 중요한 저장 데이터는 패치 적용 전에 별도로 백업하는 것을 권장합니다.
- 일부 기존 세이브의 월드맵 라벨과 저장 제목은 저장 시점에 따라 이전 표기가 남을 수 있습니다. 패치 적용 후 해당 슬롯에서 다시 저장하거나 새 진행 데이터에서는 정리된 표기를 기준으로 표시됩니다.
- 이번 배포는 pre-release입니다.
- 이 패치는 비공식 개인 한국어 패치입니다. 모든 PC 환경에서 동일하게 동작한다고 보장하지 않습니다.
- 일부 이미지형/헤더형 UI 문구와 몇몇 visible-proof 체크포인트는 아직 후속 보강 대상일 수 있습니다.
