# Licenses and Attribution

이 문서는 저장소와 GitHub Release에 올라가는 문서 기준의 라이선스/권리 고지입니다.

## 요약

이 저장소는 Wind Fantasy 3 한국어 패치 배포 패키지와 관련 고지 문서를 관리합니다.

Wind Fantasy 3 게임 본편, 실행 파일, 원본 리소스, 상표, 캐릭터, 텍스트, 이미지, 음악, 영상 등 원저작물의 권리는 해당 권리자에게 있습니다. 이 프로젝트는 비공식 현지화 패치이며 원저작권자와 제휴하거나 승인받은 공식 배포물이 아닙니다.

## 저장소 자체 코드와 문서

현재 이 저장소의 자체 코드와 문서에는 별도 오픈소스 라이선스 파일이 명시되어 있지 않습니다.

따라서 명시적인 별도 허가 없이 저장소 자체 코드/문서를 재배포, 재라이선스, 상업적으로 이용할 수 있다고 간주하지 마세요.

## 번역 워크북과 패치 데이터

배포 패키지의 패치 데이터는 한국어 번역문뿐 아니라 적용과 검증을 위해 원문 문자열, 식별자, 파일 경로, 레코드 구조 정보를 포함할 수 있습니다.

따라서 원저작물에서 파생된 정보가 포함될 수 있으며, 독립적인 자유 라이선스 자료로 취급하지 않습니다.

## 런처 패키지에 포함되는 구성요소

GitHub Release의 패치 zip에는 다음 범주의 파일이 포함됩니다.

- 자체 런처 스크립트와 패치 적용 스크립트
- Windows Python 런타임
- W3BP2 패치 파일
- 패치 적용용 보조 런타임 자산과 런타임 map
- 서드파티 고지와 라이선스 파일

릴리즈 zip은 전체 게임 설치본을 대체하지 않습니다. 사용자는 본인이 보유한 게임 설치 폴더를 런처에 지정해야 합니다.

## Python

런처 패키지는 Windows Python 런타임을 포함합니다.

- License: Python Software Foundation License
- Upstream: <https://docs.python.org/3.11/license.html>
- 런처 zip 내부 고지: `THIRD_PARTY_NOTICES.txt`

패키지 빌더는 사용 가능한 Windows Python 설치의 `LICENSE.txt`가 있을 경우 `licenses/python/` 아래로 복사하도록 설계되어 있습니다.

Python 런타임과 함께 다음 런타임 라이브러리가 포함될 수 있습니다.

- OpenSSL 3.0.13
  - License: Apache License 2.0
  - License file: `licenses/OpenSSL-3.0.13-LICENSE.txt`
- libffi
  - License: MIT
  - License file: `licenses/libffi-LICENSE.txt`
- Microsoft Visual C++ Runtime
  - License: Microsoft Visual Studio / Visual C++ Redistributable license terms
  - Notice file: `licenses/Microsoft-VC-Runtime-NOTICE.txt`

## Pretendard

패치 제작 과정에서 `Pretendard`와 `Pretendard Bold`를 사용한 생성 글리프/이미지 자산이 포함될 수 있습니다.

현재 배포 zip은 Pretendard 폰트 파일 자체를 번들하지 않습니다.

Pretendard는 SIL Open Font License 1.1로 배포되는 오픈소스 폰트입니다.

- License: SIL Open Font License 1.1
- Upstream: <https://github.com/orioncactus/pretendard>
- License text: <https://github.com/orioncactus/pretendard/blob/main/LICENSE>
- Reserved Font Name: `Pretendard`

Pretendard 폰트 파일을 별도로 재배포하는 경우에는 OFL 1.1 조건과 Reserved Font Name 조건을 따라야 합니다.

## Source Han Serif / Noto Serif CJK

일부 생성 이미지 리소스는 본명조 계열 폰트를 사용해 제작되었습니다. 본명조 계열은 Source Han Serif / Noto Serif CJK 계열로, SIL Open Font License 1.1에 따라 배포되는 오픈소스 폰트입니다.

현재 릴리즈 zip은 Source Han Serif / Noto Serif CJK 폰트 파일 자체를 번들하지 않습니다. 폰트는 일부 한국어 이미지 리소스를 렌더링하는 제작 과정에서 사용되었습니다.

- License: SIL Open Font License 1.1
- Upstream: <https://github.com/adobe-fonts/source-han-serif>
- License file: `licenses/SourceHanSerif-OFL-1.1-LICENSE.txt`

폰트 파일을 별도로 재배포하거나 수정본을 배포하는 경우에는 OFL 1.1 조건과 Reserved Font Name 조건을 따라야 합니다.

## 게임 원본 자산과 파생 패치 자산

이 프로젝트의 목적은 사용자가 보유한 Wind Fantasy 3 설치본에 한국어 패치 산출물을 적용하는 것입니다.

저장소와 릴리즈에는 전체 게임 실행에 필요한 원본 파일 세트를 포함하지 않습니다. 다만 패치용 DATA, W3BP2 패치 파일, 런타임 map 등은 원저작물의 문자열이나 데이터 구조에서 파생된 정보를 포함할 수 있습니다.

이러한 파일은 한국어 패치 적용과 검증 목적의 프로젝트 자료이며, 원저작물과 무관한 독립 오픈소스 자산으로 취급하지 않습니다.

## d3d9 shim과 런타임 도구

`d3d9.dll` shim, 메모리 스캔 보조 도구, 패치 스크립트는 이 프로젝트의 한국어 출력 실험과 패치 적용을 위해 제작된 도구입니다.

현재 별도 오픈소스 라이선스가 명시되어 있지 않으므로, 저장소 자체 코드와 동일하게 명시적 허가 없이 재배포/재라이선스/상업적 이용이 허용된 것으로 간주하지 마세요.

## 릴리즈 zip 내부 고지

릴리즈 zip에는 다음 파일이 함께 들어갑니다.

- `THIRD_PARTY_NOTICES.txt`
- `licenses/OpenSSL-3.0.13-LICENSE.txt`
- `licenses/libffi-LICENSE.txt`
- `licenses/Microsoft-VC-Runtime-NOTICE.txt`
- `licenses/Pretendard-OFL-1.1-LICENSE.txt`

이 문서는 GitHub 저장소용 상위 고지이며, 실제 zip 내부의 고지 파일도 함께 확인해야 합니다.
