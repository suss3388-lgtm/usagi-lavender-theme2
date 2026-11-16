# 우사기 라벤더 · Android 카카오톡 테마

이전 제작 자료의 우사기 그림과 카카오 공식 Android 26.9.0 샘플로 구성한 테마 프로젝트입니다.

## 2차 빌드 · 버전 1.1.0

Actions에서 **Build Usagi Lavender revision 2**의 APK 빌드 작업까지 성공한 실행을 선택하고, `usagi-lavender-v2-apk-번호`를 다운로드합니다. 이 빌드는 새 배경 PNG를 그대로 사용하고, 짧은 말풍선에서 캐릭터가 압축되지 않도록 고정 영역과 텍스트 여백을 조정하며, 선택한 하단 메뉴의 그림만 연보라 우사기로 바꿉니다. `usagi-lavender-v2-previews-번호`에는 배경·메뉴·말풍선 폭별 미리보기가 포함됩니다. 카카오톡 실제 화면의 크롭·여백은 기기에서 확인해야 합니다.

## 1차 APK 다운로드

1. [Actions](https://github.com/suss3388-lgtm/usagi-lavender-theme2/actions)에서 **Build Usagi APK from project ZIP**을 선택합니다.
2. APK 빌드 작업까지 초록색으로 완료된 최신 실행을 엽니다.
3. 하단 Artifacts에서 `usagi-lavender-apk-번호`를 다운로드합니다. GitHub 로그인이 필요합니다.
4. 압축을 풀고 `usagi-lavender-debug.apk`를 설치한 뒤, 우사기 라벤더 앱의 **테마 적용하기**를 누릅니다.

현재 자동 빌드는 저장소 루트의 `usagi-lavender-theme2-project.zip`을 압축 해제하여 실행합니다. 프로젝트 ZIP 안에 Android 소스, Gradle Wrapper, 원본 그림, 리소스 생성·검증 스크립트와 상세 README가 들어 있습니다. ZIP 이름을 그대로 유지해 주세요. 이 ZIP을 수정해 업로드하거나 Actions의 Run workflow를 누르면 새 빌드를 실행할 수 있습니다.

## 디자인

- 친구·채팅 목록: 기존 우사기 엉덩이 반복 패턴
- 채팅방: 라벤더 배경
- 받은 첫 말풍선: 크림색 `#FFFDF5`, 캐릭터 왼쪽 위
- 보낸 첫 말풍선: 버터색 `#FFECC1`, 캐릭터 오른쪽 위
- 말풍선 외곽선 없음, 고정된 캐릭터 영역과 늘어나는 텍스트 영역을 지정한 NinePatch
- 친구·채팅·지금·쇼핑·더보기: 기존 원본 그림 유지
- 버튼·강조색: 진한 라벤더 `#76598D`

## 빌드와 검증

JDK 17, Android SDK 35, Build Tools 35.0.0으로 리소스 검사·APK 빌드·lint를 실행합니다. 결과 APK는 apksigner로 v2 서명을 검사하고 앱 식별자(`com.suss3388.usagilavender`)와 표시 이름을 확인합니다. 산출물에 SHA-256 및 검증 보고서를 포함합니다.

기본 산출물은 개발용 키로 서명된 설치 가능한 APK입니다. 개발용 키는 Actions 캐시에서 재사용하지만 캐시가 삭제·만료되면 달라질 수 있어 이전 테마 앱 재설치가 필요할 수 있습니다. APK 빌드 성공과 실제 휴대폰에서의 설치·카카오톡 화면 확인은 별도입니다. 실제 기기 적용 결과는 아직 확인하지 않았습니다.
