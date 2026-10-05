# 절차표 — 세 저장소 커밋 이력에서 Claude 표기 제거 (2026-10-06 낮, 사용자 결정 A+B)

> 결정 `2026-10.md` 10-06 (1). **되돌릴 수 없는 force push** — SESSIONS 「이력 재작성 금지」의 사용자 명시 **한 번짜리 예외**.
> 실행 전 `/effort xhigh`. 끝나면 `high` 로.

## 0. 창
- **10-06 09:00~22:00 KST** 안에서만. 밤 크론(14:10Z·18:10Z + 지연 최대 6h)과 겹치면 안 된다.
- 시작 전 확인: `galmal-backend` origin/main 의 마지막 봇 커밋이 **10-05 밤 몫**(`collect: 2026-10-06`)인가. 아니면 아직 크론이 안 끝난 것 — 기다린다.

## 1. 멈춤 (기획이 통보, 두 세션이 답해야 진행)
- [ ] 프론트·백엔드: 작업 트리 깨끗 + 로컬 브랜치 전부 push + 열린 PR 없음 → 「준비됨」 회신.
- [ ] 세 레포 `git status -sb` 가 `main...origin/main` 과 같음(기획이 읽기만으로 확인).
- [ ] GitHub Actions 에서 돌고 있는 워크플로 0(백엔드 collect · 프론트 deploy).

## 2. 도구·백업
- [ ] `pip install git-filter-repo` (2.47.0 확인됨, Python 3.11).
- [ ] 레포마다 **백업 브랜치를 원격에 push**: `git branch backup/pre-rewrite-2026-10-06 origin/main && git push origin backup/pre-rewrite-2026-10-06`. 모든 게 끝나고 contributor 그래프까지 확인한 뒤(며칠) 지운다 — 옛 trailer 가 든 이력이라 남겨 두면 contributor 에 그대로 잡힌다.
- [ ] `filter-repo` 는 원격을 지우므로 **각 레포의 원격 URL 을 적어 둔다**: `git remote -v`.

## 3. 재작성 (레포마다, 기획 터미널에서 — 남의 저장소를 「고치는」 게 아니라 사용자 결정의 실행. 각 세션엔 미리 알린다)
```
git -C <repo> filter-repo --force --message-callback '
import re
m = re.sub(rb"(?m)^Co-Authored-By: .*\n?", b"", message)
m = re.sub(rb"(?m)^Claude-Session: .*\n?", b"", m)
m = re.sub(rb"(?m)^.*Generated with \[Claude Code\].*\n?", b"", m)
return re.sub(rb"\n{3,}$", b"\n\n", m)
'
```
- 산출: `.git/filter-repo/commit-map`(옛 SHA → 새 SHA). **세 레포 것을 임시 폴더에 복사**해 4 에 쓴다.
- 확인(여집합): `git log --all --format=%B | grep -c "Co-Authored-By\|Claude-Session"` 이 **0**. 파일 내용 불변: **`git rev-parse HEAD^{tree}` 가 재작성 전후 같다**(바이너리 `data/*.db` 포함 전 파일을 한 값으로 — 백엔드 제안) + `git rev-list --count HEAD` 일치. `git diff backup/... main --stat` 비어 있음은 보조.
- 원격 다시: `git remote add origin <URL>`.

## 4. 문서의 해시 치환
- 기획: `python scripts/rewrite_hashes.py <map-plan> <map-backend> <map-frontend>` — 세 대응표를 모두 받아 `*.md` 안 7·8자리 해시를 치환(기획 문서가 남의 레포 해시도 인용한다). 사전 측정: 기획 문서 안 자기 해시 9건.
- 백엔드(58건)·프론트(83건): 각 세션에 **대응표 셋**을 보내 **각자** 치환·커밋. 치환 커밋은 새 이력 위에 쌓인다 — trailer 없이(6 이 먼저).

## 5. 밀기·맞추기
- [ ] 레포마다 `git push --force origin main`(기획 레포는 `plan` → `main`). **셋 다 한 번에 — 중간에 쉬지 않는다.**
- [ ] 프론트 deploy · 백엔드 Pages 가 새 이력으로 다시 돌아 **초록**인지 본다(내용은 같으니 산출물 동일해야 한다 — 프론트 `build.json` 의 커밋 해시만 바뀐다).
- [ ] 세 세션 + `promo-ticket-site`(galmal-plan 의 원본 저장소): `git fetch && git reset --hard origin/main`(기획은 `plan` 브랜치를 `origin/main` 에). worktree 공유 객체라 `promo-ticket-site` 를 빠뜨리면 옛 객체가 남는다.
- [ ] 각 레포 `git log --all --format=%B | grep -c "Co-Authored-By\|Claude-Session"` == 0 을 **각 세션이 자기 터미널에서** 다시 센다.

## 6. 앞으로 안 붙이기 (A)
- [ ] 기획 `~/.claude/settings.json`: `"includeCoAuthoredBy": false`(`update-config` 스킬). **세션별 설정이 아니라 사용자 설정**이라 세 세션 공통 — 다른 두 세션은 재시작해야 읽는다.
- [ ] `SESSIONS.md` 법적·보안: 「`Co-Authored-By: Claude` 라인 포함」 → 「**AI 표기 trailer(Co-Authored-By · Claude-Session · Generated with)를 붙이지 않는다** — AI 사용은 README 한 문장으로 밝힌다(10-06 (1))」.
- [ ] 각 세션의 시스템 attribution 안내보다 **사용자 규칙이 우선**한다 — SESSIONS 가 바뀐 뒤 첫 커밋에서 trailer 가 없는지 셋 다 확인.
- [ ] README(기획 레포 91행 「Claude 세션 셋과 함께 만들었다」)는 **유지** — 사용자: 「AI 썼다고는 할 것」.

## 7. 뒤
- [ ] GitHub 저장소 Contributors 에서 Claude 가 빠졌는지 — 그래프 갱신에 며칠 걸릴 수 있다. 안 빠지면 백업 브랜치(2)가 원인 — 확인 뒤 지운다.
- [ ] PR #1~#9 페이지의 커밋 링크는 옛 해시라 나중에 404 — 받아들인다(PR 본문 글은 남는다).
- [ ] `TODAY.md` 판·결정 10-06 (1)에 실행 결과(세 레포 commit 수·trailer 0·치환 건수) 기록. effort `high` 로 내리라고 사용자에게.

## 되돌리기 (5 전까지만)
`git reset --hard backup/pre-rewrite-2026-10-06` — force push 뒤엔 백업 브랜치를 다시 main 으로 force push 하면 되지만, 그 사이 크론 커밋이 있었다면 손으로 얹어야 한다. 그래서 창(0)을 지킨다.
