# -*- coding: utf-8 -*-
"""목업 빌더의 데이터 입구 — 제품에 **공개 URL로** 기댄다 (SPLIT.md M6 T1pre, 2026-09-19).

`galmal-plan`에는 제품 코드·데이터가 없다. 빌더는 사이트를 쓰는 **손님 하나**로서
백엔드 API와 프론트가 배포한 자산을 받아 목업을 그린다 — 프론트와 같은 규칙이다
(「데이터는 파일 경로가 아니라 URL로 건넨다」, DECISIONS.md 2026-09-08 (1)).

주소를 바꾸려면 환경변수: GALMAL_API · GALMAL_SITE (끝 `/` 없이).
"""
import json
import os
import urllib.request

API = os.environ.get("GALMAL_API", "https://api.galmal.kr/v1").rstrip("/")
SITE = os.environ.get("GALMAL_SITE", "https://galmal.kr").rstrip("/")
_CACHE = {}


def _get(url):
    if url not in _CACHE:
        req = urllib.request.Request(url, headers={"User-Agent": "galmal-plan-design/1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            _CACHE[url] = r.read().decode("utf-8")
    return _CACHE[url]


def api_text(path):
    """v1 응답 원문. 예: api_text("deals.json")"""
    return _get(f"{API}/{path}")


def deals():
    """v1 deals.json — 봉투째(schema·generated·deals…)."""
    return json.loads(api_text("deals.json"))


def site_text(path):
    """프론트가 배포한 정적 자산 원문. 예: site_text("data/world.geojson")"""
    return _get(f"{SITE}/{path}")
