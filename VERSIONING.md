# Wind3 버전·릴리즈 정책

이 문서는 Wind3 공개 배포의 사람이 읽는 정본이다. 기계 정본은 개발
저장소의 `tooling/release/release_policy.json`과 release 저장소의
`.release/policy.json`에 byte-identical하게 두며, 둘이 다르면 게시를 중단한다.

## 버전 형식

```text
YYYYMMDD-vN          # 검증용 pre-release
YYYYMMDD-vN-release  # 검증을 마친 stable/latest
```

- `YYYYMMDD`는 새 후보를 만든 날짜다.
- 같은 날짜에 후보를 다시 만들면 `vN`을 반드시 증가시킨다.
- `YYYYMMDD-vN`과 `YYYYMMDD-vN-release`는 한 후보의 pre/stable 채널이다.
- 이미 GitHub tag나 Release에 사용된 버전은 삭제 여부와 무관하게 재사용하지
  않는다.
- ZIP 바이트, SHA-256, 런처 동작, 번역·패치 데이터, 공개 문서, Release
  본문 또는 채널 의미가 바뀌면 새 `vN`으로 다시 시작한다.

## immutable artifact와 stable 이름

공개된 pre-release는 GitHub Immutable Releases가 태그와 자산을 잠근다.
따라서 stable은 기존 Release를 수정하지 않고 별도 Release와 tag로 만든다.

- pre-release tag/name: `YYYYMMDD-vN`
- stable tag/name: `YYYYMMDD-vN-release`
- pre-release 자산: `wind3-korean-patch-YYYYMMDD-vN.zip`
- stable 자산 표시 이름:
  `wind3-korean-patch-YYYYMMDD-vN-release.zip`
- stable 자산의 바이트는 GitHub에서 재다운로드해 검증한 pre-release
  자산과 SHA-256까지 동일해야 한다.
- 동일 바이트이므로 ZIP 내부 `launcher_version.json`, 패키지 README와
  패키지 릴리즈 노트의 artifact version은 `YYYYMMDD-vN`을 유지한다.
  `-release`는 GitHub의 안정화 채널 이름이지 새 바이너리 세대가 아니다.

stable 준비 중 ZIP 내부 버전이나 문서를 다시 쓰거나 재압축하면 동일 후보가
아니다. 새 `vN` pre-release부터 다시 만든다.

## 릴리즈 노트 기준선

모든 새 pre-release와 그 stable Release의 비교 기준은 준비 명령을 실행한
시점의 GitHub `/releases/latest`가 반환한 직전 latest 안정판 하나다.

- 준비 시 `release_id`, tag, tag target commit을 release plan에 함께 봉인한다.
- 게시 직전 live `/releases/latest`가 봉인값과 달라지면 해당 후보를 폐기하고
  새 버전으로 다시 준비한다.
- 기존 `RELEASE_NOTES.md` 본문을 이어붙이거나 과거 릴리즈 섹션을 복사하지
  않는다.
- release plan의 이번 변경 section만 결정적으로 렌더링한다.
- 제목과 2단계 heading은 기계 정본의 형식과 byte-for-byte 일치해야 한다.
- 공개 본문과 패키지 문서에는 개발 정본 형식, 개발 폴더, 내부 build/artifact
  식별자나 개발 의존성을 적지 않는다.
- 실제 확인하지 않은 기능, 검증 결과, 해시 또는 proof는 적지 않는다.

즉 `20260702-v1-release`가 현재 latest라면 이후 후보의 노트는
`20260702-v1-release 대비 주요 변경사항`만 포함한다. 그보다 오래된 릴리즈
노트를 다시 붙이지 않는다.

## 강제 상태기계

```text
live latest snapshot + clean source main
  -> release plan 봉인
  -> Stage 5 package
  -> Stage 6 clean/temp + feature-closure proof
  -> release 저장소 PR + 필수 CI
  -> YYYYMMDD-vN draft 생성
  -> draft 본문/자산 digest/API actor readback
  -> immutable pre-release 공개
  -> GitHub 자산을 새 경로로 재다운로드
  -> 다운로드본 clean/temp + runtime/user proof
  -> 사용자의 별도 stable 승인
  -> YYYYMMDD-vN-release 새 PR + 새 draft
  -> pre-release와 동일 digest 및 proof readback
  -> immutable stable/latest 공개
```

pre-release와 stable은 논리적으로 순차 승격하지만 GitHub에서는 서로 다른
Release다. 공개된 pre-release를 draft로 되돌리거나 stable로 편집하지 않는다.

## canonical 명령 경계

1. `python -m tooling.release.publication_guard prepare-plan ...`
2. `python -m tooling.xlsx_truth_pipeline.cli package --release-plan ...`
3. `python -m tooling.release.candidate_stage stage-prerelease ...`
4. release 저장소 PR과 `validate`, `base-policy` check
5. `python -m tooling.release.publication_guard create-prerelease-draft ...`
6. `python -m tooling.release.publication_guard publish-prerelease ...`
7. 재다운로드 proof와 별도 사용자 승인 후
   `candidate_stage stage-stable`
8. 새 stable PR과 두 check
9. `publication_guard create-stable-draft`
10. `publication_guard publish-stable`

