# 릴리즈 노트 (20260810-v7)

## 다운로드

- 배포 파일: `wind3-korean-patch-20260810-v7.zip`
- SHA-256: `762A30CAB4FC630824E4A87FC23DD3BE2D362FE844D7FD0C045D2F69EB7ED6BE`
- 파일 크기: `53132991` bytes
- 채널: pre-release

## 20260810-v3-release 대비 주요 변경사항

### 업데이트 테스트

- 패키지 경로가 끝 구분자로 끝날 때 backend 유효성 검사 인자가 손실되어 업데이트 확인이 중단되던 문제를 Windows 인자 규칙에 맞게 수정했습니다.
- pre-release 패키지가 자신의 채널 상태를 updater metadata에 기록하도록 복구하고, 버전·태그·배포 채널이 서로 다르면 패키지를 거부하도록 검증을 강화했습니다.
- 이 pre-release는 수정된 updater가 다음 테스트 pre-release를 자동으로 조회·검증·교체하는지 확인하는 첫 번째 설치 기준점입니다.

### 런처 표시

- Full/Lite 런처 우상단에서 고DPI 환경에도 전체 버전 문자열을 우선 표시합니다.
- 게임 패치 데이터와 번역 내용은 latest stable 20260810-v3-release와 동일합니다.
