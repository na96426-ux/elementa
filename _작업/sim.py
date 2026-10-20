# -*- coding: utf-8 -*-
"""index.html 의 데이터를 읽어 자동 플레이 검사를 돌린다.
  python3 -I sim.py            # 검증 + 무작위 플레이 2000판 + 똑똑한 플레이 2000판
  python3 -I sim.py 5000       # 판 수 지정
결과: 도달 가능성, 평균 시도 횟수, 가장 늦게 발견되는 원소(막히기 쉬운 곳), 레시피 분포."""
import re, sys, os, random, statistics
from collections import Counter, defaultdict

HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
s = open(HTML, encoding="utf-8").read()
el_src = re.search(r"var ELEMENT_DATA = \[(.*?)\n  \];", s, re.S).group(1)
rec_src = re.search(r"var RECIPE_DATA = \[(.*?)\n  \];", s, re.S).group(1)
ELS = [l.split("|") for l in re.findall(r'"([^"]+)"', el_src)]
RECS = re.findall(r'"([^"+]+)\+([^"=]+)=([^"]+)"', rec_src)
BASE = ["불", "물", "흙", "공기"]
NAMES = [e[0] for e in ELS]
CAT = {e[0]: e[2] for e in ELS}
key = lambda a, b: (a, b) if a < b else (b, a)
REC = {}
for a, b, r in RECS:
    k = key(a, b)
    assert k not in REC or REC[k] == r, ("충돌", k, REC[k], r)
    REC[k] = r
nameset = set(NAMES)
for a, b, r in RECS:
    assert a in nameset and b in nameset and r in nameset, (a, b, r)
assert len(NAMES) == len(nameset), "이름 중복"

def reach():
    found = set(BASE); changed = True
    while changed:
        changed = False
        for (a, b), r in REC.items():
            if a in found and b in found and r not in found:
                found.add(r); changed = True
    return found

def play(mode, rng):
    """한 판. mode: random = 아무 쌍이나 / smart = 아직 안 해 본 쌍만.
    돌려주는 값: 총 시도 수, 발견 순서."""
    found = list(BASE); fset = set(found); tried = set(); order = []; tries = 0
    total = len(NAMES)
    while len(found) < total:
        tries += 1
        if mode == "random":
            a = rng.choice(found); b = rng.choice(found)
        else:
            # 아직 안 해 본 쌍 중 무작위 (실제 플레이어는 같은 실수를 잘 반복하지 않음)
            for _ in range(200):
                a = rng.choice(found); b = rng.choice(found)
                if key(a, b) not in tried: break
            tried.add(key(a, b))
        r = REC.get(key(a, b))
        if r and r not in fset:
            found.append(r); fset.add(r); order.append((r, tries))
        if tries > 400000:
            return tries, order, False
    return tries, order, True

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    print(f"원소 {len(NAMES)}  레시피 {len(RECS)}  고유 쌍 {len(REC)}")
    r = reach()
    miss = [n for n in NAMES if n not in r]
    print("도달 불가:", miss or "없음")
    per = Counter(r for _, _, r in RECS)
    print("결과별 레시피 수 분포:", dict(sorted(Counter(per.values()).items())))
    used = Counter()
    for a, b, _ in RECS: used[a] += 1; used[b] += 1
    dead = [n for n in NAMES if used[n] == 0]
    print(f"재료로 안 쓰이는 원소 {len(dead)}개:", " ".join(dead))
    top = used.most_common(8)
    print("가장 많이 쓰이는 재료:", ", ".join(f"{n}({c})" for n, c in top))
    # 단계(깊이): 시작 원소에서 몇 번 조합해야 닿는가
    depth = {n: 0 for n in BASE}
    changed = True
    while changed:
        changed = False
        for (a, b), res in REC.items():
            if a in depth and b in depth:
                d = max(depth[a], depth[b]) + 1
                if res not in depth or depth[res] > d:
                    depth[res] = d; changed = True
    deep = sorted(depth.items(), key=lambda x: -x[1])[:10]
    print("가장 깊은 원소:", ", ".join(f"{n}({d})" for n, d in deep))
    print("깊이 분포:", dict(sorted(Counter(depth.values()).items())))

    for mode in ("smart", "random"):
        rng = random.Random(42)
        tries_all = []; last = Counter(); stuck = 0; late_pos = defaultdict(list)
        for g in range(N):
            t, order, ok = play(mode, rng)
            if not ok: stuck += 1; continue
            tries_all.append(t)
            for i, (n, _) in enumerate(order):
                late_pos[n].append(i)
            for n, _ in order[-5:]:
                last[n] += 1
        print(f"\n[{mode}] {N}판  완주 {N-stuck}  시도 평균 {statistics.mean(tries_all):.0f}  중앙값 {statistics.median(tries_all):.0f}  최대 {max(tries_all)}")
        print("  마지막 5개에 자주 남는 원소:", ", ".join(f"{n}({c})" for n, c in last.most_common(12)))
        avgpos = sorted(((statistics.mean(v), n) for n, v in late_pos.items()), reverse=True)[:10]
        print("  평균 발견 순서가 가장 늦은 원소:", ", ".join(f"{n}({p:.0f})" for p, n in avgpos))