GitHub Release 생성·업로드·게시·회수는 이 guard가 사용하는 전용
`jhf-dev` API 자격증명으로만 수행한다. 브라우저, Computer Use, raw
`gh release`, 다른 계정의 토큰, 임의 policy/settings 파일은 정상 경로가
아니다.

## 절대 금지

- `absent -> published pre-release` 또는 `absent -> stable/latest` 직행
- draft 없이 처음부터 공개
- 공개된 Release의 tag, 자산, 본문 또는 채널을 in-place 수정
- 로컬 live 폴더나 업로드 전 ZIP을 GitHub 재다운로드 proof로 대체
- 원격 pre-release asset ID와 연결되지 않은 redownload proof
- 사용자 승인 없이 stable/latest 게시
- release 저장소 main 직접 push, force push, tag 이동·삭제
- `earlydreamer` 계정으로 `jhf-dev/wf3-kr-release` commit/PR/push/Release 생성
- immutable 또는 ruleset을 끈 상태에서 게시

## 계정과 커밋

- 개발 저장소: `earlydreamer`
- 공개 release 저장소: author와 committer 모두
  `jhf-dev <285839567+jhf-dev@users.noreply.github.com>`
- release 저장소 변경은 non-main branch -> PR -> 필수 check -> rebase merge
  순서만 허용한다.
- commit 제목은 한국어 한 줄, 빈 줄 하나, `- ` 한국어 bullet 2~4줄로 쓴다.
  attribution trailer와 bullet 사이 빈 줄은 넣지 않는다.

## proof와 receipt

- release plan은 live latest와 source commit, 이번 변경 section을 묶는다.
- Stage 6 proof는 plan hash, build/artifact ID, ZIP 이름·크기·digest,
  directory/ZIP clean-temp, 모든 런처 기동, F3 marker closure를 묶는다.
- draft와 publish mutation 전에 만료 시간이 있는 authorization receipt를
  먼저 append하고, 같은 계정의 API readback 뒤 postcondition receipt를
  hash chain에 append한다.
- 다른 version, release ID, body hash, asset digest 또는 commit의 receipt는
  재사용할 수 없다.
- stable redownload proof는 live immutable pre-release의 release ID와 asset
  ID에 결속되어야 한다.

## break-glass

공개 Release 삭제, latest 회수, ruleset 변경, immutable 설정 변경은 정상
publication 명령에 넣지 않는다. 사고 시 먼저 자동 업데이트 영향을 차단하고
대상 Release/tag/asset/body/해시를 보존한 뒤 별도 incident 기록과 사용자
승인을 받아 수행한다. 같은 tag나 version은 다시 쓰지 않고 수정본은 새
`vN` pre-release부터 시작한다.

개인 계정 소유 저장소에서는 owner가 ruleset 자체를 바꿀 수 있으므로 기술적
절대 권한 분리는 불가능하다. 현재 통제는 실수와 일반 경로 우회를 강하게
차단하지만, 장기적으로는 조직 소유 저장소와 non-admin GitHub App publisher,
별도 reviewer가 더 강한 경계다.

## 최초 governance bootstrap

최초 trusted-base workflow를 main에 넣는 PR은 candidate가 자기 validator를
제공하므로 일반 PR과 같은 방식으로 자동 병합하지 않는다.

- 개발 저장소 main에 release PR 전체 diff의 경로와 SHA-256을 묶은
  `release_bootstrap_manifest.json`이 먼저 커밋·푸시되어 있어야 한다.
- release guard는 그 manifest, 두 저장소 policy/settings 사본, release PR
  head, source remote main, 전용 계정, 전체 필수 테스트와 standalone
  validator를 다시 검사한다.
- 그 뒤 생성된 30분짜리 일회성 challenge 문구를 사용자가 그대로
  회신해야만 bootstrap merge가 허용된다.
- bootstrap은 `base-policy`가 main에 생긴 뒤 자동으로 금지된다. 병합 직후
  canary PR에서 `validate`와 `base-policy`의 exact head-SHA 성공을 확인한
  다음에만 ruleset을 활성화한다.

## private source repository blocker

개발 저장소와 공개 release 저장소의 credential은 같은 프로세스에 함께
싣지 않는다. source 검사는 별도 `earlydreamer` 전용 프로세스,
release mutation은 `jhf-dev` 전용 프로세스가 담당한다.

- private source의 release-tag ruleset desired state는
  `source_github_settings.json`으로 별도 관리한다.
- source ruleset exact audit, tag target, source actor 중 하나라도 확인되지
  않으면 release plan 준비부터 중단한다.
- release-event audit가 private source tag를 확인할 때는 owner token이
  아니라 별도 read-only GitHub App installation token을 사용한다.
- 현재 private 저장소 ruleset API가 GitHub Pro 업그레이드 또는 공개 전환을
  요구하며 403을 반환하므로, 이 조건이 해결되고 read-only App이 설정되기
  전에는 새 publication이 정상적으로 차단된다. 로컬 훅만으로 대체하지 않는다.

## legacy

`beta-20260609-v2`까지의 `beta-*` tag와 machine governance 이전에 공개된
`20260725-v2`는 과거 식별용으로만 남긴다. 기존 mutable Release를 새 정책에
맞는 후보라고 승격하거나 in-place 수정하지 않는다.
