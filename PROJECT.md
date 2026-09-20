# 갈래말래 — 프로젝트 지도·현황·운영 정보

> 세션 시작 시 프로젝트를 빠르게 파악하기 위한 **지도**다. 규칙은 여기 두지 않는다 —
> 세 세션 공통 규칙은 **`SESSIONS.md`**, 저장소별 규칙은 각 저장소의 `CLAUDE.md`. (규칙을 두 곳에 적으면 갈린다.)

## 한 줄 요약
"시간 남는데 어디 싸게 갈까?"에 답하는 **항공권 발견(discovery) 서비스**. (「특가」는 쓰지 않는다 — `SPEC.md` F19)
목적지를 검색하는 게 아니라, 예산·기분으로 **목적지를 정해준다**. 한국 출발 전용.

## 저장소 셋 (2026-09-19~)

| 저장소 | 세션 | 무엇 | 서빙 |
|---|---|---|---|
| [`galmal-plan`](https://github.com/RYU-TOMI/galmal-plan) | 기획 | 제품·스펙·결정 기록·계약의 **이유** · `design/` | — |
| [`galmal-backend`](https://github.com/RYU-TOMI/galmal-backend) | 백엔드 | 수집·판정·**v1 API**·계약 정본 `contract/v1/`·크론 | `https://api.galmal.kr/v1/` |
| [`galmal-frontend`](https://github.com/RYU-TOMI/galmal-frontend) | 프론트 | v1 소비 · 화면 빌드 | `https://galmal.kr` |

로컬: `개인 프로젝트/galmal-plan · galmal-backend · galmal-frontend`(형제). 세 저장소 모두 **공개**.

## 아키텍처 (핵심 원칙)
- **정적 생성 + 서버 없음.** 백엔드는 JSON을, 프론트는 HTML을 미리 만든다 → GitHub Pages 두 곳. 비용은 도메인 외 $0.
- **경계는 「데이터 / 화면」**: 백엔드는 사실(v1 JSON)만, 프론트는 말(화면)만. 창은 백엔드, 임계는 프론트(`DECISIONS.md` 2026-09-08).
- **데이터는 URL로 건넨다** — 나중에 백엔드가 서버가 돼도 프론트 코드는 안 바뀐다. `design/` 목업도 같은 규칙.
- 스택 고정: Python 정적 생성 + 순수 JS + 지도만 d3-geo(벤더링). Node/npm·프레임워크 없음.

## 하루의 흐름
```
20:10 UTC(05:10 KST) 예약 — 2026-09-20~, 실제 시작은 GitHub 지연만큼 늦다 · galmal-backend collect.yml
  (1회 관측 2026-09-19: 시작 22:18Z = 지연 2시간 8분 → 사이트 갱신 07:19 KST. 한 번 잰 값이라 범위가 아니다)
  수집 → 판정 → 메일 수집·파싱 → 알림 발송 → publish.py(docs/v1) → 커밋 → Pages(api.galmal.kr)
  → API가 새 값을 서빙하는지 확인 → repository_dispatch(client_payload.generated)
galmal-frontend deploy.yml
  v1 40개(meta·index·deals·vocab + 노선 36)를 한 스냅숏으로 받는다(섞이면 배포 안 함) → site/build.py → Pages(galmal.kr) + build.json
다음 날 백엔드 상태 점검: API 신선도 · 사이트 build.json 일치 · 구독 주소
```

## 제품 방향 (중요 — 2026-07-30 전환)
- 초기엔 "특가 목록"이었으나, **발견(discovery)** 콘셉트로 전환.
- 경쟁(스카이스캐너·트립닷컴)은 "목적지 우선 검색". 우리는 "목적지를 정해주는" 틈새.
- 발견 모드는 지연 데이터(3일)에 **관대함**: 가격은 예약 약속이 아니라 "대략 이 정도" 신호.
  클릭하면 실시간 예약처로 넘어감.
- 메인 화면 = **인터랙티브 세계지도** (아래 로드맵 참조).

## 데이터 파이프라인 (2계층) — `galmal-backend`
1. **노선 상세(depth)**: `fetch_prices.py` — 36개 노선을 v3 API로 날짜별 깊게 수집 → `offers` 테이블.
   특가 판정(`detect_deals.py`)·노선 상세 페이지·30일 히스토리 차트용.
2. **광역 발견(breadth)**: `fetch_breadth.py` — 한국 전 공항(ICN/GMP/PUS/TAE/CJU)을 v2 API로
   공항당 1회 호출, 목적지당 최저가 → `broad_offers` 테이블. "어디 갈까" 발견 피드용.
   품질 필터: `dests.py` 사전에 있는 목적지 + 신선도 3일 이내만.
- 메일: `mail_ingest.py`(수집, IMAP) → `parse_mail.py`(claude-haiku-4-5로 특가 추출) → `mail_deals`.
- 구독: `subscriptions.py`(받은편지함=구독자 DB, PII 미저장) → `send_alerts.py`(Gmail SMTP 발송).

## 완료된 것 ✅
- 데이터 수집·특가 판정·메일 파싱·구독 알림 파이프라인 (크론 매일 무결점 가동 중)
- 노선 상세 페이지 26개 + sitemap/robots (SEO 기반)
- 갈래말래 브랜딩, 보딩패스 카드 UI, dataviz 팔레트
- **발견 데이터 계층**: fetch_breadth + dests + broad_offers
- **발견 홈 v1 (동작 중)**: 화면0 출발지 선택 · 지도 무대(핀·항로·거리 3단계·LOD) ·
  카드 피드(hero·정렬 3종) · 필터 도크(날짜·분위기·예산) · 확장 상세(시세 비교·예약처 4곳·광고 고지) · noscript 대체
- **작업 체계 정립(2026-08-22)**: 3세션 모두 챕터제 — `PLAN.md`·`FRONTEND.md`, 미결은 `SPEC.md`·`BACKLOG.md`
- **저장소 분리 M0~M6 (2026-09-08 ~ 09-19)** — 한 저장소 → `galmal-backend` · `galmal-frontend` · `galmal-plan`.
  v1 API(`api.galmal.kr/v1`) 뒤로 데이터를 건네고, 화면은 프론트가 굽는다. 기록 `SPLIT.md`·`DECISIONS.md` 2026-09-08~09-17.

## 현재 — 세션별 현황

> 로드맵은 각 세션 문서가 소유한다: 기획 `PLAN.md` · 백엔드 `galmal-backend/BACKEND.md` · 프론트 `galmal-frontend/FRONTEND.md`.

| 세션 | 최근 | 다음 |
|---|---|---|
| 기획 | 저장소 분리 M0~M6 | **참조 데이터 v1 발행** 계약(`DECISIONS.md` 2026-09-17 완료 절) → PH7 시즌 이벤트 |
| 백엔드 | BE9(테스트 신뢰성) · BE10(계약 목록 이전) | 참조 데이터 발행 · BE8 재개 |
| 프론트 | M4 이동 · T6d 스냅숏 검사 | 참조 데이터로 손 사본 제거 · CH6 재개 · B43 |

**규칙: 기획 챕터(PH)는 프론트 챕터(CH)보다 하나 앞선다.** 이전 동안 멈췄던 기능 챕터(CH6·CH4 T7·BE8)는 M6 후 재개한다.

### 문서 지도 (`galmal-plan`)
| 문서 | 역할 |
|---|---|
| `SESSIONS.md` | **세 세션 공통 규칙**(한 벌) |
| `PRODUCT.md` | 제품 본질 — 대상·목적·포지셔닝·원칙 |
| `IA.md` · `FLOWS.md` | 사이트맵·URL / 유저 플로우·실패 경로 |
| **`SPEC.md`** | 화면·상태 인벤토리 + 챕터별 확정 인터랙션 스펙 · §3 미결 |
| `COPY.md` · `DESIGN.md` | 화면 문자열·보이스 / 시각 언어 |
| `CONTRACT.md` · `TAGS.md` | 계약·태그의 **이유와 원칙**(목록 정본은 `galmal-backend`) |
| `DECISIONS.md` | 왜 그렇게 정했나 + 기각안 |
| `PLAN.md` | 기획 작업 방식 · 함정 기록 |
| ~~`SPLIT.md`~~ | 저장소 분리 M0~M6 기록 — **2026-09-19 삭제.** 전문은 `git show 810dafa:SPLIT.md` |
| `design/` | 목업 — 글로 합의 안 되는 것만 |

### 미결은 한 곳에서 본다
열린 결정은 **`SPEC.md` §3 미결 통합 목록**이 단일 출처다(현재 17건 + 프론트 실측 4건).
PROJECT.md에 열린 결정을 중복해 적지 않는다 — 두 곳에 적으면 반드시 어긋난다.

**최우선**: `F1` 딜이 0건인 날 화면이 **완전한 막다른 길**이다(`origins`가 비면 핀도 안내도 없음).
수집은 외부 API에 의존하므로 언제든 발생할 수 있다.
→ **양쪽에서 막는다**: 생성 쪽 방어(수집 실패 시 이전 산출물 유지·하한선)는 백엔드 `BE1`(백로그 `BB1`),
화면 쪽 빈 상태는 기획 `PH3` → 프론트 `CH3`.

### 시각 산출물 (design/)
| 파일 | 내용 |
|---|---|
| `feed_map.html` | 홈 레이아웃 확정 시안 — 지도 + 피드 + 플로팅 카드 (2026-08-01) |
| `storyboard.html` | LOD 상태별 정지 장면 (입장/일본 확대/호버/동남아) |
| `freshness.html` | 신선도 배지 확정 스펙 (2026-08-22) |

## 이후 백로그
- ~~커스텀 도메인·서치콘솔~~ ✅(2026-09-05) → 커뮤니티 시딩(뽐뿌 등)
- Trip.com 제휴 재신청(3개월 트래픽 후) — affiliates.py 코드는 대기 상태로 유지
- 항공사 프로모션 페이지 크롤링(두 번째 LLM 파싱 사용처)

## 법적·보안
규칙은 **`SESSIONS.md` §법적·보안**. 여기엔 배경만:
- 타 비교사이트 DB 크롤링 금지의 근거 — 여기어때 판례(민사 10억).
- 구독자 이메일은 해시만 저장(`alert_log`), 메일 본문은 로컬 전용(`data/emails_raw.db`, gitignore).
- 가격은 데이터가 최대 수일 지연이라 「조회 시점 기준, 실제 가격은 예약처 확인」을 붙인다.

## 운영 정보
- **도메인**: `galmal.kr`(가비아). apex A 4개 → GitHub(`185.199.108~111.153`), `api` CNAME → `ryu-tomi.github.io.`
  - `galmal.kr` = `galmal-frontend` Pages(**Actions 배포** — 도메인은 Pages 설정에 저장, CNAME 파일 불필요)
  - `api.galmal.kr` = `galmal-backend` Pages(**브랜치 배포** `main:/docs` — `docs/CNAME`이 있어야 한다)
  - 도메인을 새로 붙였는데 `https_certificate`가 `null`이면 **기다리지 말고 제거→재등록**(2026-09-17 실측: 33분 무반응 → 재등록 25초)
- **시크릿**: `galmal-backend`의 **`production` 환경**에만 6종 — `TP_TOKEN` · `TP_MARKER` · `MAIL_ADDRESS` · `MAIL_APP_PASSWORD` · `ANTHROPIC_API_KEY` · `DISPATCH_TOKEN`.
  GitHub 시크릿은 **쓰기 전용** — 읽을 수 있는 사본은 로컬 `galmal-backend/.env`뿐이다(gitignore). 잃지 않는다.
  - `DISPATCH_TOKEN`: fine-grained PAT, `galmal-frontend` 하나에 **Contents: Read and write**(Actions 아님), 만료 없음.
  - 🔴 미등록 3종 `TP_TRIP_TRS`·`TP_TRIP_P`·`TP_TRIP_CAMPAIGN` — Trip.com 제휴 승인 후 등록. 없으면 Trip.com 링크가 수수료 없이 나간다.
- **변수**(로그에 보여야 해서 vars): `galmal-backend` `API_URL=https://api.galmal.kr` · `SITE_URL=https://galmal.kr` / `galmal-frontend` `API_URL=https://api.galmal.kr/v1`.
- 전용 메일: flightpromokr@gmail.com (항공사 뉴스레터 구독 + 구독 신청 접수)
- 비용: 연 25,700원 — 도메인 첫해 16,500원(갱신 23,100원) + 메일 파싱 API ~연 2,600원. 호스팅·Actions는 공개 저장소라 $0.
