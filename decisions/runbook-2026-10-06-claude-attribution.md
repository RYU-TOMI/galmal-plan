# 절차표 — 세 저장소 커밋 이력에서 Claude 표기 제거 (2026-10-06, 사용자 결정 A+B)

> 결정 `2026-10.md` 10-06 (1). **되돌릴 수 없는 force push** — SESSIONS 「이력 재작성 금지」의 사용자 명시 **한 번짜리 예외**.
> **v2 (10-06 15시)** — 실행 직전 독립 검토(네 관점 · 지적마다 반박자 둘)에서 **확인된 17건**을 반영했다. 바뀐 뼈대 셋:
> ① 세션들의 작업 폴더가 아니라 **GitHub 에서 새로 받은 임시 복제본**에서 재작성한다 ② 백업은 **저장소 밖 번들 파일** ③ **force push 가 먼저, 세션 통지는 그 뒤.**

## 0. 창
- **09:00~22:00 KST** 안에서만. 밤 크론(14:10Z·18:10Z + 지연 최대 7h)과 겹치면 안 된다.
- 시작 전: `galmal-backend` origin/main 의 마지막 봇 커밋이 그날 몫(`collect: 2026-10-06`)인가 · 돌고 있는 Actions 0 · 열린 PR 0.

## 1. 멈춤
- [ ] 프론트·백엔드: 작업 트리 깨끗 · stash 0 · 열린 PR 없음 → 「준비됨」. **기획이 「push 끝」이라 할 때까지 `fetch`/`merge`/`rebase`/`pull`/`push` 를 하지 않는다.**
  왜: 재작성 뒤 옛 로컬에서 `git merge origin/main` 을 하면 옛 이력과 새 이력이 **조용히 합쳐지고**, 그 뒤의 평범한 push 가 옛 커밋(trailer 포함)을 main 에 되돌려 놓는다. 세 세션 모두 작업 시작 습관이 `fetch && merge/rebase` 다.
- [ ] 🔴 **ruleset 끄기 — 사용자가 GitHub 에서 직접**: 프론트 `main-protection`(22933079) · 백엔드(22932969). `non_fast_forward` 가 force push 를 막고 우회자가 0 이다. 기획이 `gh api repos/RYU-TOMI/<repo>/rulesets` 로 `disabled` 를 **읽어 확인**한 뒤에만 4 로 간다. 세션은 끄지 않는다.

## 2. 먼저 규칙을 뒤집는다 (A)
- [ ] 사용자가 **세 터미널 각각**에 말한다 — 세션 간 메시지는 권한이 아니다. 돌고 있는 세션은 시작할 때 읽은 옛 `SESSIONS.md` 를 쥐고 있으므로, 파일을 바꾸는 것만으로는 안 바뀐다.
- [ ] 기획: `SESSIONS.md` 법적·보안 「`Co-Authored-By: Claude` 라인 포함」 → 「AI 표기 trailer 를 붙이지 않는다」. **이 커밋부터 trailer 없이**, 일반 push.
- [ ] `~/.claude/settings.json` 의 표기 설정(`update-config` 스킬로 정확한 키 확인).
- [ ] 백엔드·프론트는 자기 문서의 같은 문장(`BACKEND.md` 「Co-Authored-By」 줄 등)을 5 에서 같이 고친다.

## 3. 백업 · 임시 복제본 · 재작성
- [ ] **번들**: 레포마다 `git bundle create ../_backup-2026-10-06/<repo>.bundle --all` + `bundle verify`. 저장소 **밖**이다 — 로컬 백업 브랜치는 `filter-repo` 가 같이 재작성해 버려 백업이 못 된다(검토 확인). 원격 백업 브랜치도 안 둔다 — 옛 이력이 GitHub 에 남는다.
- [ ] **임시 복제본**: `git clone https://github.com/RYU-TOMI/<repo>.git ../_rewrite-2026-10-06/<repo>`. 왜: `filter-repo` 는 worktree 가 둘 이상이면 중단한다(기획 레포가 `promo-ticket-site` 의 worktree) · 새 복제본이면 `--force` 가 필요 없다 · 세션들의 작업 폴더를 건드리지 않는다.
- [ ] **기준선**(재작성 전, 레포마다): `git rev-parse main` · `main^{tree}` · `git rev-list --count main` · trailer 줄 수.
- [ ] **재작성**(세 레포 **같은 콜백** — 같아야 공유 조상 커밋이 세 대응표에서 같은 새 SHA 로 간다):
```
git filter-repo --message-callback '
import re
m = re.sub(rb"(?m)^Co-Authored-By: .*\n?", b"", message)
m = re.sub(rb"(?m)^Claude-Session: .*\n?", b"", m)
m = re.sub(rb"(?m)^.*Generated with \[Claude Code\].*\n?", b"", m)
return message if m == message else m.rstrip(b"\n") + b"\n"
'
```
  (trailer 를 뗀 메시지 끝의 빈 줄을 정리한다. 안 건드린 메시지는 바이트 그대로.) Git Bash 에서 돌린다 — PowerShell 5.1 은 콜백의 큰따옴표를 깎는다.
