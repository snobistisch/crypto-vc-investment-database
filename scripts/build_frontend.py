#!/usr/bin/env python3
"""Builds docs/index.html — the interactive frontend for the research.

Separation of concerns: `frontend/template.html` holds the markup, styling and
behaviour; this script computes a compact payload from the dataset and injects
it at the `__PAYLOAD__` placeholder. No figure in the page is typed by hand —
every number, including the ones in the narrative, is derived here.

The payload is index-compressed: fund names, investor names, project names and
round types are stored once in lookup tables and referenced by integer. Without
that, the repeated co-investor strings alone would roughly triple the page.

Output: docs/index.html (self-contained, no external requests)
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import FUNDS  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
TEMPLATE = os.path.join(ROOT, "frontend", "template.html")
OUT_DIR = os.path.join(ROOT, "docs")
OUT = os.path.join(OUT_DIR, "index.html")

COMPLETENESS_STATEMENT = (
    "Complete within the publicly accessible and named sources as of the "
    "cutoff date. Unannounced rounds, secondary transactions, liquid market "
    "positions, and investors that press releases lump under 'others' remain "
    "structurally invisible."
)


class Interner:
    """Maps repeated strings to integer ids, preserving first-seen order."""

    def __init__(self):
        self.values = []
        self._index = {}

    def add(self, value):
        value = value or ""
        if value not in self._index:
            self._index[value] = len(self.values)
            self.values.append(value)
        return self._index[value]


def build_coinvestment(coinv, fund_index):
    """Reshapes the co-investment analysis for the charts.

    Re-indexes onto the page's own fund order so a chart never has to hold two
    index spaces, and pre-selects the rows each chart draws so the page does no
    ranking of its own.
    """
    remap = {}
    for i, f in enumerate(coinv["funds"]):
        if f["slug"] in fund_index:
            remap[i] = fund_index[f["slug"]]

    def conv(e):
        return {
            "a": remap[e["a"]], "b": remap[e["b"]],
            "shared": e["shared"], "expected": e["expected"],
            "expected_naive": e["expected_naive"],
            "lift": e["lift"], "p_more": e["p_more"], "p_less": e["p_less"],
            "sig_more": e["sig_more"], "sig_less": e["sig_less"],
            "a_rounds": e["a_rounds"], "b_rounds": e["b_rounds"],
            "reason": e.get("reason", ""),
        }

    pairs = [conv(e) for e in coinv["pairs"] if e["a"] in remap and e["b"] in remap]
    scored = [p for p in pairs if p["lift"] is not None]

    # The two charted rankings. Anything with too little expected overlap is
    # excluded from the "apart" side — a low count there carries no signal.
    strongest = sorted([p for p in scored if p["lift"] > 1],
                       key=lambda p: -p["lift"])[:8]
    weakest = sorted([p for p in scored if p["lift"] < 1
                      and p["expected"] >= coinv["method"]["min_expected_for_avoidance"]],
                     key=lambda p: p["lift"])[:8]

    # The methodological exhibit: the biggest raw counts, next to what the
    # permutation null expected of them.
    top_raw = sorted(scored, key=lambda p: -p["shared"])[:12]

    profiles = []
    for p in coinv["profiles"]:
        if p["slug"] not in fund_index:
            continue
        profiles.append({
            "i": fund_index[p["slug"]], "name": p["name"],
            "rounds": p["rounds"], "solo_rounds": p["solo_rounds"],
            "solo_rate": p["solo_rate"], "distinct_partners": p["distinct_partners"],
            "top_partner": p["top_partner"], "top_partner_rounds": p["top_partner_rounds"],
            "median_lift": p["median_lift"],
            "sig_more_count": p["sig_more_count"], "sig_less_count": p["sig_less_count"],
        })

    above = sum(1 for p in scored if p["lift"] > 1)
    top_raw_below = sum(1 for p in top_raw if p["lift"] <= 1)

    # The headline the charts make: ranking pairs by raw count and ranking them
    # by lift do not agree. Computed rather than asserted, so the sentence in
    # the page cannot drift away from the data behind it.
    by_raw = sorted(scored, key=lambda p: -p["shared"])[:10]
    by_lift = sorted(scored, key=lambda p: -p["lift"])[:10]
    keys_raw = {(p["a"], p["b"]) for p in by_raw}
    keys_lift = {(p["a"], p["b"]) for p in by_lift}
    overlap = len(keys_raw & keys_lift)
    raw_lifts = [p["lift"] for p in top_raw]

    return {
        "method": coinv["method"],
        "totals": dict(coinv["totals"], pairs_above_chance=above,
                       top_raw_below_chance=top_raw_below,
                       top_raw_n=len(top_raw),
                       top10_overlap=overlap,
                       top_raw_lift_min=round(min(raw_lifts), 2) if raw_lifts else None,
                       top_raw_lift_max=round(max(raw_lifts), 2) if raw_lifts else None),
        "pairs": pairs,
        "strongest": strongest,
        "weakest": weakest,
        "top_raw": top_raw,
        "profiles": profiles,
    }


def main():
    ds = json.load(open(os.path.join(PROCESSED, "dataset.json")))
    controls_path = os.path.join(PROCESSED, "coverage-controls.json")
    controls = json.load(open(controls_path)) if os.path.exists(controls_path) else {"funds": {}}
    coinv_path = os.path.join(PROCESSED, "coinvestment.json")
    if not os.path.exists(coinv_path):
        sys.exit("coinvestment.json missing — run analyze_coinvestment.py first")
    coinv = json.load(open(coinv_path))

    investments = ds["investments"]
    rounds_by_id = {r["round_id"]: r for r in ds["rounds"]}
    projects_by_slug = {p["project_slug"]: p for p in ds["projects"]}

    fund_slugs = [f["fund_slug"] for f in ds["funds"]]
    fund_index = {slug: i for i, slug in enumerate(fund_slugs)}

    round_types = Interner()
    inv_types = Interner()
    roles = Interner()
    statuses = Interner()
    confidences = Interner()
    investors = Interner()
    projects = Interner()

    project_meta = []

    def project_id(slug):
        idx = projects.add(slug)
        while len(project_meta) <= idx:
            project_meta.append(None)
        if project_meta[idx] is None:
            p = projects_by_slug.get(slug) or {}
            project_meta[idx] = [
                p.get("project_name") or slug,
                p.get("token_ticker") or "",
                p.get("source_url") or "",
            ]
        return idx

    # ---- investment rows -------------------------------------------------
    rows = []
    for r in investments:
        rnd = rounds_by_id.get(r["round_id"]) or {}
        co = [investors.add(n.strip()) for n in (r.get("co_investors") or "").split(";")
              if n.strip()]
        rows.append([
            fund_index[r["fund_slug"]],
            project_id(r["project_slug"]),
            r["round_date"] or "",
            round_types.add(r["round_type"] or ""),
            inv_types.add(r["investment_type"] or ""),
            roles.add(r["fund_role"] or ""),
            1 if r["is_lead"] else 0,
            r["round_size_usd"] or 0,
            r["valuation_usd"] or 0,
            statuses.add(r["verification_status"] or ""),
            confidences.add(r["confidence"] or ""),
            r.get("primary_source_url") or "",
            r.get("aggregator_source_url") or "",
            co,
            rnd.get("investor_count") or 0,
            1 if r.get("conflict_flag") else 0,
            r.get("notes") or "",
        ])

    # ---- per-fund statistics --------------------------------------------
    stats = {}
    for r in investments:
        s = stats.setdefault(r["fund_slug"], {
            "rounds": 0, "companies": set(), "leads": 0, "years": Counter(),
            "types": Counter(), "amounts": [], "with_valuation": 0,
        })
        s["rounds"] += 1
        s["companies"].add(r["project_slug"])
        if r["is_lead"]:
            s["leads"] += 1
        if r["round_date"]:
            s["years"][r["round_date"][:4]] += 1
        s["types"][r["round_type"] or "unstated"] += 1
        if r["round_size_usd"]:
            s["amounts"].append(r["round_size_usd"])
        if r["valuation_usd"]:
            s["with_valuation"] += 1

    def median(values):
        if not values:
            return 0
        v = sorted(values)
        mid = len(v) // 2
        return v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) // 2

    funds_payload = []
    for f in ds["funds"]:
        slug = f["fund_slug"]
        s = stats.get(slug, {"rounds": 0, "companies": set(), "leads": 0,
                             "years": Counter(), "types": Counter(), "amounts": [],
                             "with_valuation": 0})
        ctrl = controls.get("funds", {}).get(slug, {})
        cr = (ctrl.get("cryptorank") or {}).get("investments")
        years = sorted(s["years"])
        funds_payload.append({
            "slug": slug,
            "name": f["fund_name"],
            "rounds": s["rounds"],
            "companies": len(s["companies"]),
            "leads": s["leads"],
            "lead_rate": round(100.0 * s["leads"] / s["rounds"]) if s["rounds"] else 0,
            "first_year": years[0] if years else "",
            "last_year": years[-1] if years else "",
            "by_year": dict(s["years"]),
            "top_types": s["types"].most_common(5),
            "median_round_usd": median(s["amounts"]),
            "with_valuation": s["with_valuation"],
            "cryptorank": cr if isinstance(cr, int) else None,
            "portfolio_url": f["official_portfolio_url"],
            "aggregator_url": f["aggregator_fund_url"],
            "country": (ctrl.get("cryptorank") or {}).get("country") or "",
        })

    # ---- co-investment network ------------------------------------------
    # Only counts rounds where two selected funds actually share the same
    # round. Being in the same cap table is not evidence of a relationship,
    # so the page labels this co-occurrence and nothing more.
    pair_counts = Counter()
    solo_counts = Counter()
    for rnd in ds["rounds"]:
        selected = sorted({s.strip() for s in (rnd.get("selected_funds") or "").split(",")
                           if s.strip()})
        if len(selected) == 1:
            solo_counts[selected[0]] += 1
        for i in range(len(selected)):
            for j in range(i + 1, len(selected)):
                pair_counts[(selected[i], selected[j])] += 1

    pairs = [[fund_index[a], fund_index[b], n]
             for (a, b), n in pair_counts.items() if a in fund_index and b in fund_index]
    pairs.sort(key=lambda p: -p[2])

    # ---- headline figures for the narrative ------------------------------
    total_amount_rounds = {r["round_id"] for r in investments if r["round_size_usd"]}
    disclosed = sum(rounds_by_id[rid]["round_size_usd"] for rid in total_amount_rounds
                    if rounds_by_id.get(rid, {}).get("round_size_usd"))
    lead_total = sum(1 for r in investments if r["is_lead"])
    with_primary = sum(1 for r in investments if r.get("primary_source_url"))
    shared_rounds = sum(1 for r in ds["rounds"] if (r.get("selected_fund_count") or 0) > 1)

    cf_rows = [(controls.get("funds", {}).get(s, {}).get("crypto_fundraising") or {})
               .get("visible_rows") for s in fund_slugs]
    cf_rows = [v for v in cf_rows if isinstance(v, int)]

    payload = {
        "meta": {
            "cutoff": ds["source_consulted_date"],
            "generated": date.today().isoformat(),
            "projects_parsed": ds["scrape"]["projects_parsed"],
            "projects_failed": len(ds["scrape"]["projects_failed"]),
            "rounds_in_source": ds["scrape"]["rounds_total_in_source"],
            "edges_in_source": ds["scrape"]["investor_edges_total"],
            "investments": len(investments),
            "rounds": len(ds["rounds"]),
            "companies": len(ds["projects"]),
            "conflicts": len(ds["conflicts"]),
            "unknowns": len(ds["unknowns"]),
            "lead_total": lead_total,
            "with_primary": with_primary,
            "shared_rounds": shared_rounds,
            "disclosed_usd": disclosed,
            "fund_page_limit_max": max(cf_rows) if cf_rows else None,
            "fund_page_limit_funds": len(cf_rows),
            "completeness": COMPLETENESS_STATEMENT,
        },
        "funds": funds_payload,
        "lookups": {
            "round_types": round_types.values,
            "investment_types": inv_types.values,
            "roles": roles.values,
            "statuses": statuses.values,
            "confidences": confidences.values,
            "investors": investors.values,
            "projects": projects.values,
            "project_meta": project_meta,
        },
        "rows": rows,
        "pairs": pairs,
        "solo": {fund_index[k]: v for k, v in solo_counts.items() if k in fund_index},
        "coinvest": build_coinvestment(coinv, fund_index),
    }

    if not os.path.exists(TEMPLATE):
        sys.exit("template missing: %s" % TEMPLATE)
    html = open(TEMPLATE, encoding="utf-8").read()
    if "__PAYLOAD__" not in html:
        sys.exit("template has no __PAYLOAD__ placeholder")

    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    # The payload sits inside a <script type="application/json"> block, so the
    # only sequence that can break out of it is a literal closing script tag.
    blob = blob.replace("</", "<\\/")
    html = html.replace("__PAYLOAD__", blob)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)

    print("Written: %s" % OUT)
    print("  page %.1f KB, payload %.1f KB" % (len(html) / 1024.0, len(blob) / 1024.0))
    print("  %d investment rows, %d funds, %d co-investment pairs"
          % (len(rows), len(funds_payload), len(pairs)))
    print("  lookup tables: %d investors, %d projects, %d round types"
          % (len(investors.values), len(projects.values), len(round_types.values)))


if __name__ == "__main__":
    main()
