# -*- coding: utf-8 -*-
"""PH8 사진 큐레이션 — 목적지마다 자유 라이선스 사진 후보를 Wikimedia Commons 에서 고른다.

산출물:
  design/photos.json  목적지(한글 도시명) → 채택 1장 + 대안 2장 (제목·작가·라이선스·원본 페이지·800px URL)
  design/photos.html  사용자가 폰에서 훑어보는 검수 페이지 (「이건 아니다」만 골라내면 된다)

정책(SPEC §CH6 사진): 목적지당 1장 · 자유 라이선스(CC0 · CC BY · CC BY-SA · Public domain)만 · 출처 표기 · 비용 $0.
목적지 목록은 공개 URL(deals.json · routes/index.json)에서 받는다 — 같은 도시의 코드 여럿(NRT/TYO)은 한 사진을 쓴다.
검색은 영어 도시명으로(Commons 는 영어가 정확하다). 한글→영어 표는 이 파일이 가진다(기획 소유 참조 데이터).
소유: 기획 세션. 실행: python design/build_photos.py  (Commons API, 키 없음, 도시당 1~2회 호출)
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import _data

EN = {  # 한글 도시명 → 영어 검색어 (Commons)
 "오클랜드":"Auckland","암스테르담":"Amsterdam","바르셀로나":"Barcelona","베이징":"Beijing","코타키나발루":"Kota Kinabalu",
 "방콕":"Bangkok","브리즈번":"Brisbane","광저우":"Guangzhou","파리":"Paris","세부":"Cebu","제주":"Jeju Island","콜롬보":"Colombo",
 "치앙마이":"Chiang Mai","삿포로":"Sapporo","다낭":"Da Nang","델리":"New Delhi","다롄":"Dalian","도하":"Doha","발리":"Bali",
 "두바이":"Dubai","로마":"Rome","프랑크푸르트":"Frankfurt","후쿠오카":"Fukuoka","괌":"Guam","하노이":"Hanoi","항저우":"Hangzhou",
 "히로시마":"Hiroshima","홍콩":"Hong Kong","푸켓":"Phuket","호놀룰루":"Honolulu","이스탄불":"Istanbul","뉴욕":"New York City",
 "자카르타":"Jakarta","가오슝":"Kaohsiung","오사카":"Osaka","칼리보(보라카이)":"Boracay","구마모토":"Kumamoto","고마쓰":"Kanazawa",
 "가고시마":"Kagoshima","카트만두":"Kathmandu","쿠알라룸푸르":"Kuala Lumpur","로스앤젤레스":"Los Angeles","런던":"London",
 "멜버른":"Melbourne","마카오":"Macau","몰디브":"Maldives","마닐라":"Manila","뮌헨":"Munich","마쓰야마":"Matsuyama","나디":"Nadi Fiji",
 "나고야":"Nagoya","나트랑":"Nha Trang","도쿄":"Tokyo","오키나와":"Okinawa","푸꾸옥":"Phu Quoc","프라하":"Prague","양곤":"Yangon",
 "타이중":"Taichung","시애틀":"Seattle","샌프란시스코":"San Francisco","호치민":"Ho Chi Minh City","상하이":"Shanghai",
 "싱가포르":"Singapore","사이판":"Saipan","시드니":"Sydney","싼야":"Sanya","선전":"Shenzhen","보홀":"Bohol","칭다오":"Qingdao",
 "타이베이":"Taipei","울란바토르":"Ulaanbaatar","빈":"Vienna","비엔티안":"Vientiane","샤먼":"Xiamen","토론토":"Toronto",
 "밴쿠버":"Vancouver","취리히":"Zurich",
}
# 도시 사진에서 흔한 잡음: 지도·깃발·로고·문장·표지판·도표·항공기·공항 내부
BAD = re.compile(r"map|flag|logo|coat|seal|emblem|diagram|chart|sign|airport|aircraft|airplane|plane|boeing|airbus|"
                 r"metro|subway|station|bus|train|tram|car|road|highway|screenshot|poster|stamp|coin|banknote|"
                 r"statue|portrait|people|man|woman|girl|boy|wedding|football|stadium|logo", re.I)
OK_LIC = re.compile(r"^(CC0|CC BY( ?[\d.]+)?|CC BY-SA( ?[\d.]+)?|Public domain|CC-BY(-SA)?( ?[\d.]+)?)", re.I)
UA = {"User-Agent": "galmal-plan-photos/1 (https://galmal.kr; design/build_photos.py)"}
API = "https://commons.wikimedia.org/w/api.php"


def api(params):
    params.update(format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def search(q, n=12):
    r = api({"action": "query", "list": "search", "srnamespace": 6, "srlimit": n,
             "srsearch": f'{q} filetype:bitmap -intitle:map -intitle:flag'})
    return [x["title"] for x in r.get("query", {}).get("search", [])]


def info(titles):
    if not titles: return []
    r = api({"action": "query", "prop": "imageinfo", "titles": "|".join(titles),
             "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 800})
    out = []
    for p in r.get("query", {}).get("pages", []):
        ii = (p.get("imageinfo") or [None])[0]
        if not ii: continue
        m = ii.get("extmetadata", {})
        g = lambda k: re.sub(r"<[^>]+>", "", m.get(k, {}).get("value", "") or "").strip()
        out.append({"title": p["title"], "w": ii.get("width", 0), "h": ii.get("height", 0), "mime": ii.get("mime", ""),
                    "thumb": ii.get("thumburl"), "page": ii.get("descriptionurl"),
                    "license": g("LicenseShortName"), "license_url": g("LicenseUrl"), "author": g("Artist")[:80],
                    "desc": g("ImageDescription")[:140]})
    return out


BEACH = ("몰디브","보홀","푸켓","괌","사이판","발리","세부","보라카이","오키나와","나트랑","푸꾸옥","싼야","나디","코타키나발루","호놀룰루","제주","다낭")
BAD2 = re.compile(r"painting|drawing|print|engraving|ukiyo|woodblock|sketch|illustration|engine|motor|interior|museum|"
                  r"artwork|lithograph|watercolor|montage|collage|book|page|scan|manuscript|bombing|air raid|war|"
                  r"1[0-8]\d\d|19[0-7]\d|rooftop|garden|roof", re.I)


def cat_members(cat, n=40):
    r = api({"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cat, "cmnamespace": 6,
             "cmtype": "file", "cmlimit": n})
    return [x["title"] for x in r.get("query", {}).get("categorymembers", [])]


def wiki_lead(en):
    """en.wikipedia 문서의 대표 사진 파일명 — 사람이 고른 사진이라 잡음이 적다."""
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "prop": "pageimages", "piprop": "name", "titles": en, "redirects": 1, "format": "json", "formatversion": "2"})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        j = json.load(r)
    for pg in j.get("query", {}).get("pages", []):
        n = pg.get("pageimage")
        if n: return "File:" + n
    return None


def good(rows):
    out = [r for r in rows if OK_LIC.match(r["license"]) and r["mime"] in ("image/jpeg", "image/png")
           and r["w"] >= 1200 and r["w"] > r["h"] * 1.15 and not BAD.search(r["title"]) and not BAD2.search(r["title"])
           and not BAD2.search(r["desc"]) and r["thumb"]]
    def rank(r):  # 오래된 흑백(PD)이 위로 오는 걸 막는다 — 최신 CC 를 앞에, PD 는 맨 뒤
        Lc = r["license"].upper()
        return (2 if Lc.startswith("PUBLIC") else 0 if ("4.0" in Lc or Lc.startswith("CC0")) else 1, -min(r["w"], 4000))
    out.sort(key=rank)
    return out


def voyage_banner(en):
    """en.wikivoyage 페이지 배너 — 여행 가이드가 고른 대표 사진(7:1, 자유 라이선스)."""
    url = "https://en.wikivoyage.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "prop": "pageprops", "titles": en, "redirects": 1, "format": "json", "formatversion": "2"})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        j = json.load(r)
    for pg in j.get("query", {}).get("pages", []):
        b = (pg.get("pageprops") or {}).get("wpb_banner")
        if b: return "File:" + b
    return None


def pick(ko, en):
    city = en.replace(" City", "").replace(" Fiji", "").replace(" Island", "")
    beach = any(k in ko for k in BEACH)
    # 여행지 분류를 앞에, 도시 풍경(skyline)은 맨 뒤 — 2026-09-29 사용자: 「여행지라고 보기엔 너무 도시 사진」
    cats = ([f"Beaches of {city}", f"Beaches in {city}"] if beach else []) + [
        f"Tourist attractions in {city}", f"Landmarks in {city}", f"Temples in {city}", f"Old town of {city}",
        f"Historic centre of {city}", f"Parks in {city}", f"Night in {city}", f"Views of {city}", f"Skylines of {city}"]
    pool = []
    for c in cats:
        try: pool += [t for t in cat_members(c) if t not in pool]
        except Exception: pass
        if len(pool) >= 60: break
    rows = []
    for i in range(0, min(len(pool), 60), 20): rows += info(pool[i:i+20])
    g = good(rows)
    front = []
    for fn in (voyage_banner, wiki_lead):          # 사람이 고른 대표 사진을 맨 앞에: Wikivoyage 배너 → 위키백과 대표
        try:
            t = fn(en)
            if t:
                r = good(info([t]))
                if r and r[0]["title"] not in [x["title"] for x in front]: front += r
        except Exception: pass
    g = front + [x for x in g if x["title"] not in [f["title"] for f in front]]
    if len(g) < 3:
        cands = []
        for q in (f'"{city}" temple', f'"{city}" landmark', f'"{city}" beach' if beach else f'"{city}" old town'):
            try: cands += [t for t in search(q) if t not in cands and t not in pool]
            except Exception: pass
        g += [r for r in good(info(cands[:20])) if r["title"] not in [x["title"] for x in g]]
    return g[:3]


def main():
    D = _data.deals(); ri = json.loads(_data.api_text("routes/index.json"))
    codes = {}
    for d in D["deals"]: codes.setdefault(d["ko"], set()).add(d["d"])
    for r in ri["routes"]: codes.setdefault(r["d_name"], set()).add(r["d"])
    out = {}; miss = []
    for ko in sorted(codes):
        en = EN.get(ko)
        if not en: miss.append(ko); continue
        try:
            c = pick(ko, en)
        except Exception as e:
            print("ERR", ko, type(e).__name__, e); c = []
        out[ko] = {"codes": sorted(codes[ko]), "en": en, "chosen": c[0] if c else None, "alternates": c[1:3]}
        print(f"{ko:<10} {'OK' if c else '--'} {len(c)}  {c[0]['license'] if c else ''}")
        time.sleep(0.4)
    io.open(os.path.join(BASE, "photos.json"), "w", encoding="utf-8", newline="").write(
        json.dumps({"generated": D["generated"], "source": "Wikimedia Commons", "cities": out}, ensure_ascii=False, indent=1))
    n_ok = sum(1 for v in out.values() if v["chosen"])
    print(f"\n도시 {len(out)} · 후보 있음 {n_ok} · 없음 {len(out)-n_ok} · 영어명 없음 {miss}")
    # ── 검수 페이지
    cards = []
    for i, (ko, v) in enumerate(sorted(out.items()), 1):
        if not v["chosen"]:
            cards.append(f'<article class="c none"><div class="ph">후보 없음</div><div class="bd"><b>{i}. {ko}</b><small>{" · ".join(v["codes"])}</small></div></article>'); continue
        ch = v["chosen"]; alts = "".join(f'<a href="{a["page"]}" target="_blank" rel="noopener"><img loading="lazy" src="{a["thumb"]}" alt=""></a>' for a in v["alternates"])
        cards.append(f'''<article class="c"><a href="{ch["page"]}" target="_blank" rel="noopener"><img loading="lazy" src="{ch["thumb"]}" alt="{ko}"></a>
<div class="bd"><b>{i}. {ko}</b><small>{" · ".join(v["codes"])} · {ch["license"]} · {ch["author"] or "작가 미상"}</small>
<div class="alts">{alts}</div></div></article>''')
    html = f'''<title>목적지 사진 검수</title><meta charset="utf-8">
<style>:root{{--ink:#20353A;--sub:#5E7A7C;--line:#E6EDEC;--bg:#F4F8F7;--accent:#F2603F}}html{{color-scheme:light}}
body{{background:var(--bg);color:var(--ink);font-family:'Pretendard Variable',Pretendard,-apple-system,'Apple SD Gothic Neo',sans-serif;padding:0 16px 40px;margin:0}}
h1{{font-size:18px;margin:16px 0 4px}}p{{color:var(--sub);font-size:13px;margin:0 0 14px;line-height:1.5}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}}
.c{{background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}}
.c img{{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:#dde}}
.c.none .ph{{aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;color:var(--sub);font-weight:700}}
.bd{{padding:8px 10px 10px}}b{{font-size:14px}}small{{display:block;color:var(--sub);font-size:11px;line-height:1.4;margin-top:2px;overflow-wrap:anywhere}}
.alts{{display:flex;gap:4px;margin-top:6px}}.alts img{{width:48px;height:36px;border-radius:5px}}</style>
<h1>목적지 사진 검수 — {len(out)}곳</h1>
<p>Wikimedia Commons 자유 라이선스(CC0·CC BY·CC BY-SA·PD)에서 자동으로 고른 1차 후보. 큰 사진이 채택안, 아래 작은 두 장이 대안.
<b>「이건 아니다」인 번호만</b> 알려주면 된다(대안 중 하나면 「12 → 두 번째」). 누르면 원본 페이지.</p>
<div class="g">{"".join(cards)}</div>'''
    io.open(os.path.join(BASE, "photos.html"), "w", encoding="utf-8", newline="").write(html)


if __name__ == "__main__":
    main()
