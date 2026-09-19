<p align="center">
  <a href="https://galmal.kr"><img src="https://galmal.kr/assets/og.png" alt="갈래말래 — 어디, 갈까? 세계 지도에 오늘 싼 여행지가 찍혀 있다" width="720"></a>
</p>

# 갈래말래 — 기획

**[galmal.kr](https://galmal.kr) 의 제품·스펙·결정 기록을 두는 저장소.** 코드는 없다. 무엇을 왜 만들었고, 무엇을 버렸는지가 있다.

## 한눈에

<!-- 발췌: galmal-plan/PRODUCT.md §한 줄 소개 — 고칠 땐 거기부터 -->
> **어디, 갈까?**
> 목적지를 정하지 않은 사람에게, 평소보다 싸게 갈 수 있는 곳을 지도로 보여주는 한국 출발 항공권 발견 서비스.

<img src="https://raw.githubusercontent.com/RYU-TOMI/galmal-frontend/main/.github/readme/home-desktop.png" alt="발견 홈 데스크톱 화면 — 지도, 카드 피드, 필터" width="720">

기존 항공권 사이트는 **「어디로 가세요?」**로 시작한다 — 목적지를 이미 정한 사람의 도구다.
갈래말래는 그 앞 단계, **「어디 갈지 모르겠는데 오늘 뭐가 살 만한가」**에 답한다.
출발지를 고르면 최근 30일 시세보다 싼 곳이 지도에 찍히고, 예산·기간·분위기로 좁혀 고른다. 예약은 예약처로 넘긴다.

## 세 저장소

<!-- 발췌: galmal-plan/PROJECT.md §저장소 셋 — 고칠 땐 거기부터 -->
| 저장소 | 무엇 | 서빙 |
|---|---|---|
| **[`galmal-plan`](https://github.com/RYU-TOMI/galmal-plan)** ← 여기 | **제품·스펙·결정 기록·계약의 이유** · `design/` 목업 | — |
| [`galmal-backend`](https://github.com/RYU-TOMI/galmal-backend) | 수집·판정·**v1 API**·계약 정본 `contract/v1/`·크론 | `https://api.galmal.kr/v1/` |
| [`galmal-frontend`](https://github.com/RYU-TOMI/galmal-frontend) | v1 을 받아 화면을 굽는다 | `https://galmal.kr` |

경계는 **데이터 / 화면**이다. 백엔드는 사실(JSON)만 내고 HTML 을 만들지 않는다. 프론트는 DB 를 모르고 계약만 읽는다.
기획은 둘 사이의 **계약을 정한다** — 필드·어휘 목록은 백엔드 `contract/v1/` 이 정본이고, 여기엔 **왜 그렇게 정했는지**를 둔다.

## 어떻게 도나

<!-- 발췌: galmal-plan/PROJECT.md §하루의 흐름 — 고칠 땐 거기부터. 크론 시각은 galmal-backend 의 collect.yml 이 정본 -->
```
galmal-backend   매일 아침(KST) 크론 — 수집 → 판정 → v1/*.json 발행 → api.galmal.kr
      │
      └─ repository_dispatch(api-updated · generated) ─┐
                                                       ▼
galmal-frontend  deploy.yml
      ① v1 응답 전부를 받는다 ─ 한 발행분이 아니면 여기서 멈춘다
      ② 어휘 매핑·칩 검사     ─ 계약과 어긋나면 여기서 멈춘다
      ③ HTML·sitemap·build.json → GitHub Pages(galmal.kr)
      │
      └─ 다음 날 백엔드 점검이 galmal.kr/build.json 을 읽어 「사이트가 뒤처졌나」를 본다

galmal-plan      목업 빌더(design/)도 같은 공개 URL 을 읽는 손님 하나다
```

## 문서 지도

**처음이면 `PROJECT.md` → `PRODUCT.md` → `DECISIONS.md` 순서로.**

| 문서 | 무엇 |
|---|---|
| [`PROJECT.md`](PROJECT.md) | **지도** — 저장소 셋 · 하루의 흐름 · 현황 · 운영 정보(도메인 · 시크릿 · 비용) |
| [`PRODUCT.md`](PRODUCT.md) | 제품 본질 — 누구를 위해 · 무엇을 · 경쟁 서비스와 무엇이 다른가 |
| [`SPEC.md`](SPEC.md) | 화면·상태 인벤토리와 챕터별 확정 인터랙션. 미결은 §3 한 곳 |
| [`IA.md`](IA.md) · [`FLOWS.md`](FLOWS.md) | 사이트맵·URL / 사용자 흐름과 **실패 경로** |
| [`DESIGN.md`](DESIGN.md) | 시각 언어 — 색 · 타이포 · 컴포넌트 · 지도 스타일 |
| [`COPY.md`](COPY.md) | 화면 문자열 전수와 보이스 규칙 — 없는 문자열을 지어내지 않는다 |
| [`CONTRACT.md`](CONTRACT.md) · [`TAGS.md`](TAGS.md) | 프론트↔백엔드 계약과 태그 어휘의 **이유와 원칙** |
| [`DECISIONS.md`](DECISIONS.md) | **왜 그렇게 정했나, 무엇을 기각했나.** 뒤집은 결정은 지우지 않고 뒤집힌 이유와 같이 남긴다 |
| [`PLAN.md`](PLAN.md) | 기획 작업 방식과 **함정 기록** — 실제로 틀린 적이 있는 확인 방법들 |
| [`SESSIONS.md`](SESSIONS.md) | 세 저장소 공통 작업 규칙(한 벌 — 각 저장소 `CLAUDE.md`가 가져온다) |

## 목업 (`design/`)

글로 합의되지 않는 것만 그린다. 23장 — 발견 홈 · 전환 · 필터 · 모바일 시트 · 신선도 배지 · OG 이미지 등.
각 목업은 **그날 결정의 스냅숏**이라 본문에 그날의 수치가 적혀 있고, 새 데이터로 다시 굽지 않는다.

```bash
python design/build_home.py      # 빌더는 제품 데이터를 공개 URL(api.galmal.kr · galmal.kr)에서 받는다
```
빌더는 Python 표준 라이브러리만 쓴다. 저장소 안에 제품 코드·데이터가 없으므로, 사이트를 쓰는 **손님**처럼 URL 로 기댄다(`design/_data.py`).

## 설계에서 고른 것

결정마다 기각한 대안이 [`DECISIONS.md`](DECISIONS.md) 에 있다. 대표적인 것:

- **특가 목록에서 발견으로 방향을 바꿨다**(2026-07-30). 특가만 모아 보여주면 기존 검색 사이트와 다를 게 없었다 — 그건 목적지를 이미 정한 사람의 도구다
- **「싸다」는 절대 가격이 아니라 평소 대비로 말한다.** 최근 30일 중앙값과 비교하고, 비교할 표본이 없으면 주장하지 않는다
- **「특가」라는 단어를 발견 화면에서 쓰지 않는다.** 제품 안에 특가의 정의가 둘이었다 — 임계값을 맞추는 대신 단어를 나눴다
- **서버 없이 정적으로 굽는다.** 데이터가 하루 한 번 바뀌는 서비스라 방문자마다 요청할 이유가 없다. 연 운영비는 도메인 포함 약 2만 5천 원
- **저장소를 데이터 / 화면으로 나눴다**(2026-09-08 ~ 09-19). 데이터는 URL 로 건넨다 — 나중에 백엔드가 서버가 돼도 프론트 코드는 안 바뀐다
- **목록은 한 곳에만 둔다.** 계약 필드·태그 어휘를 문서와 코드에 두 벌 두었다가 레포 분리 첫날 갈렸다. 목록은 코드 옆으로 옮기고 문서엔 이유만 남겼다

## 어떻게 일했나

한 사람이 **Claude(Claude Code) 세션 셋** — 기획 · 백엔드 · 프론트 — 과 함께 만들었다. 커밋의 `Co-Authored-By: Claude` 가 그 표시다.

- **방향과 결정은 사람이 내렸다.** 세션은 제안하고, 근거를 재고, 기각한 대안까지 문서로 남겼다 — 그 기록이 이 저장소다
- 세 세션은 저장소마다 **자기 구역만** 고치고, 남의 구역에서 문제를 찾으면 고치지 않고 그 세션에 알렸다
- 작업은 **챕터 → 태스크(커밋 하나) → 스코프 잠금**. 작업 중 찾은 딴 문제는 그 자리에서 고치지 않고 백로그에 적었다
- 확인은 **「조용히 통과할 수 있나」**부터 물었다 — 예외도 안 나고 화면도 멀쩡한데 틀린 것이 가장 비쌌다. 실제로 틀렸던 확인 방법들은 [`PLAN.md`](PLAN.md) 함정 기록에 있다

2026-07-09 부터의 전체 이력이 이 저장소에 있다(분리 전 이름 `promo-ticket-site`). 코드 이력은 두 저장소에도 그대로 들어가 있다.

## 법적 고지

- 가격은 **조회 시점 기준**이며 실제 예약 가격은 예약처에서 달라질 수 있다
- **(광고)** 표시가 붙은 링크로 예약하면 운영자가 수수료를 받는다. 이용자가 내는 가격은 같다
- 다른 비교 사이트의 DB 를 크롤링하지 않는다 — 공식 API · 제휴 · 항공사 공지만 쓴다. 가격 데이터: Travelpayouts(Aviasales)
