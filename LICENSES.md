# 서드파티 오픈소스 및 배포 정책

이 문서는 Wind Fantasy 3 한국어 패치 저장소와 공개 최종 사용자 패키지의 권리 경계, 서드파티 구성요소 고지 원칙을 정합니다.

## 프로젝트 자료의 권리

Wind Fantasy 3 게임 본편, 실행 파일, 원본 리소스, 상표, 캐릭터, 텍스트, 이미지, 음악, 영상 등 원저작물의 권리는 해당 권리자에게 있습니다. 이 프로젝트는 비공식 현지화 패치이며 원저작권자와 제휴하거나 승인받은 공식 배포물이 아닙니다.

이 저장소가 작성한 런처·패치 코드, 번역문, 워크북, 런타임 데이터와 패치 데이터에는 별도 허가가 없는 한 오픈소스 라이선스가 부여되지 않습니다. 서드파티 라이선스는 각 서드파티 구성요소에만 적용되며, 프로젝트 자료나 게임 원본·파생 자산의 재배포 권한을 부여하지 않습니다.

## 공개 최종 사용자 패키지의 배포 경계

공개 ZIP은 정식 게임 설치본에 적용하는 차이 패치입니다.

- 게임 대상 파일은 W3BP2 차이 데이터로만 배포합니다.
- `WIND3.EXE`, 완전한 원본 게임 파일, 완전한 패치 게임 파일을 포함하지 않습니다.
- 사용자가 보유한 정식 설치본에서 대상 파일을 검증한 뒤 패치를 적용합니다.
- 원본 복구용 전체 게임 파일은 패키지에 넣지 않고, 적용 시 사용자 PC의 검증된 설치본에서 로컬 백업합니다.

이 경계는 저작권 보호를 위한 필수 배포 정책입니다. 개발 중 생성되는 완전한 빌드 산출물이나 원본 기준 파일은 공개 ZIP에 넣지 않습니다.

## 공개 패키지의 서드파티 구성요소

현재 공개 패키지 생성기는 다음 구성요소의 고지와 라이선스 전문을 함께 복사합니다.

| 구성요소 | 사용 범위 | 라이선스 또는 조건 | 패키지 내 전문 |
| --- | --- | --- | --- |
| CPython 3.11.8 | 내장 Python 런타임 | Python Software Foundation License | `licenses/CPython-3.11.8-LICENSE.txt` |
| PyInstaller 6.20.0 | Python 런타임 패키징과 bootloader | GPL v2 이상 + PyInstaller Bootloader Exception 등 upstream 전문 기준 | `licenses/PyInstaller-6.20.0-COPYING.txt` |
| OpenSSL 3.0.13 | 내장 Python 런타임의 암호화 라이브러리 | Apache License 2.0 | `licenses/OpenSSL-3.0.13-LICENSE.txt` |
| libffi | 내장 Python 런타임 구성요소 | MIT 계열 라이선스 | `licenses/libffi-LICENSE.txt` |
| Microsoft Visual C++ Runtime | Windows 실행 런타임 | Microsoft 재배포 조건, 오픈소스 아님 | `licenses/Microsoft-VC-Runtime-NOTICE.txt` |
| Pretendard | 게임용 한국어 글리프 생성 입력 | SIL Open Font License 1.1 | `licenses/Pretendard-OFL-1.1-LICENSE.txt` |

각 구성요소의 upstream 주소와 상세 고지는 패키지의 `THIRD_PARTY_NOTICES.txt`에서 확인할 수 있습니다.

## 폰트와 생성 글리프

저장소의 고정된 Pretendard 폰트는 게임용 한국어 글리프 패치를 재현 가능하게 생성하는 빌드 입력입니다. 공개 최종 사용자 ZIP에는 Pretendard 폰트 파일 자체를 넣지 않고, 그 폰트에서 생성한 글리프 패치만 포함할 수 있습니다.

Pretendard의 SIL Open Font License 1.1은 Pretendard와 그 파생 폰트에 적용됩니다. 게임 원본 폰트 리소스, 게임 이미지, 프로젝트 번역문이나 다른 패치 데이터까지 오픈소스로 전환하지 않습니다.

## 비배포 개발 도구

XLSX 런처는 저장소 내부에서 워크북 정본을 빌드·검증하는 개발 도구이며 공개 배포 대상이 아닙니다. 공개 최종 사용자 ZIP과 공개 서드파티 고지에는 XLSX 런처 및 그 개발용 Python 의존성을 포함하지 않습니다.

개발 환경에 `openpyxl`, `et_xmlfile`, Pillow 등이 설치되어 있더라도 이를 공개 패키지의 구성요소로 고지하지 않습니다.

## 패키지별 정본

특정 배포 세대에 실제 적용되는 고지는 그 패키지에 포함된 다음 파일이 정본입니다.

- `THIRD_PARTY_NOTICES.txt`
- `licenses/`
- `checksums.sha256`

이 저장소 문서와 패키지 내부 고지가 다르면 해당 바이너리 세대의 실제 포함 파일을 다시 감사하고, 누락을 수정한 새 버전으로 재빌드해야 합니다. 이미 배포된 ZIP을 같은 버전명으로 덮어쓰지 않습니다.
