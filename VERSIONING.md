# 버전명 정책

이 저장소의 릴리즈 버전은 사용자가 받은 배포 파일을 쉽게 식별하고, 문제가 생겼을 때 같은 배포본을 다시 찾을 수 있도록 정합니다.

## 기본 형식

이번 정책부터 안정화 release와 개발 테스트용 pre-release를 버전명에서 구분합니다.

```text
YYYYMMDD-vN-release
YYYYMMDD-vN
```

예시:

```text
20260609-v1
20260609-v2
20260609-v2-release
```

- `YYYYMMDD`: 배포일입니다.
- `vN`: 같은 날짜에 다시 배포할 때 1부터 증가시킵니다.
- `YYYYMMDD-vN-release`: 개발자 테스트가 끝난 안정화 release입니다.
- `YYYYMMDD-vN`: 실험적 기능이 포함될 수 있는 개발 테스트용 pre-release입니다.
- 안정화 release만 버전명 맨 뒤에 `-release`를 붙입니다.
- pre-release 버전명에는 `pre-release`, `beta`, `test` 같은 타입 단어를 붙이지 않습니다.
- `YYYYMMDD-vN`과 `YYYYMMDD-vN-release`는 같은 base version입니다. `-release`는 더 높은 패치 번호가 아니라 공개 상태/채널 표시입니다.
- pre-release 이후 ZIP 내용, SHA-256, 런처 동작, 릴리즈 노트, 사용자 안내 문서가 바뀌면 같은 `vN-release`로 올리지 않고 `vN`을 증가시킨 뒤 release로 배포합니다.

## 배포 파일 이름

버전명은 Git tag, GitHub Release 제목, `launcher_version.json`, README, 체크섬, 릴리즈 ZIP 이름에 그대로 반영합니다.

```text
wind3-korean-patch-YYYYMMDD-vN-release.zip
wind3-korean-patch-YYYYMMDD-vN.zip
```

GitHub Release 제목/name은 반드시 버전명만 사용합니다. 제품명, `Latest`, `Hotfix`, 한국어 설명 같은 접두사나 접미사를 붙이지 않습니다.

## release와 pre-release의 의미

- release는 개발자 테스트가 끝난 안정화 버전입니다. GitHub에서는 `prerelease=false`, `draft=false`, latest 상태로 공개합니다.
- pre-release는 실험적 기능이 포함된 개발 테스트용 릴리즈입니다. 테스트 중에만 `prerelease=true`, `draft=false`로 둘 수 있습니다.
- 안정화 release를 올릴 때 같은 테스트 주기의 pre-release는 draft로 전환해 비공개 처리합니다.
- 같은 base version의 pre-release와 release는 동일한 변경 단위를 가리킵니다. 안정화 과정에서 배포물이 바뀌면 새 base version을 만듭니다.

## 릴리즈 노트 정책

- pre-release 릴리즈 노트에는 직전 버전 대비 변경사항만 적습니다.
- latest 안정화 release 릴리즈 노트에는 이전 latest 안정화 release 이후 현재 release까지의 모든 pre-release 변경사항을 누적해서 적습니다.
- 기존 릴리즈 노트의 섹션 양식과 검증 근거 형식을 유지합니다.
- 변경사항, 검증 결과, SHA-256, clean/temp gate 같은 증거는 실제 확인한 내용만 적습니다.

## 언제 번호를 올리는가

같은 날짜에 아래 항목 중 하나라도 바뀌면 `vN`을 올립니다.

- 배포 ZIP 내용
- SHA-256 체크섬
- 런처 동작
- 번역/패치 데이터
- 사용자에게 영향을 주는 안내 문서
- GitHub release/prerelease/draft 상태나 릴리즈 노트 범위

문서 오타처럼 사용자 동작이나 배포 ZIP 식별에 영향이 없는 수정은 같은 릴리즈를 다시 만들지 않고 다음 배포에 포함합니다.

## 커밋 메시지 정책

릴리즈 저장소 커밋 메시지는 참조 커밋과 같은 구조를 사용합니다.

```text
런처 패키지를 EXE 엔트리포인트로 정리

- 개발용과 배포용 런처의 최종 진입점을 EXE로 고정
- 배포 EXE가 PowerShell bootstrap 없이 bundled Python backend를 직접 호출하도록 정리
- csc 직접 빌드와 ZIP 산출물 검증, active note 갱신을 추가
```

- 제목은 첫 줄에 한국어로 씁니다.
- 본문은 `- ` bullet line으로 변경사항을 요약합니다.
- 본문은 가능하면 `2-4`줄로 씁니다.
- 본문에 별도 헤딩을 만들지 않습니다.
- 본문 bullet 사이에 빈 줄을 넣지 않습니다. 빈 줄은 Git의 제목/본문 구분선 하나만 둡니다.
- `hotfix`, `release update`, `notes fix`처럼 모호하거나 영어로 된 제목은 피합니다.

## 검증 정책

릴리즈 상태를 보고하기 전에는 GitHub의 실제 상태를 확인합니다.

- tag 이름
- GitHub Release 제목/name
- `draft`
- `prerelease`
- latest 여부
- asset 이름
- asset SHA-256

로컬 ZIP을 만들었다는 사실만으로 공개 release 상태를 확정해서 말하지 않습니다.

## 기존 beta 버전

`beta-20260609-v2`까지의 `beta-*` 태그는 과거 배포 식별용 legacy 버전명으로 유지합니다.

`beta-20260609-v2` 이후 새 배포에는 `beta-*`를 사용하지 않습니다.
