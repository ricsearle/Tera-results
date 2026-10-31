"""Generate results.md and results.html from race data. Scoring: RRS Appendix A low point, no discards."""
from html import escape

VENUE = "Netley Sailing Club"
DATE = "Saturday 31 October 2026"
HELMS = {"3403": "Rupert", "228": "Daniel", "1991": "Freddie M", "2584": "Kiera",
         "2392": "Penny", "2166": "Cammy", "4600": "Freddie P"}
CLASSES = {"Tera Sport": ["3403", "228", "1991", "2584", "2392", "2166"], "Tera Pro": ["4600"]}
# Finishing order as reported (all classes mixed). "NNNN CODE" for penalty codes.
RACES = [
    "4600, 3403, 228, 1991, 2584, 2392, 2166",
    "3403, 4600, 1991, 228, 2584, 2166, 2392 OCS",
    "4600, 3403, 2584, 2166, 228, 1991, 2392",
    "4600, 3403, 2392, 228, 2584, 2166, 1991",
    "3403, 4600, 228, 2166, 2584, 2392, 1991",
]

def score_class(boats):
    n = len(boats)
    per_race = []  # list of {sail: (points, code)}
    orders = []
    for race in RACES:
        res, order, pos = {}, [], 0
        for tok in [t.strip() for t in race.split(",")]:
            parts = tok.split()
            sail, code = parts[0], (parts[1].upper() if len(parts) > 1 else None)
            if sail not in boats:
                continue
            if code:
                res[sail] = (n + 1, code)
            else:
                pos += 1
                res[sail] = (pos, None)
            order.append(sail)
        for b in boats:
            if b not in res:
                res[b] = (n + 1, "DNC"); order.append(b)
        per_race.append(res)
        orders.append(order)
    rows = []
    for b in boats:
        pts = [r[b][0] for r in per_race]
        rows.append({"sail": b, "helm": HELMS.get(b, "?"), "res": [r[b] for r in per_race],
                     "total": sum(pts), "key": (sum(pts), sorted(pts), [-0] + [p for p in reversed(pts)])})
    # A8.1: sorted scores best-first; A8.2: last race backwards
    rows.sort(key=lambda r: (r["total"], sorted(p for p, _ in r["res"]), [p for p, _ in reversed(r["res"])]))
    for i, r in enumerate(rows, 1):
        r["pos"] = i
    return rows, per_race, orders

def html():
    nr = len(RACES)
    rw = f"{60 / nr:.1f}%"
    out = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Tera Results — {VENUE}</title>',
           f'<style>{open("style.css").read()} :root{{--rw:{rw}}}</style></head><body>',
           f'<header><div class="club">{VENUE}</div><h1>Tera Racing — Results</h1>',
           f'<div class="meta">{DATE} &nbsp;·&nbsp; {nr} races sailed</div>',
           '<svg width="170" height="120" viewBox="0 0 170 120" fill="#fff"><path d="M90 5 L90 95 L30 95 Z"/><path d="M96 20 L96 95 L140 95 Z"/><path d="M15 102 H160 L145 115 H30 Z"/></svg></header>']
    medal = {1: "g", 2: "s", 3: "b"}
    results = {}
    for cls, boats in CLASSES.items():
        rows, per_race, orders = score_class(boats)
        results[cls] = (rows, orders)
        out.append(f'<h2>{cls} <span class="tag">{len(boats)} BOAT{"S" if len(boats) > 1 else ""}</span></h2><p class="sub">Overall standings</p>')
        out.append('<table><thead><tr><th>Pos</th><th>Sail No.</th><th class="l">Helm</th>'
                   + "".join(f'<th class="r">R{i+1}</th>' for i in range(nr)) + '<th>Total</th></tr></thead><tbody>')
        for r in rows:
            pos = f'<span class="medal {medal[r["pos"]]}">{r["pos"]}</span>' if r["pos"] in medal else r["pos"]
            cells = ""
            for p, c in r["res"]:
                if c: cells += f'<td>{p}<span class="code">{c}</span></td>'
                elif p == 1: cells += '<td class="win">1</td>'
                else: cells += f'<td>{p}</td>'
            out.append(f'<tr><td class="pos">{pos}</td><td>{r["sail"]}</td><td class="l helm">{escape(r["helm"])}</td>{cells}<td class="total">{r["total"]}</td></tr>')
        out.append('</tbody></table>')
    # race-by-race grid for Tera Sport
    rows, orders = results["Tera Sport"]
    _, per_race, _ = score_class(CLASSES["Tera Sport"])
    out.append('<h2>Race by Race <span class="tag">TERA SPORT</span></h2><p class="sub">Finishing order in each race</p>')
    out.append('<table class="grid"><thead><tr>' + "".join(f'<th class="l">Race {i+1}</th>' for i in range(nr)) + '</tr></thead><tbody>')
    for i in range(len(CLASSES["Tera Sport"])):
        cells = ""
        for ri, order in enumerate(orders):
            sail = order[i]; p, c = per_race[ri][sail]
            lab = f'<span class="rp ocs">{c}</span>' if c else f'<span class="rp">{p}</span>'
            cells += f'<td class="l">{lab} {escape(HELMS[sail])} <span class="sn">{sail}</span></td>'
        out.append(f'<tr>{cells}</tr>')
    out.append('</tbody></table>')
    pro = results["Tera Pro"][0][0]
    if all(p == 1 for p, _ in pro["res"]):
        out.append(f'<p class="sub" style="margin-top:6px">Tera Pro: {pro["sail"]} {pro["helm"]} finished 1st in every race.</p>')
    out.append('<div class="notes"><p><strong>Scoring:</strong> RRS Appendix A Low Point System. No discards. '
               'OCS / DNF / DNS / DNC scored as number of entries + 1. Ties broken under A8.</p></div>')
    out.append(f'<footer><span>{VENUE} · Tera Racing</span><span>Provisional results — subject to protests</span></footer></body></html>')
    return "\n".join(out)

def md():
    nr = len(RACES)
    out = [f"# {VENUE} — Tera Race Results, {DATE}", "",
           "Scoring: RRS Appendix A Low Point. DNF/DNS/DNC/OCS/DSQ = entries + 1. No discards. 2136 (Rosy) not competing.", ""]
    for cls, boats in CLASSES.items():
        rows, _, orders = score_class(boats)
        out += [f"## {cls} (after {nr} races)", "",
                "| Pos | Sail No. | Helm | " + " | ".join(f"R{i+1}" for i in range(nr)) + " | Total |",
                "|---:|---:|---|" + "---:|" * nr + "---:|"]
        for r in rows:
            cells = " | ".join(f"{p} ({c})" if c else str(p) for p, c in r["res"])
            out.append(f'| {r["pos"]} | {r["sail"]} | {r["helm"]} | {cells} | {r["total"]} |')
        out.append("")
    out += ["## Finishing orders as recorded (all classes)", ""] + [f"- **Race {i+1}:** {r}" for i, r in enumerate(RACES)]
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    open("results.html", "w").write(html())
    open("results.md", "w").write(md())
