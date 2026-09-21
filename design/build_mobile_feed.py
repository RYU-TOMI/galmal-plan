# -*- coding: utf-8 -*-
"""모바일 재검토(PH5b) — 피드가 기본 화면이면 어떤가. **실기기에서 여는 목업.**

2026-09-21 사용자: 「지도가 너무 작아서 그냥 딜만 보여주는 걸로 갈까 모바일은? 거의 쓸모가 없음」.
지금까지의 모바일 목업(build_mobile.py)은 데스크톱 화면에 390px 틀을 나란히 그린 것이라
**손가락으로 밀어 볼 수 없었다** — B62 가 헤드리스에선 「이상 없음」이던 이유와 같다(PLAN 함정 12).
이 빌더는 **폰에서 그대로 여는 한 화면**을 만든다. 위 막대로 두 안을 바꿔 본다.

  A  피드만            지도 없음. 거리 단계는 필터 칩으로 내려온다
  B  피드 + 지도 버튼   기본은 피드, 「지도로 보기」가 전체 화면 지도를 연다

데이터는 공개 URL(api.galmal.kr/v1 · galmal.kr)에서 받는다. 예약 링크의 URL 은 싣지 않는다(목업이라 누를 수 없게).
소유: 기획 세션. 산출물 design/mobile_feed.html — 그날 결정의 스냅숏이라 다시 굽지 않는다.
"""
import io, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import _data

D = _data.deals()
WORLD = json.loads(_data.site_text("data/world.geojson"))


def slim(d):
    return {
        "o": d["o"], "d": d["d"], "ko": d["ko"], "country": d.get("country"),
        "price": d["price"], "median": d.get("median"), "discount": d.get("discount") or 0,
        "low": d.get("low"), "obs": d.get("obs_days") or 0,
        "dep": d["dep"], "ret": d["ret"], "nights": d.get("nights"), "when": d.get("when"),
        "tags": d.get("tags") or [], "haul": d.get("haul"), "tr": d.get("transfers"),
        "seen": d.get("seen"), "lat": d["lat"], "lon": d["lon"], "route": d.get("route"),
        "links": [{"name": l["name"], "ad": bool(l.get("ad"))} for l in d.get("links") or []],
    }


def round_geo(o):
    """좌표를 소수 2자리로 — 폰 화면에선 구별되지 않고 용량이 3분의 1로 준다."""
    if isinstance(o, list):
        return [round_geo(x) for x in o]
    if isinstance(o, float):
        return round(o, 2)
    if isinstance(o, dict):
        return {k: round_geo(v) for k, v in o.items() if k != "properties"}
    return o


DATA = {"generated": D["generated"], "origins": D["origins"], "deals": [slim(d) for d in D["deals"]]}
data_js = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))
world_js = json.dumps(round_geo(WORLD), separators=(",", ":"))

