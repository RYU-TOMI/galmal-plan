# -*- coding: utf-8 -*-
"""문서 안 커밋 해시를 옛 → 새 로 치환한다 (절차표 2026-10-06 §4).

사용: python scripts/rewrite_hashes.py <commit-map>... [--glob PATTERN]... [--dry]
  commit-map 은 git filter-repo 가 남기는 .git/filter-repo/commit-map (옛 새 두 열). 세 레포 것을 모두 준다 —
  기획 문서는 남의 레포 해시도 인용한다.
치환 대상: 이 저장소 *.md 안의 7·8자리 16진수 토큰 중 어느 대응표의 옛 SHA 접두사와 일치하는 것. 새 값은 같은 길이 접두사.
안전: 접두사가 대응표 안에서 여러 옛 SHA 에 걸리면(모호) 치환하지 않고 보고한다. 숫자만으로 된 토큰(`1000000` 같은 10진수 상수)도 표에 걸리면 바꾸지 않고 보고한다. 바이트 LF 유지(newline="").
"""
import glob, io, re, sys

argv = sys.argv[1:]
globs = ["**/*.md"]
while "--glob" in argv:  # 코드 파일 속 인용까지: --glob "**/*.py"
    k = argv.index("--glob"); globs.append(argv[k + 1]); del argv[k:k + 2]
maps = [a for a in argv if not a.startswith("--")]
dry = "--dry" in argv
old2new = {}
for m in maps:
    for line in io.open(m, encoding="utf-8"):
        p = line.split()
        if len(p) == 2 and len(p[0]) == 40 and p[0] != "old":
            old2new[p[0]] = p[1]
if not old2new:
    sys.exit("대응표가 비었다")

def lookup(tok):
    if tok.isdigit():  # 1000000 · 1048576 같은 10진수 상수가 16진으로도 읽힌다 — 표에 걸려도 손으로(프론트 발견 2026-10-07)
        return "DIGITS" if any(o.startswith(tok) for o in old2new) else None
    hits = [o for o in old2new if o.startswith(tok)]
    if len(hits) == 1: return old2new[hits[0]][:len(tok)]
    if len(hits) > 1: return "AMBIG"
    return None

tok_re = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{7,8}(?![0-9a-fA-F])")
total = 0; ambig = []
files = sorted({f for g in globs for f in glob.glob(g, recursive=True)})
for f in files:
    s = io.open(f, encoding="utf-8", newline="").read()
    n = 0
    def sub(m):
        nonlocal_n[0] += 0
        r = lookup(m.group(0))
        if r in ("AMBIG", "DIGITS"): ambig.append((f, m.group(0), r)); return m.group(0)
        if r: nonlocal_n[0] += 1; return r
        return m.group(0)
    nonlocal_n = [0]
    t = tok_re.sub(sub, s)
    n = nonlocal_n[0]
    if n:
        total += n; print(f"{f}: {n}")
        if not dry: io.open(f, "w", encoding="utf-8", newline="").write(t)
print("치환", total, "건", "(dry)" if dry else "")
for f, tok, why in ambig: print("손으로 확인:", f, tok, "(접두사 모호)" if why == "AMBIG" else "(숫자만 — 10진수 상수일 수 있음)")
