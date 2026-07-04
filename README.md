# 남승현 — Gen AI · Data Scientist 포트폴리오

순수 정적 사이트(HTML/CSS/Vanilla JS)로, 빌드 과정 없이 GitHub Pages에 바로 배포됩니다.

## 구조

```
index.html              페이지 뼈대
css/style.css           전체 스타일 (색 토큰은 :root 에 모여 있음)
js/data.js              ★ 프로필 + 15개 프로젝트 콘텐츠 (수정은 대부분 여기서)
js/main.js              렌더링 로직 (필터·카드·모달)
assets/diagrams/        플로우 다이어그램 SVG 21종
assets/pdf/             이력서·보고서 PDF 넣는 곳 (현재 비어 있음)
tools/generate_diagrams.py  다이어그램 재생성 스크립트
```

## 콘텐츠 수정 방법

- 카드 순서 변경: `js/data.js` 의 `PROJECTS` 배열 순서만 바꾸면 됩니다.
- 기간 추가: 해당 카드의 `period: null` 을 `"YYYY.MM – YYYY.MM"` 으로 교체.
- 다이어그램 수정: `tools/generate_diagrams.py` 의 스펙을 고친 뒤 `python3 tools/generate_diagrams.py` 재실행.

## 추가해야 하는 파일 (배포 전)

| 파일 | 용도 | 미추가 시 |
|---|---|---|
| `assets/profile.jpg` | 푸터 프로필 사진 | 자동 숨김 (에러 없음) |
| `assets/pdf/resume.pdf` | 이력서 다운로드 버튼 | 404 |
| `assets/pdf/est-moe.pdf` | EST-MoE 논문 | 404 |
| `assets/pdf/gender-gap.pdf` | 캡스톤 보고서 (스폰서 공개 조건 확인 후) | 404 |
| `assets/pdf/ideology.pdf` | 의회 이념 예측 논문 | 404 |
| `assets/pdf/covid-ohio.pdf` | COVID 보고서 (공동저자 동의 후) | 404 |
| `assets/pdf/github-network.pdf` | 네트워크 분석 보고서 (공동저자 동의 후) | 404 |

PDF를 당장 못 넣는 카드는 `js/data.js` 에서 해당 카드의 `pdf: {...}` 를 `pdf: null` 로 바꾸면 버튼이 사라집니다.

## 로컬 미리보기

```bash
python3 -m http.server 8000
# http://localhost:8000
```
