# -*- coding: utf-8 -*-
"""author.py 의 데이터를 index.html 의 ELEMENT_DATA / RECIPE_DATA 에 끼워 넣는다.
실행: python3 -I build.py   (이 폴더에서)
이후로는 index.html 이 유일한 원본이다. author.py 는 초안 작성용."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import author

els, recs = author.parse()
errs, _, _ = author.validate(els, recs)
if errs:
    for e in errs: print("!!", e)
    sys.exit(1)

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
s = open(html_path, encoding="utf-8").read()

def js_arr(lines, indent="    "):
    return ",\n".join(indent + '"' + l + '"' for l in lines)

el_lines = ["|".join(e) for e in els]
# 레시피는 결과별로 묶어 한 줄에 여러 개 (읽기 쉽게)
from collections import OrderedDict
by_r = OrderedDict()
for a, b, r in recs:
    by_r.setdefault(r, []).append(f"{a}+{b}={r}")
rec_lines = []
cat_of = {e[0]: e[2] for e in els}
last_cat = None
for r, items in by_r.items():
    c = cat_of[r]
    if c != last_cat:
        rec_lines.append("    // " + author.CATNAMES[c])
        last_cat = c
    rec_lines.append("    " + ", ".join('"' + x + '"' for x in items))

new_el = "var ELEMENT_DATA = [\n" + js_arr(el_lines) + "\n  ];"
new_rec = "var RECIPE_DATA = [\n" + ",\n".join(rec_lines) + "\n  ];"

s, n1 = re.subn(r"var ELEMENT_DATA = \[.*?\n  \];", lambda m: new_el, s, count=1, flags=re.S)
s, n2 = re.subn(r"var RECIPE_DATA = \[.*?\n  \];", lambda m: new_rec, s, count=1, flags=re.S)
assert n1 == 1 and n2 == 1, (n1, n2)
open(html_path, "w", encoding="utf-8").write(s)
print("원소", len(els), "레시피", len(recs), "→ index.html 갱신")