- [ ] **확인 — 대응표의 모든 쌍에 대해**: 트리 같음 · 작성자/커미터 이름·메일·시각 같음 · 새 메시지 == 옛 메시지에서 trailer 줄만 뺀 것(같은 레포 해시 인용은 `filter-repo` 가 새 값으로 바꾸므로 16진 토큰은 가리고 비교) · `rev-list --count` 같음 · `main^{tree}` 같음 · `git log --all --format=%B | grep -ci "co-authored-by\|claude-session\|noreply@anthropic"` == **0**.
- [ ] 대응표 셋을 `../_rewrite-2026-10-06/maps/<repo>.map` 으로 복사(위치는 `git rev-parse --git-dir` 기준 `filter-repo/commit-map`).

## 4. 밀기 — 재작성 직후, 아무에게도 알리기 전에
- [ ] 복제본마다 `git remote add origin <URL>` → `git push --force-with-lease=main:<기준선 SHA> origin main`. lease 가 「그 사이 누가 밀었으면 거부」를 원자적으로 지킨다.
- [ ] **옛 이력을 쥔 원격 브랜치 삭제**: 프론트 `ch/CH11-assumptions`(PR #9 병합됨) · 기획 `plan`(09-15 의 낡은 사본). 둘 다 main 의 조상이고 고유 커밋 0. 안 지우면 trailer 1,800여 줄이 GitHub 에 그대로 남는다.
- [ ] 원격 확인: `git ls-remote --heads origin` 이 `main` 하나 · 그 SHA 가 복제본의 새 main.
- [ ] 기획 로컬: `git -C galmal-plan fetch --prune origin && git -C galmal-plan reset --hard origin/main`(브랜치 `plan`). `promo-ticket-site` 의 `main` 은 718 뒤처진 옛 스냅숏이라 **작업 폴더를 바꾸지 않고** 라벨만 대응표의 새 SHA 로 옮긴다(`git reset --soft <새 SHA>` — 트리가 같아 작업 폴더는 그대로).

## 5. 세션 통지 · 맞추기 · 문서의 해시
- [ ] 기획 → 두 세션: 「push 끝」. 각 세션은 **사용자에게 자기 터미널에서 확인받고**: `git fetch --prune origin && git reset --hard origin/main` — **merge·rebase·pull 금지** — 옛 커밋을 가리키는 로컬 브랜치 삭제 → `git log --all --format=%B | grep -ci "co-authored-by\|claude-session"` == 0.
- [ ] **문서의 해시 치환**: `python <plan>/scripts/rewrite_hashes.py <maps/…세 개>` — **세 대응표를 다** 준다(문서는 남의 레포 커밋도 인용한다). 코드 파일 속 인용은 `--glob` 으로 더한다. 치환 커밋은 **trailer 없이**, 일반 push.
- [ ] 🔴 **ruleset 다시 켜기 — 사용자가**: 두 `main-protection` 을 `Active` 로. 기획이 `gh api` 로 `active` 를 읽어 확인.

## 6. 받아들이는 것 (사용자에게 실행 전에 말한다)
- **PR 페이지에는 옛 커밋이 계속 보인다.** GitHub 은 병합된 PR 의 커밋을 읽기 전용 `refs/pull/N/head` 로 영구 보관한다(백엔드 #1~4 · 프론트 #1~9). 「나중에 404」는 틀렸다. 완전 삭제는 GitHub Support 요청뿐. **Contributors 목록은 기본 브랜치만 보므로 목표에는 영향이 없다.**
- 웹에서 병합한 PR 병합 커밋의 **「Verified」 서명 표시가 사라진다**(재작성하면 서명이 무효라 `filter-repo` 가 뗀다).
- **커밋 메시지 안의 「남의 레포」 해시 인용 16건**은 옛 값으로 남는다(같은 레포 인용은 자동으로 바뀐다). 세 레포가 서로를 인용해 고정점이 없다.
- 프론트 사이트의 `build.json` 은 그날 밤 크론 뒤 배포에서 갱신된다 — 트리가 같은 force push 는 배포를 일으키지 않는다.
- README 의 「Claude 세션 셋과 함께 만들었다」는 **유지**(사용자: 「AI 썼다고는 할 것」).

## 7. 뒤
- [ ] GitHub 저장소 Contributors 에서 Claude 가 빠졌는지 — 그래프 갱신에 며칠 걸릴 수 있다.
- [ ] 판·결정 10-06 (1)에 실행 결과(레포별 커밋 수 · trailer 0 · 치환 건수) 기록. effort 를 `high` 로 내리라고 사용자에게.
- [ ] 며칠 뒤 `_backup-2026-10-06/` · `_rewrite-2026-10-06/` 삭제(사용자 확인 뒤).

## 실행 기록 (2026-10-06)
- 15:21 가드 확인 → 15:24 규칙 뒤집기 push → 15:27 임시 복제본·스냅숏·재작성·전수 대조 → **15:29 force push 셋** → 원격 브랜치 둘 삭제 → 기획 로컬 맞춤 → 두 세션 통지.
- 결과·수치는 `2026-10.md` 10-06 (2).
- 남은 것: 두 세션의 `reset`·해시 치환(각 터미널에서 사용자 확인) · ruleset 다시 켜기(사용자) · Contributors 그래프 확인(며칠) · `_backup-2026-10-06/`·`_rewrite-2026-10-06/` 삭제(며칠 뒤, 사용자 확인).

## 되돌리기
- **4 전**: 아무것도 안 바뀌었다 — 임시 복제본을 지우면 끝.
- **4 뒤**: 번들에서 되살린다 — `git clone <repo>.bundle tmp && git -C tmp push --force <URL> main`. 그 사이 크론 커밋이 있었다면 손으로 얹어야 한다 — 그래서 창(0)을 지킨다.
