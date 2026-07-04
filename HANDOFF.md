# Claude Code 인계 지시서 — GitHub Pages 배포

이 폴더는 완성된 정적 포트폴리오 사이트입니다. 빌드 불필요, 그대로 서빙하면 됩니다.

## 해야 할 일 (순서대로)

1. **저장소 생성·푸시**
   - GitHub 계정: `SHKNam`
   - 옵션 A (추천): `SHKNam.github.io` 저장소로 푸시 → `https://shknam.github.io/` 루트 배포
   - 옵션 B: `portfolio` 저장소로 푸시 → `https://shknam.github.io/portfolio/`
   - 이 사이트는 **모든 경로가 상대 경로**라 두 옵션 모두 수정 없이 동작함
2. **GitHub Pages 활성화**
   - Settings → Pages → Source: `Deploy from a branch` → `main` / `/ (root)`
3. **배포 확인**
   - 히어로·필터·카드 15개·모달·다이어그램 렌더링 확인
   - 모바일 뷰(375px)에서 여정 라인이 세로로 전환되는지 확인

## 사용자에게 확인받을 것 (푸시 전)

- `assets/profile.jpg` (프로필 사진) — 없으면 자동 숨김이라 나중에 추가해도 됨
- `assets/pdf/resume.pdf` (이력서) — 없으면 푸터 버튼이 404. 파일을 받거나, 받기 전까지 버튼을 숨기려면 `js/main.js` 푸터 렌더링에서 해당 `<a>` 제거
- 보고서/논문 PDF 5종 (README 표 참고) — 못 받은 카드는 `js/data.js` 에서 `pdf: null` 처리

## 건드리지 말 것

- 카드 본문 텍스트 (전부 사용자와 확정한 최종본)
- 기간(`period`) — `null` 인 카드에 임의로 기간을 추가하지 말 것 (사용자 결정: 기간 미기입 진행)
- 회사·고객 실명, 벤더명, 내부 시스템명을 추가하지 말 것 (일반화된 현재 표기가 확정본)

## 커밋 예시

```bash
git init && git add -A
git commit -m "feat: portfolio site — 15 project cards, 21 diagrams, static build"
git branch -M main
git remote add origin git@github.com:SHKNam/SHKNam.github.io.git
git push -u origin main
```
