# -*- coding: utf-8 -*-
"""PH8 사진 2차 — 사용자가 「이상하다」고 한 도시만, **랜드마크를 사람이 지정해** 다시 찾는다.

1차(build_photos.py) 결과를 사용자가 검수했다(2026-09-29): 77곳 중 39곳 OK. 나머지 38곳은 「괌이면 해변, 뉴욕이면 자유의 여신상 —
유튜브 썸네일처럼 보고 매력적이어야 한다」. 분류·검색으로는 「상징적인가」를 못 가르므로, 도시마다 **찾을 랜드마크를 기획이 손으로 적는다.**
품질 신호: Commons 의 Featured/Quality/Valued 판정(extmetadata `Assessments`)을 우선한다 — 사람이 「잘 찍혔다」고 표를 준 사진이다.

산출물: photos.json 갱신(OK 도시는 그대로, 38곳은 새 후보 최대 4장) · photos2.html(38곳만 검수)
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from build_photos import api, info, OK_LIC, BAD, BAD2, UA  # noqa

OK_NUMS = {5, 8, 9, 12, 13, 14, 15, 17, 18, 20, 23, 24, 25, 26, 29, 34, 37, 40, 42, 43, 46, 48, 49, 51, 52, 56, 59, 63, 64, 65, 66, 67, 68, 69, 71, 72, 73, 76, 77}

# 도시 → 검색어(랜드마크) 셋. 앞이 더 상징적.
LANDMARK = {
 "가고시마": ["Sakurajima volcano Kagoshima", "Sengan-en Kagoshima", "Kagoshima bay Sakurajima sunset"],
 "가오슝": ["Lotus Pond Kaohsiung Dragon Tiger Pagodas", "Fo Guang Shan Buddha Museum", "Pier-2 Art Center Kaohsiung"],
 "고마쓰": ["Kenrokuen garden Kanazawa", "Higashi Chaya Kanazawa", "Kanazawa Castle"],
 "괌": ["Tumon Bay Guam beach", "Two Lovers Point Guam", "Ritidian beach Guam"],
 "구마모토": ["Kumamoto Castle", "Suizenji garden Kumamoto", "Mount Aso crater"],
 "나고야": ["Nagoya Castle", "Atsuta Shrine", "Oasis 21 Nagoya night"],
 "뉴욕": ["Statue of Liberty", "Brooklyn Bridge Manhattan skyline", "Times Square night"],
 "다낭": ["Golden Bridge Ba Na Hills", "My Khe beach Da Nang", "Dragon Bridge Da Nang night"],
 "두바이": ["Burj Khalifa Dubai", "Burj Al Arab beach", "Dubai Marina night"],
 "로스앤젤레스": ["Hollywood Sign", "Santa Monica Pier sunset", "Griffith Observatory Los Angeles"],
 "마쓰야마": ["Dogo Onsen Honkan", "Matsuyama Castle", "Botchan train Matsuyama"],
 "마카오": ["Ruins of St. Paul's Macau", "Senado Square Macau", "Macau Tower night"],
 "발리": ["Tanah Lot temple", "Tegallalang rice terraces", "Uluwatu temple cliff"],
 "방콕": ["Wat Arun Bangkok", "Grand Palace Bangkok", "Wat Pho reclining Buddha"],
 "베이징": ["Forbidden City Beijing", "Great Wall Mutianyu", "Temple of Heaven Beijing"],
 "보홀": ["Chocolate Hills Bohol", "Alona Beach Panglao", "Bohol tarsier"],
 "브리즈번": ["Brisbane Story Bridge night", "South Bank Brisbane Streets Beach", "Brisbane River city skyline"],
 "비엔티안": ["Pha That Luang Vientiane", "Patuxai Vientiane", "Buddha Park Vientiane"],
 "사이판": ["Saipan Micro Beach", "Managaha island Saipan", "Saipan lagoon aerial"],
 "삿포로": ["Odori Park Sapporo", "Sapporo Clock Tower", "Sapporo snow festival"],
 "샌프란시스코": ["Golden Gate Bridge", "Painted Ladies Alamo Square", "San Francisco cable car"],
 "샤먼": ["Gulangyu island Xiamen", "Xiamen University campus", "Nanputuo Temple Xiamen"],
 "세부": ["Kawasan Falls Cebu", "Magellan's Cross Cebu", "Bantayan island beach"],
 "싱가포르": ["Marina Bay Sands Singapore night", "Gardens by the Bay Supertree", "Merlion Singapore"],
 "싼야": ["Yalong Bay Sanya beach", "Sanya Nanshan Guanyin", "Wuzhizhou island Sanya"],
 "양곤": ["Shwedagon Pagoda", "Sule Pagoda Yangon", "Yangon colonial buildings"],
 "오키나와": ["Okinawa Churaumi Aquarium", "Shuri Castle Okinawa", "Okinawa beach Zamami"],
 "자카르타": ["Monas Jakarta", "Istiqlal Mosque Jakarta", "Kota Tua Jakarta"],
 "제주": ["Seongsan Ilchulbong", "Hyeopjae beach Jeju", "Jeju Hallasan"],
 "취리히": ["Zurich Grossmünster Limmat", "Lake Zurich", "Zurich old town"],
 "칭다오": ["Qingdao Zhanqiao pier", "Qingdao Badaguan", "Laoshan Qingdao"],
 "카트만두": ["Boudhanath stupa", "Swayambhunath Kathmandu", "Kathmandu Durbar Square"],
 "코타키나발루": ["Kota Kinabalu sunset Tanjung Aru", "Mount Kinabalu", "Kota Kinabalu City Mosque"],
 "콜롬보": ["Galle Face Green Colombo", "Gangaramaya Temple Colombo", "Colombo Lotus Tower"],
 "쿠알라룸푸르": ["Petronas Towers", "Batu Caves", "Kuala Lumpur skyline night"],
 "프랑크푸르트": ["Frankfurt Römer", "Frankfurt skyline Main river", "Frankfurt Eiserner Steg"],
 "호치민": ["Saigon Notre-Dame Basilica", "Ben Thanh Market", "Ho Chi Minh City Hall"],
 "홍콩": ["Victoria Peak Hong Kong night", "Hong Kong Victoria Harbour", "Tian Tan Buddha"],
}
NOISE = re.compile(r"map|flag|logo|stamp|coin|diagram|plan|model|replica|toy|lego|poster|screenshot|drawing|painting|"
                   r"interior|ticket|menu|sign\b|plaque|statue of .* (bust|head)|closeup|close-up|detail", re.I)


def search(q, n=15):
    r = api({"action": "query", "list": "search", "srnamespace": 6, "srlimit": n, "srsearch": f'{q} filetype:bitmap'})
    return [x["title"] for x in r.get("query", {}).get("search", [])]


def assess(t):
    r = api({"action": "query", "prop": "imageinfo", "titles": t, "iiprop": "extmetadata"})
    for p in r.get("query", {}).get("pages", []):
        m = ((p.get("imageinfo") or [{}])[0]).get("extmetadata", {})
        return (m.get("Assessments", {}) or {}).get("value", "")
    return ""


def pick(ko):
    seen, rows = [], []
    for q in LANDMARK[ko]:
        try: titles = [t for t in search(q) if t not in seen]
        except Exception: titles = []
        seen += titles
        for r in info(titles[:12]): r["q"] = q; rows.append(r)
        time.sleep(0.3)
    good = [r for r in rows if OK_LIC.match(r["license"]) and r["mime"] in ("image/jpeg", "image/png")
            and r["w"] >= 1200 and r["w"] > r["h"] * 1.1 and not NOISE.search(r["title"]) and not BAD2.search(r["title"]) and r["thumb"]]
    for r in good[:24]:
        try: r["assess"] = assess(r["title"])
        except Exception: r["assess"] = ""
    qi = {q: i for i, q in enumerate(LANDMARK[ko])}
    good.sort(key=lambda r: (0 if r.get("assess") else 1, qi[r["q"]], 0 if "4.0" in r["license"] or r["license"].startswith("CC0") else 1, -min(r["w"], 4000)))
    return good[:4]


def main():
    j = json.load(io.open(os.path.join(BASE, "photos.json"), encoding="utf-8")); c = j["cities"]
    names = sorted(c)
    redo = [ko for i, ko in enumerate(names, 1) if i not in OK_NUMS]
    for i, ko in enumerate(names, 1):
        c[ko]["ok"] = (i in OK_NUMS)
    for ko in redo:
        try: g = pick(ko)
        except Exception as e: print("ERR", ko, e); g = []
        if g: c[ko]["chosen"], c[ko]["alternates"] = g[0], g[1:4]
        print(ko, len(g), (g[0]["assess"] or "-") if g else "")
    io.open(os.path.join(BASE, "photos.json"), "w", encoding="utf-8", newline="").write(json.dumps(j, ensure_ascii=False, indent=1))
    print("done", len(redo))


if __name__ == "__main__":
    main()
