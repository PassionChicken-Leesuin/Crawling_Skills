# Crawling Skills

Claude Code / Claude Desktop용 크롤링 스킬 모음. 각 폴더가 스킬 하나이며 `SKILL.md`(언제·어떻게 쓰는지) + `scripts/`(실행 코드) + `assets/`(템플릿) + `references/`(API 메모)로 구성된다.

| 스킬 | 하는 일 | 핵심 제약 |
|---|---|---|
| [`reddit-crawl-arctic`](reddit-crawl-arctic/) | Arctic Shift API로 서브레딧×기간 게시글 수집 → 키워드 그룹 필터 → 댓글 트리 → CSV. API 키·로그인 불필요, 재개 가능 | 서버 키워드 검색은 활발한 서브레딧에서 타임아웃 → 날짜 페이지네이션 + 로컬 필터 |
| [`x-search-collect`](x-search-collect/) | 로그인된 내장 브라우저에서 X 검색 결과를 자동 스크롤 수집 → 파일 덤프 → 병합 CSV. API 키 불필요 | 15분당 40~50회 검색 제한, 과거 글은 거의 안 나옴(최근 편향) |

## 설치

```bash
git clone https://github.com/PassionChicken-Leesuin/Crawling_Skills.git
cd Crawling_Skills && ./install.sh        # ~/.claude/skills/ 에 복사 (기존 폴더는 덮어씀)
```

또는 `packages/*.skill` 파일을 Claude Desktop에서 열어 **Save skill**.

## 개발 규칙

- 스킬 하나 = 폴더 하나. `SKILL.md` frontmatter의 `name`은 폴더명과 같게, `description`에는 "언제 써야 하는지"를 충분히 넓게 적는다(스킬은 과소 트리거되는 경향이 있다).
- 프로젝트 전용 값(서브레딧 목록, 키워드)은 스크립트에 박지 말고 `assets/*.template.json` + `*.example.json`으로 뺀다.
- 수집 중 배운 제약(속도 제한, 안 되는 파라미터, 우회 방법)은 반드시 `SKILL.md`나 `references/`에 적는다. 다음 세션의 Claude는 이 문서만 보고 움직인다.
- 패키징: skill-creator의 `python -m scripts.package_skill <skill-folder>` → `packages/`에 복사.

## 이력

- 2026-10-21 `reddit-crawl-arctic`, `x-search-collect` 추가 (서울대 UCD 과목 AI 에이전트 위임 연구에서 사용: Reddit 13개 서브레딧 13만 건, X 1.9천 건 수집).
