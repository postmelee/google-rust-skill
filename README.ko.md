# Google Rust Guidelines — 에이전트 스킬

[English](README.md)

Google Rust Style Guide를 코드 작성·리뷰·리팩터링에 적용하는 비공식 커뮤니티
스킬입니다. 라이브러리와 애플리케이션, 플랫폼별 정책, 규칙의 예외를 구분합니다.
Google이 제작·관리·보증하는 프로젝트가 아닙니다.

## 설치

Node.js 22.20 이상과 Skills CLI를 사용하는 경우, 이 저장소에서 실행합니다.

```sh
npx skills add . --skill google-rust-guidelines -a codex
```

GitHub 공개 후에는 실제 소유자와 저장소 이름을 지정합니다.

```sh
npx skills add OWNER/REPOSITORY --skill google-rust-guidelines
```

사용자 전체 설치에는 `-g`를 추가합니다. Node 없이 설치하려면
`skills/google-rust-guidelines` 폴더 전체를 에이전트의 스킬 디렉터리에 복사합니다.
Codex는 `~/.agents/skills/` 또는 프로젝트의 `.agents/skills/`를 사용할 수 있습니다.
기존 설치를 확인하고, 출처·라이선스·참조 파일도 함께 유지하세요.

## 사용

```text
$google-rust-guidelines로 이 Rust 변경을 리뷰해줘.
프로젝트 정책과 공개 API 호환성을 유지하고, 적용되는 규칙과 예외를 설명해줘.
```

실행용 스킬은 Markdown과 UI 메타데이터로 구성됩니다. 참조 문서를 읽는 데
네트워크·Python·API 키가 필요하지 않습니다. Rust 도구는 실제 코드 검증에
필요한 경우에만 사용합니다.

## 평가와 한계

15개 평가 사례에는 올바른 코드를 그대로 두는 경우와 실제 위반 사례가 포함됩니다.
평가 입력과 정답표는 분리되어 있습니다.

- [평가 절차](evals/README.md)
- [기존 스킬 2개·스킬 없음과의 비교 기록](evals/results/2026-10-23/REPORT.md)
- [원문 버전](provenance/upstream.json)
- [규칙별 출처](provenance/rule-map.json)

이 개발용 사례와 단일 모델의 소규모 비교만으로 정확도 향상이나 토큰 절약을
입증했다고 주장하지 않습니다. 문서의 바이트 크기와 실제 모델 사용량을 구분합니다.
호스트별 자동 호출 동작 역시 별도 확인이 필요합니다.

## 검증·공개

개발 환경 설치, 검증 명령, ZIP 생성, GitHub 공개 순서는 [영문 README](README.md)에
정리되어 있습니다. 유지보수 스크립트는 GitHub 저장소를 생성하거나 자동 공개하지
않습니다. 실행용 ZIP에는 스킬과 필수 출처·라이선스만 포함합니다.

## 라이선스

Google 원문을 재구성한 가이드와 문서는 [CC BY 3.0](LICENSE),
독자 작성한 Python 도구·Rust/Python 평가 입력·CI 설정은 [MIT](LICENSES/MIT.txt)입니다.
Google 원문의 코드 예제는 별도 Apache 2.0 조건이며, 실행용 패키지에 원문 코드
예제 묶음을 포함하지 않습니다. [출처와 변경 고지](skills/google-rust-guidelines/NOTICE.md)를
함께 배포하세요.
