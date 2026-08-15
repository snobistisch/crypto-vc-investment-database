#!/usr/bin/env python3
"""Generates research/coverage-report.md from the dataset.

Every number in the report comes from `dataset.json` or
`coverage-controls.json`. No figure is typed in by hand.
"""

import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import FUNDS  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "research", "coverage-report.md")

STATEMENT = (
    "Complete within the publicly accessible and named sources as of the "
    "cutoff date. Unannounced rounds, secondary transactions, liquid market "
    "positions, and investors that press releases lump under 'others' remain "
    "structurally invisible."
)


def fmt(value):
    return "—" if value in (None, "") else ("{:,}".format(value)
                                            if isinstance(value, int) else str(value))


def main():
    ds = json.load(open(os.path.join(PROCESSED, "dataset.json")))
    controls_path = os.path.join(PROCESSED, "coverage-controls.json")
    controls = json.load(open(controls_path)) if os.path.exists(controls_path) else {"funds": {}}

    inv = ds["investments"]
    per_fund = {}
    for r in inv:
        f = per_fund.setdefault(r["fund_slug"], {
            "rounds": 0, "companies": set(), "leads": 0, "with_amount": 0,
            "with_valuation": 0, "with_primary": 0, "with_type": 0, "years": set(),
        })
        f["rounds"] += 1
        f["companies"].add(r["project_slug"])
        f["leads"] += 1 if r["is_lead"] else 0
        f["with_amount"] += 1 if r["round_size_usd"] else 0
        f["with_valuation"] += 1 if r["valuation_usd"] else 0
        f["with_primary"] += 1 if r["primary_source_url"] else 0
        f["with_type"] += 1 if r["round_type"] else 0
        if r["round_date"]:
            f["years"].add(r["round_date"][:4])

    lines = []
    add = lines.append
    add("# Coverage Report")
    add("")
    add("**Source cutoff date:** %s" % ds["source_consulted_date"])
    add("**Report generated:** %s" % date.today().isoformat())
    add("")
    add("> %s" % STATEMENT)
    add("")
    add("Every figure below is generated from `data/processed/dataset.json` and")
    add("`data/processed/coverage-controls.json`. This report deliberately carries")
    add("no overall coverage percentage: a percentage presupposes a known")
    add("denominator, and the denominator is exactly what is not known.")
    add("")

    add("## What the scrape searched")
    add("")
    add("| | |")
    add("| --- | ---: |")
    add("| Project pages parsed | %s |" % fmt(ds["scrape"]["projects_parsed"]))
    add("| Pages failed | %s |" % fmt(len(ds["scrape"]["projects_failed"])))
    add("| Rounds in the source | %s |" % fmt(ds["scrape"]["rounds_total_in_source"]))
    add("| Investor relations in the source | %s |" % fmt(ds["scrape"]["investor_edges_total"]))
    add("| Investment rows after filtering to the twenty funds | %s |" % fmt(len(inv)))
    add("| Unique rounds with at least one selected fund | %s |" % fmt(len(ds["rounds"])))
    add("| Unique portfolio companies | %s |" % fmt(len(ds["projects"])))
    add("")

    add("## Rounds and companies per fund")
    add("")
    add("| Fund | Rounds | Unique companies | Of which lead | Active | ")
    add("| --- | ---: | ---: | ---: | --- |")
    for slug, meta in sorted(FUNDS.items(), key=lambda kv: -len(
            per_fund.get(kv[0], {"companies": set()})["companies"])):
        f = per_fund.get(slug)
        if not f:
            add("| %s | 0 | 0 | 0 | — |" % meta["fund_name"])
            continue
        years = sorted(f["years"])
        span = "%s–%s" % (years[0], years[-1]) if years else "—"
        add("| %s | %s | %s | %s | %s |" % (
            meta["fund_name"], fmt(f["rounds"]), fmt(len(f["companies"])),
            fmt(f["leads"]), span))
    add("")

    add("## Own count next to the control sources")
    add("")
    add("The *source fund page* column is a display limit, not a portfolio total.")
    add("The *CryptoRank* column is CryptoRank's own count from `__NEXT_DATA__`,")
    add("not the visible list of ten rows.")
    add("")
    add("| Fund | Own companies | Source fund page | Official page | RootData | CryptoRank | Difference own − CryptoRank |")
    add("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for slug, meta in FUNDS.items():
        f = per_fund.get(slug, {"companies": set()})
        c = controls.get("funds", {}).get(slug, {})
        cr = (c.get("cryptorank") or {}).get("investments")
        own = len(f["companies"])
        diff = own - cr if isinstance(cr, int) else None
        add("| %s | %s | %s | %s | %s | %s | %s |" % (
            meta["fund_name"], fmt(own),
            fmt((c.get("crypto_fundraising") or {}).get("visible_rows")),
            fmt((c.get("official_portfolio") or {}).get("names_found")),
            fmt((c.get("rootdata") or {}).get("investments")),
            fmt(cr),
            ("+%d" % diff if isinstance(diff, int) and diff > 0 else fmt(diff))))
    add("")

    add("## Data quality per fund")
    add("")
    add("| Fund | Rows | With round size | With valuation | With round type | With primary source URL |")
    add("| --- | ---: | ---: | ---: | ---: | ---: |")
    for slug, meta in FUNDS.items():
        f = per_fund.get(slug)
        if not f:
            add("| %s | 0 | — | — | — | — |" % meta["fund_name"])
            continue
        n = f["rounds"]
        def pct(x):
            return "%d (%d%%)" % (x, round(100.0 * x / n)) if n else "—"
        add("| %s | %s | %s | %s | %s | %s |" % (
            meta["fund_name"], fmt(n), pct(f["with_amount"]), pct(f["with_valuation"]),
            pct(f["with_type"]), pct(f["with_primary"])))
    add("")

    status_counts = {}
    conf_counts = {}
    for r in inv:
        status_counts[r["verification_status"]] = status_counts.get(r["verification_status"], 0) + 1
        conf_counts[r["confidence"]] = conf_counts.get(r["confidence"], 0) + 1
    add("## Verification and confidence")
    add("")
    add("| Verification status | Rows |")
    add("| --- | ---: |")
    for k, v in sorted(status_counts.items(), key=lambda kv: -kv[1]):
        add("| %s | %s |" % (k, fmt(v)))
    add("")
    add("| Confidence | Rows |")
    add("| --- | ---: |")
    for k in ("high", "medium", "low"):
        add("| %s | %s |" % (k, fmt(conf_counts.get(k, 0))))
    add("")
    add("`verified_two_sources` does not occur. The scripts do not themselves")
    add("establish a second independent primary source, and a status handed out")
    add("automatically is not verification.")
    add("")

    add("## Remaining data gaps")
    add("")
    missing = {}
    for u in ds["unknowns"]:
        for field in u["missing_fields"].split(", "):
            if field:
                missing[field] = missing.get(field, 0) + 1
    add("| Missing field | Investment rows |")
    add("| --- | ---: |")
    for k, v in sorted(missing.items(), key=lambda kv: -kv[1]):
        add("| %s | %s |" % (k, fmt(v)))
    add("")
    add("Structurally blank, with the reason:")
    add("")
    add("- `fund_ticket_usd` — no source used publishes what an individual fund put")
    add("  into a round. Copying the round size here would produce a number that")
    add("  looks right and is wrong.")
    add("- `country`, `sector`, `chain_or_ecosystem` — the source's project pages")
    add("  carry no country, sector, or ecosystem taxonomy. Not filled in by feel.")
    add("- `acquisition_or_exit`, `acquirer`, `exit_price_usd` — require a separate")
    add("  exit dataset; that falls outside this brief.")
    add("- `secondary_source_url` — requires manual verification per row.")
    add("")
    add("## Cross-check against the earlier dashboard research")
    add("")
    dash_path = os.path.join(ROOT, "data", "imported", "investment-dashboard-rounds.json")
    if os.path.exists(dash_path):
        dash = json.load(open(dash_path))["rounds"]
        keys = {(r["fund_slug"], r["project_name"].strip().lower(),
                 (r["round_date"] or "")[:7]) for r in inv}
        usable = [d for d in dash if d.get("fund_canonical")]
        matched = [d for d in usable
                   if (d["fund_canonical"], d["project_name"].strip().lower(),
                       (d.get("round_date") or "")[:7]) in keys]
        add("| | |")
        add("| --- | ---: |")
        add("| Fund-round pairs from the dashboard (13 Aug 2026) | %s |" % fmt(len(dash)))
        add("| Of which found again in this dataset | %s |" % fmt(len(matched)))
        add("| Not found again | %s |" % fmt(len(usable) - len(matched)))
        add("")
        add("The rows not found again were not silently dropped and not carried over")
        add("as confirmed. They do not match on the combination of fund, project name")
        add("and month. Plausible causes, not investigated row by row: the project was")
        add("renamed at the source, the round was updated since 13 August 2026, or the")
        add("month differs between announcement and registration. Carrying them over")
        add("without that check would add rows to the dataset that the current source")
        add("does not confirm.")
        add("")
    add("## Source conflicts")
    add("")
    n_conf = len(ds["conflicts"])
    add("The `Conflicts` sheet contains %s %s. %s not smoothed over: the current"
        % (fmt(n_conf), "conflict row" if n_conf == 1 else "conflict rows",
           "It is" if n_conf == 1 else "They are"))
    add("source page was kept in the data fields, and the deviating value from the")
    add("earlier dashboard research stays next to it.")
    add("")
    add("Not investment advice.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("Written: %s" % OUT)


if __name__ == "__main__":
    main()