PAGE = r"""<title>모바일 피드 목업</title>
<meta charset="utf-8">
<style>
/* 색·글자는 제품의 것(galmal.kr discover.css :root). 제품이 라이트 하나라(DECISIONS 2026-09-20 (3)) 목업도 라이트 하나다. */
:root{--accent:#F2603F;--accent2:#C6472A;--ink:#20353A;--sub:#5E7A7C;--sea:#EDF4F3;--land:#D2E7DE;
  --coast:#33534F;--line:#E6EDEC;--soft:#F0F5F4;--bg:#F4F8F7;--card:#FFFFFF;--mock:#20353A;
  --font:'Pretendard Variable',Pretendard,-apple-system,'Apple SD Gothic Neo','Noto Sans KR',sans-serif}
html{color-scheme:light;-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--font);font-size:15px;line-height:1.45;
  -webkit-tap-highlight-color:transparent}
button,select,input{font:inherit;color:inherit}
button{cursor:pointer}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.num{font-variant-numeric:tabular-nums}

/* ── 목업 틀(제품 아님) ─────────────────────── */
.mock{background:var(--mock);color:#fff;padding:8px 16px 9px;display:flex;flex-direction:column;gap:6px}
.mock .seg{display:flex;background:rgba(255,255,255,.12);border-radius:9px;padding:3px;gap:3px}
.mock .seg button{flex:1;border:0;background:transparent;color:rgba(255,255,255,.72);font-weight:700;
  font-size:13px;padding:7px 4px;border-radius:7px;min-height:36px}
.mock .seg button[aria-pressed="true"]{background:#fff;color:var(--mock)}
.mock p{margin:0;font-size:12px;color:rgba(255,255,255,.78);line-height:1.4}

/* ── 제품 머리 + 필터 (붙어 다닌다) ─────────── */
.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--bg);
  border-bottom:1px solid var(--line)}
.hd{display:flex;align-items:center;justify-content:space-between;padding:10px 16px 6px}
.hdr{display:flex;gap:6px;align-items:center}
.logo{font-weight:900;font-size:19px;letter-spacing:-.02em}
.logo em{font-style:normal;color:var(--accent)}
.orig{appearance:none;-webkit-appearance:none;border:1px solid var(--line);background:var(--card);
  border-radius:999px;padding:7px 30px 7px 13px;font-weight:700;font-size:14px;min-height:36px;
  background-image:linear-gradient(45deg,transparent 50%,var(--sub) 50%),linear-gradient(135deg,var(--sub) 50%,transparent 50%);
  background-position:calc(100% - 16px) 55%,calc(100% - 11px) 55%;background-size:5px 5px;background-repeat:no-repeat}
.rows{display:flex;flex-direction:column;gap:6px;padding:2px 0 9px}
.row{display:flex;gap:6px;overflow-x:auto;padding:0 16px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.row::-webkit-scrollbar{display:none}
.row .lab{flex:none;align-self:center;font-size:12px;color:var(--sub);font-weight:700;width:34px}
.chip{flex:none;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:7px 13px;
  font-size:14px;font-weight:600;min-height:36px;white-space:nowrap}
.chip[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:#fff}
.bud{display:flex;align-items:center;gap:10px;padding:0 16px}
.bud input{flex:1;accent-color:var(--accent);min-height:30px}
.bud output{font-weight:800;font-size:14px;min-width:92px;text-align:right}

/* ── 피드 ───────────────────────────────────── */
.feedhd{display:flex;align-items:baseline;justify-content:space-between;padding:14px 16px 8px;gap:10px}
.feedhd h1{margin:0;font-size:17px;font-weight:900;letter-spacing:-.01em}
.feedhd small{color:var(--sub);font-size:13px;font-weight:600}
.sort{display:flex;gap:4px;padding:0 16px 10px}
.sort button{border:0;background:transparent;color:var(--sub);font-weight:700;font-size:13px;padding:6px 10px;
  border-radius:8px;min-height:32px}
.sort button[aria-pressed="true"]{background:var(--soft);color:var(--ink)}
.feed{display:flex;flex-direction:column;gap:10px;padding:0 16px 120px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden}
.card>button{display:flex;width:100%;border:0;background:transparent;text-align:left;padding:0;align-items:stretch}
.ph{flex:none;width:84px;min-height:104px;display:flex;align-items:flex-end;padding:8px;color:#fff;
  font-size:11px;font-weight:800;letter-spacing:.02em;text-shadow:0 1px 2px rgba(0,0,0,.25)}
.bd{flex:1;min-width:0;padding:11px 13px 11px 12px;display:flex;flex-direction:column;gap:3px}
.l1{display:flex;align-items:center;justify-content:space-between;gap:8px}
.city{font-weight:900;font-size:17px;letter-spacing:-.01em;overflow-wrap:anywhere}
.city small{font-weight:600;color:var(--sub);font-size:12px;margin-left:5px}
.stamp{flex:none;font-size:12px;font-weight:900;color:var(--accent2);border:1.5px solid var(--accent);
  border-radius:5px;padding:1px 6px;transform:rotate(-3deg);white-space:nowrap}
.stamp.t2{background:#FFF1EC}.stamp.t3{background:var(--accent);color:#fff;border-color:var(--accent)}
.rec{flex:none;font-size:12px;font-weight:800;color:var(--accent2);white-space:nowrap}
.price{font-weight:900;font-size:19px;letter-spacing:-.02em}
.price small{font-size:12px;font-weight:700;color:var(--sub);margin-left:4px}
.dt{font-size:13px;color:var(--ink);font-weight:600}
.dt small{color:var(--sub);font-weight:600;font-size:12px;margin-left:5px}
.meta{display:flex;flex-wrap:wrap;gap:4px 8px;font-size:12px;color:var(--sub);font-weight:600}
.meta .dir{color:var(--coast);font-weight:800}

/* 확장 상세 — 결정하는 자리 */
.det{border-top:1px solid var(--line);padding:13px 14px 14px;display:flex;flex-direction:column;gap:12px}
.det h2{margin:0;font-size:13px;color:var(--sub);font-weight:800}
.cmp{display:flex;flex-direction:column;gap:6px}
.bar{display:grid;grid-template-columns:96px 1fr;align-items:center;gap:8px;font-size:13px;font-weight:700}
.bar i{display:block;height:10px;border-radius:5px;background:var(--line)}
.bar.now i{background:var(--accent)}
.bar b{font-weight:800}
.why{margin:0;font-size:14px;font-weight:700;color:var(--ink)}
.abs{margin:0;font-size:12px;color:var(--sub);line-height:1.5}
.adnote,.pnote{margin:0;font-size:12px;color:var(--sub);line-height:1.5}
.links{display:flex;flex-direction:column;gap:6px}
.lk{display:flex;align-items:center;justify-content:space-between;border:1px solid var(--line);border-radius:11px;
  padding:11px 13px;font-weight:800;font-size:14px;background:var(--card);min-height:44px}
.lk small{color:var(--sub);font-weight:700;font-size:12px}
.more{font-size:13px;font-weight:800;color:var(--coast)}
.empty{padding:34px 16px;text-align:center;color:var(--sub);font-weight:600}
.empty button{margin-top:10px;border:1px solid var(--line);background:var(--card);border-radius:999px;padding:9px 16px;font-weight:800}

/* ── B안: 지도 버튼 + 전체 화면 지도 ─────────── */
.fab{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(18px + env(safe-area-inset-bottom,0px));z-index:30;
  border:0;background:var(--ink);color:#fff;font-weight:800;font-size:15px;border-radius:999px;padding:13px 22px;
  min-height:48px;box-shadow:0 6px 20px rgba(32,53,58,.28);display:flex;gap:8px;align-items:center}
.fab svg{width:17px;height:17px}
.mapv{position:fixed;inset:0;z-index:50;background:var(--sea);display:flex;flex-direction:column}
.mapv canvas{flex:1;width:100%;min-height:0;display:block;touch-action:none}
.mtop{position:absolute;top:calc(10px + env(safe-area-inset-top,0px));left:12px;right:12px;display:flex;
  justify-content:space-between;gap:8px;pointer-events:none}
.mtop>*{pointer-events:auto}
.pill{flex:none;border:0;background:var(--card);border-radius:999px;padding:10px 13px;font-weight:800;font-size:14px;min-height:44px;
  box-shadow:0 2px 10px rgba(32,53,58,.16)}
.pill.dark{background:var(--ink);color:#fff}
.stages{display:flex;background:var(--card);border-radius:999px;padding:3px;box-shadow:0 2px 10px rgba(32,53,58,.16)}
.stages button{border:0;background:transparent;border-radius:999px;padding:8px 8px;font-size:12px;letter-spacing:-.02em;font-weight:800;
  color:var(--sub);min-height:38px}
.stages button[aria-pressed="true"]{background:var(--ink);color:#fff}
.mcount{position:absolute;left:12px;bottom:calc(14px + env(safe-area-inset-bottom,0px));background:rgba(255,255,255,.92);
  border-radius:9px;padding:6px 10px;font-size:12px;font-weight:700;color:var(--sub)}
.mcard{position:absolute;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));background:var(--card);
  border-radius:16px;box-shadow:0 8px 28px rgba(32,53,58,.25);overflow:hidden;display:flex}
.mcard .ph{width:74px;min-height:92px}
.mcard .bd{padding:10px 12px}
.mcard .go{border:0;background:var(--ink);color:#fff;border-radius:9px;padding:8px 12px;font-weight:800;font-size:13px;
  align-self:flex-start;margin-top:4px;min-height:36px}
.mcard .x{position:absolute;top:4px;right:4px;border:0;background:transparent;font-size:20px;color:var(--sub);
  width:40px;height:40px;line-height:1}
@media (prefers-reduced-motion:no-preference){.card,.chip,.fab{transition:background-color .15s,color .15s}}
</style>

<div class="mock" role="region" aria-label="목업 조작">
  <div class="seg" role="group" aria-label="안 고르기">
    <button type="button" id="varA" aria-pressed="true">A · 피드만</button>
    <button type="button" id="varB" aria-pressed="false">B · 피드 + 지도 버튼</button>
  </div>
  <p id="mocknote"></p>
</div>

<div class="top">
  <div class="hd">
    <div class="logo">갈래<em>말래</em></div>
    <div class="hdr">
      <select class="orig" id="origin" aria-label="출발지"></select>
      <button type="button" class="chip" id="fbtn" aria-expanded="false" aria-controls="rows">필터</button>
    </div>
  </div>
  <div class="row" id="rowHaul" role="group" aria-label="거리" style="padding-bottom:9px"><span class="lab">거리</span></div>
  <div class="rows" id="rows" hidden>
    <div class="row" id="rowMood" role="group" aria-label="분위기"><span class="lab">분위기</span></div>
    <div class="row" id="rowWhen" role="group" aria-label="언제"><span class="lab">언제</span></div>
    <div class="bud"><span class="lab" style="font-size:12px;color:var(--sub);font-weight:700;width:34px">예산</span>
      <input type="range" id="budget" min="5" max="200" step="5" value="200" aria-label="예산 상한(만원)">
      <output id="budgetOut" class="num" for="budget"></output></div>
  </div>
</div>

<div class="feedhd"><h1>오늘의 발견</h1><small id="count" class="num"></small></div>
<div class="sort" role="group" aria-label="정렬">
  <button type="button" data-sort="price" aria-pressed="true">싼 순</button>
  <button type="button" data-sort="discount" aria-pressed="false">할인율순</button>
  <button type="button" data-sort="soon" aria-pressed="false">임박순</button>
</div>
<div class="feed" id="feed"></div>

<button type="button" class="fab" id="fab" hidden>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z"/><path d="M9 4v14M15 6v14"/></svg>
  지도로 보기</button>

<div class="mapv" id="mapv" hidden>
  <canvas id="cv" aria-label="딜 지도"></canvas>
  <div class="mtop">
    <button type="button" class="pill dark" id="mapClose">← 목록</button>
    <div class="stages" role="group" aria-label="거리 단계">
      <button type="button" data-st="near" aria-pressed="false">가까운 곳</button>
      <button type="button" data-st="mid" aria-pressed="true">조금 더 멀리</button>
      <button type="button" data-st="far" aria-pressed="false">아주 멀리</button>
    </div>
  </div>
  <div class="mcount num" id="mcount"></div>
  <div class="mcard" id="mcard" hidden></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const DATA = __DATA__;
const WORLD = __WORLD__;
</script>
<script>
(function(){
"use strict";
const $ = s => document.querySelector(s);
const GRAD = {"해변":"linear-gradient(135deg,#8fd0e0,#2a6f8f)","온천":"linear-gradient(135deg,#ffc07a,#e0782f)",
  "도시":"linear-gradient(135deg,#ff9a76,#c6472a)","미식":"linear-gradient(135deg,#f2603f,#7a2e18)",
  "자연":"linear-gradient(135deg,#a8e0c0,#2a8f6c)","문화":"linear-gradient(135deg,#ffcf9a,#c6652a)"};
const TOP = ["해변","도시","미식","자연","문화","온천"];
const WHEN = ["이번 주말","다음 주말","이번 주","이번 달","다음 달"];
const HAUL = [["short","가까운 곳"],["mid","조금 더 멀리"],["long","아주 멀리"]];
const WD = "일월화수목금토";
const st = {variant:"A", origin:"SEL", haul:null, mood:null, when:null, budget:200, sort:"price", open:null, stage:"mid", pick:null};

const won = v => v.toLocaleString("ko-KR") + "원";
const md = s => { const d = new Date(s + "T00:00:00"); return (d.getMonth()+1) + "/" + d.getDate() + "(" + WD[d.getDay()] + ")"; };
function fresh(seen){
  if(!seen) return "발견가 · 스캔 시점 기준";
  const h = (Date.now() - new Date(seen).getTime()) / 36e5;
  if(h < 3) return "발견가 · 방금 가격";
  if(h < 24) return "발견가 · " + Math.floor(h) + "시간 전 가격";
  if(h < 48) return "발견가 · 어제 가격";
  return "발견가 · " + Math.floor(h/24) + "일 전 가격";
}
function absTime(seen){
  const d = new Date(seen); const p = n => String(n).padStart(2,"0");
  return (d.getMonth()+1) + "/" + d.getDate() + "(" + WD[d.getDay()] + ") " + p(d.getHours()) + ":" + p(d.getMinutes()) + " 기준";
}
const tier = d => d.discount >= 42 ? "t3" : d.discount >= 28 ? "t2" : d.discount >= 15 ? "t1" : null;
const isRecord = d => d.low != null && d.obs >= 14 && d.price < d.low && (1 - d.price/d.low) >= 0.05;
const topTag = d => d.tags.find(t => TOP.includes(t)) || "도시";
const subTags = d => d.tags.filter(t => !TOP.includes(t)).slice(0,2);

function list(){
  let a = DATA.deals.filter(d => d.o === st.origin && d.price <= st.budget * 10000);
  if(st.haul) a = a.filter(d => d.haul === st.haul);
  if(st.mood) a = a.filter(d => d.tags.includes(st.mood));
  if(st.when === "later") a = a.filter(d => !WHEN.includes(d.when));
  else if(st.when) a = a.filter(d => d.when === st.when);
  const by = {price:(x,y)=>x.price-y.price, discount:(x,y)=>y.discount-x.discount||x.price-y.price,
              soon:(x,y)=>x.dep.localeCompare(y.dep)||x.price-y.price}[st.sort];
  return a.slice().sort(by);
}

/* ── 필터 칩 ── */
function chips(row, items, key){
  const el = $(row); [...el.querySelectorAll(".chip")].forEach(n => n.remove());
  items.forEach(([val,label]) => {
    const b = document.createElement("button"); b.type = "button"; b.className = "chip"; b.textContent = label;
    b.setAttribute("aria-pressed", String(st[key] === val));
    b.onclick = () => { st[key] = st[key] === val ? null : val; st.open = null; render(); };
    el.appendChild(b);
  });
}
function renderFilters(){
  chips("#rowHaul", HAUL, "haul");
  chips("#rowMood", TOP.map(t => [t,t]), "mood");
  chips("#rowWhen", WHEN.map(w => [w,w]).concat([["later","그 이후"]]), "when");
  $("#budgetOut").textContent = st.budget >= 200 ? "상한 없음" : st.budget + "만원까지";
  const n = [st.mood, st.when].filter(Boolean).length + (st.budget < 200 ? 1 : 0);
  $("#fbtn").textContent = (n ? "필터 " + n : "필터") + ($("#rows").hidden ? " ▾" : " ▴");
}

/* ── 카드 ── */
function thumb(d, cls){ return '<div class="ph" style="background:' + GRAD[topTag(d)] + '">' + (cls||"") + topTag(d) + '</div>'; }
function mark(d){
  const t = tier(d);
  if(t) return '<span class="stamp ' + t + '">평소보다 ' + d.discount + '%↓</span>';
  if(isRecord(d)) return '<span class="rec">' + d.obs + '일 중 최저가예요</span>';
  return "";
}
function head(d){
  return '<div class="l1"><span class="city">' + d.ko + (d.country ? '<small>' + d.country + '</small>' : '') + '</span>' + mark(d) + '</div>' +
    '<div class="price num">' + won(d.price) + '<small>왕복</small></div>' +
    '<div class="dt num">' + md(d.dep) + '~' + md(d.ret) + '<small>' + (d.nights||"") + '</small></div>' +
    '<div class="meta"><span class="' + (d.tr === 0 ? "dir" : "") + '">' + (d.tr === 0 ? "직항" : "경유 " + d.tr + "회") + '</span>' +
    subTags(d).map(t => '<span>' + t + '</span>').join("") + '<span>' + fresh(d.seen) + '</span></div>';
}
function detail(d){
  let cmp;
  const shown = d.median != null && d.median > d.price && d.discount >= 1;   /* 0%↓ 는 「비슷해요」로 — DECISIONS 2026-09-21 (2) */
  if(shown){
    const w = Math.max(8, Math.round(d.price / d.median * 100));
    cmp = '<div class="cmp"><div class="bar"><span>평소 시세(중앙값)</span><span><i style="width:100%"></i></span></div>' +
      '<div class="bar num"><span></span><b>' + won(d.median) + '</b></div>' +
      '<div class="bar now"><span>발견가</span><span><i style="width:' + w + '%"></i></span></div>' +
      '<div class="bar num"><span></span><b>' + won(d.price) + ' · ' + d.discount + '%↓</b></div></div>';
  } else {
    cmp = '<p class="why">' + (d.median == null ? "아직 이 노선의 평소 시세를 모아두지 못했어요" : "지금은 평소 시세와 비슷해요") + '</p>';
  }
  const hasAd = d.links.some(l => l.ad);
  return '<div class="det"><div><h2>평소 시세와 비교</h2></div>' + cmp +
    (d.seen ? '<p class="abs">' + absTime(d.seen) + '<br>항공권 가격은 예약 사이트가 마지막으로 조회한 값이라 며칠 전일 수 있어요.</p>' : '') +
    (hasAd ? '<p class="adnote">(광고) 표시는 예약하시면 저희가 수수료를 받는 링크예요 · 가격은 같아요</p>' : '') +
    '<div class="links">' + d.links.map(l => '<div class="lk"><span>' + l.name + (l.ad ? ' <small>(광고)</small>' : '') + '</span><small>가격 확인 ›</small></div>').join("") + '</div>' +
    '<p class="pnote">위 가격은 발견가(스캔 시점) · 실시간 최저가는 각 사이트에서 확인하세요</p>' +
    (d.route ? '<div class="more">이 노선 시세 자세히 →</div>' : '') + '</div>';
}
function renderFeed(){
  const a = list(), feed = $("#feed");
  $("#count").textContent = DATA.origins[st.origin].name + " 출발 · " + a.length + "곳";
  if(!a.length){
    feed.innerHTML = '<div class="empty">조건에 맞는 곳이 아직 없어요<br><button type="button" id="reset">필터 지우기</button></div>';
    $("#reset").onclick = () => { st.haul = st.mood = st.when = null; st.budget = 200; $("#budget").value = 200; render(); };
    return;
  }
  feed.innerHTML = a.map(d => {
    const id = d.o + "-" + d.d, open = st.open === id;
    return '<article class="card" id="c-' + id + '"><button type="button" data-id="' + id + '" aria-expanded="' + open + '">' +
      thumb(d) + '<div class="bd">' + head(d) + '</div></button>' + (open ? detail(d) : '') + '</article>';
  }).join("");
  feed.querySelectorAll(".card>button").forEach(b => b.onclick = () => { st.open = st.open === b.dataset.id ? null : b.dataset.id; renderFeed(); });
}

/* ── 지도(B안) ── */
const cv = $("#cv"), ctx = cv.getContext("2d");
let proj, zoomT = d3.zoomIdentity, pins = [];
const STAGE = { near:{c:[128,33],k:6}, mid:{c:[116,20],k:3.2}, far:{c:[95,28],k:2.1} };
function sizeCanvas(){
  const r = cv.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio||1, 2);
  cv.width = Math.round(r.width*dpr); cv.height = Math.round(r.height*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0); return r;
}
function baseProj(r){ return d3.geoEquirectangular().fitExtent([[0,0],[r.width,r.height]], {type:"Sphere"}).rotate([-150,0]); }
function toStage(name, r){
  const s = STAGE[name]; proj = baseProj(r);
  const p = proj(s.c); zoomT = d3.zoomIdentity.translate(r.width/2 - p[0]*s.k, r.height*0.42 - p[1]*s.k).scale(s.k);
  d3.select(cv).call(zoom.transform, zoomT);
}
function draw(){
  const r = cv.getBoundingClientRect(); if(!r.width) return;
  ctx.clearRect(0,0,r.width,r.height); ctx.fillStyle = "#EDF4F3"; ctx.fillRect(0,0,r.width,r.height);
  ctx.save(); ctx.translate(zoomT.x, zoomT.y); ctx.scale(zoomT.k, zoomT.k);
  const path = d3.geoPath(proj, ctx);
  ctx.beginPath(); path(WORLD); ctx.fillStyle = "#D2E7DE"; ctx.fill();
  ctx.lineWidth = .6/zoomT.k; ctx.strokeStyle = "rgba(51,83,79,.35)"; ctx.stroke(); ctx.restore();
  const a = list(); if(!a.length){ pins = []; $("#mcount").textContent = "조건에 맞는 곳이 없어요"; return; }
  const lo = d3.min(a, d => d.price), hi = d3.max(a, d => d.price);
  const col = d3.interpolateRgb("#C6472A", "#F8C9BB");
  const og = DATA.origins[st.origin], op = zoomT.apply(proj([og.lon, og.lat]));
  pins = a.map(d => { const p = zoomT.apply(proj([d.lon, d.lat])); return {d, x:p[0], y:p[1], t:hi>lo ? (d.price-lo)/(hi-lo) : 0}; })
          .filter(p => p.x > -20 && p.x < r.width+20 && p.y > -20 && p.y < r.height+20);
  ctx.beginPath(); ctx.arc(op[0], op[1], 5, 0, 7); ctx.fillStyle = "#20353A"; ctx.fill();
  ctx.font = "800 12px " + getComputedStyle(document.body).fontFamily; ctx.textBaseline = "middle";
  const boxes = [];
  pins.slice().sort((p,q) => q.t - p.t).forEach(p => {       /* 싼 핀이 위에 그려지게 비싼 것부터 */
    const pk = st.pick && st.pick === p.d.o + "-" + p.d.d;
    ctx.beginPath(); ctx.arc(p.x, p.y, pk ? 10 : 7, 0, 7); ctx.fillStyle = col(p.t); ctx.fill();
    ctx.lineWidth = pk ? 3 : 1.5; ctx.strokeStyle = pk ? "#20353A" : "#fff"; ctx.stroke();
  });
  pins.slice().sort((p,q) => p.t - q.t).forEach(p => {       /* 라벨은 싼 곳부터 자리를 잡는다 */
    const txt = p.d.ko + " " + Math.round(p.d.price/10000) + "만", w = ctx.measureText(txt).width + 10;
    const b = {x:p.x + 10, y:p.y - 10, w, h:20};
    if(b.x + w > r.width - 4 || b.y < 60) return;
    if(boxes.some(o => b.x < o.x+o.w && b.x+b.w > o.x && b.y < o.y+o.h && b.y+b.h > o.y)) return;
    boxes.push(b); ctx.fillStyle = "rgba(255,255,255,.92)"; ctx.beginPath(); if(ctx.roundRect) ctx.roundRect(b.x, b.y, w, 20, 6); else ctx.rect(b.x, b.y, w, 20); ctx.fill();
    ctx.fillStyle = "#20353A"; ctx.fillText(txt, b.x + 5, b.y + 10.5);
  });
  $("#mcount").textContent = "지도에 " + pins.length + "곳 · 전체 " + a.length + "곳";
}
const zoom = d3.zoom().scaleExtent([1, 14]).on("zoom", e => { zoomT = e.transform; draw(); });
function pickAt(x, y){
  let best = null, bd = 26;
  pins.forEach(p => { const dd = Math.hypot(p.x - x, p.y - y); if(dd < bd){ bd = dd; best = p; } });
  return best;
}
function showPick(d){
  const mc = $("#mcard");
  if(!d){ st.pick = null; mc.hidden = true; $("#mcount").hidden = false; draw(); return; }
  st.pick = d.o + "-" + d.d; $("#mcount").hidden = true; mc.hidden = false;
  mc.innerHTML = thumb(d) + '<div class="bd">' + head(d) + '<button type="button" class="go">자세히 보기</button></div><button type="button" class="x" aria-label="닫기">×</button>';
  mc.querySelector(".x").onclick = () => showPick(null);
  mc.querySelector(".go").onclick = () => { const id = st.pick; closeMap(); st.open = id; renderFeed();
    const el = document.getElementById("c-" + id); if(el) el.scrollIntoView({block:"start", behavior:"auto"}); window.scrollBy(0, -220); };
  draw();
}
function openMap(){
  $("#mapv").hidden = false; document.documentElement.style.overflow = "hidden";
  const r = sizeCanvas(); d3.select(cv).call(zoom).on("dblclick.zoom", null);
  st.stage = st.haul === "short" ? "near" : st.haul === "long" ? "far" : "mid"; stageBtns(); toStage(st.stage, r);
}
function closeMap(){ $("#mapv").hidden = true; document.documentElement.style.overflow = ""; showPick(null); }
function stageBtns(){ document.querySelectorAll(".stages button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.st === st.stage))); }
cv.addEventListener("click", e => { const r = cv.getBoundingClientRect(), p = pickAt(e.clientX - r.left, e.clientY - r.top); showPick(p ? p.d : null); });
document.querySelectorAll(".stages button").forEach(b => b.onclick = () => { st.stage = b.dataset.st; stageBtns(); showPick(null); toStage(st.stage, cv.getBoundingClientRect()); });
$("#mapClose").onclick = closeMap; $("#fab").onclick = openMap;
window.addEventListener("resize", () => { if(!$("#mapv").hidden){ const r = sizeCanvas(); proj = baseProj(r); draw(); } });

/* ── 목업 조작 ── */
const NOTE = {
  A: "지도가 없습니다. 「가까운 곳·멀리」는 맨 위 거리 칩으로 내려왔습니다. 화면 전체가 카드입니다.",
  B: "기본은 같은 피드입니다. 아래 「지도로 보기」를 누르면 지도가 화면 전체를 씁니다 — 끌고 벌려서 둘러볼 수 있고, 핀을 누르면 카드가 뜹니다."
};
function setVariant(v){
  st.variant = v; $("#varA").setAttribute("aria-pressed", String(v === "A")); $("#varB").setAttribute("aria-pressed", String(v === "B"));
  $("#mocknote").textContent = NOTE[v]; $("#fab").hidden = v !== "B"; if(v !== "B") closeMap();
  try{ localStorage.setItem("mf-variant", v); }catch(e){}
}
$("#fbtn").onclick = () => { const r = $("#rows"); r.hidden = !r.hidden; $("#fbtn").setAttribute("aria-expanded", String(!r.hidden)); renderFilters(); };
$("#varA").onclick = () => setVariant("A"); $("#varB").onclick = () => setVariant("B");
document.querySelectorAll(".sort button").forEach(b => b.onclick = () => { st.sort = b.dataset.sort;
  document.querySelectorAll(".sort button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); renderFeed(); });
$("#budget").oninput = e => { st.budget = +e.target.value; st.open = null; render(); };
const sel = $("#origin");
Object.keys(DATA.origins).forEach(k => { const o = document.createElement("option"); o.value = k; o.textContent = DATA.origins[k].name + " 출발"; sel.appendChild(o); });
sel.onchange = () => { st.origin = sel.value; st.open = null; render(); };
function render(){ renderFilters(); renderFeed(); if(!$("#mapv").hidden) draw(); }
let v0 = "A"; try{ v0 = localStorage.getItem("mf-variant") || "A"; }catch(e){}
render(); setVariant(v0);
})();
</script>
"""

out = PAGE.replace("__DATA__", data_js).replace("__WORLD__", world_js)
path = os.path.join(BASE, "mobile_feed.html")
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(out)
print("deals", len(DATA["deals"]), "· generated", DATA["generated"], "·", len(out.encode("utf-8")) // 1024, "KB →", path)
