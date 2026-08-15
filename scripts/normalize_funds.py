#!/usr/bin/env python3
"""Builds the normalised dataset: rounds, investments, companies, aliases.

Inverts the index. The scrape produces projects with rounds and investors;
this script turns that into one investment row per combination of fund and
round, but only for the funds in `funds.py`. All other investors in
the same round are kept as co-investors.

Input    data/processed/rounds.json
         data/imported/investment-dashboard-rounds.json
         data/imported/investment-dashboard-vc-research.json
Output   data/processed/dataset.json
"""

import hashlib
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import FUNDS, SLUG_TO_CANONICAL, canonical_for_slug, canonical_for_name  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
IMPORTED = os.path.join(ROOT, "data", "imported")
SOURCE_BASE = "https://crypto-fundraising.info"

# Round types from the source -> investment_type per the allowed categories.
TOKEN_ROUND_TYPES = {"public sale", "ico", "ido", "ieo", "token sale", "launchpad"}
STRATEGIC_ROUND_TYPES = {"strategic", "strategic round"}
INCUBATION_ROUND_TYPES = {"incubation", "incubated"}

# Round types that are not an investment in the sense of the brief.
EXCLUDED_ROUND_TYPES = {"grant", "grants", "airdrop", "treasury diversification"}


def stable_id(*parts):
    raw = "|".join(str(p or "") for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def classify_investment_type(round_type):
    rt = (round_type or "").strip().lower()
    if not rt:
        return "unknown"
    if rt in TOKEN_ROUND_TYPES:
        return "public_sale"
    if rt in STRATEGIC_ROUND_TYPES:
        return "strategic"
    if rt in INCUBATION_ROUND_TYPES:
        return "incubated"
    if "saft" in rt:
        return "SAFT"
    if "token" in rt:
        return "token"
    # Pre-seed, Seed, Series A through F, Private, Extended, Bridge: equity rounds.
    return "equity"


def is_excluded(round_type):
    return (round_type or "").strip().lower() in EXCLUDED_ROUND_TYPES


def verification_status(primary, aggregator, conflict):
    """Determines the verification status from the sources that actually exist.

    The aggregator page always counts. A Details link on it points to the
    original announcement or press release; that counts as a primary source.
    There is no case in which this script itself establishes two independent
    primary sources, so `verified_two_sources` is never assigned here — that
    only happens for manually verified rows.
    """
    if conflict:
        return "conflict"
    if primary and aggregator:
        return "verified_primary"
    if aggregator:
        return "verified_aggregator_only"
    return "single_source"


def confidence_for(status, has_date, has_amount):
    if status == "conflict":
        return "low"
    if status == "verified_primary" and has_date:
        return "high"
    if status == "verified_aggregator_only" and has_date and has_amount:
        return "medium"
    if status == "verified_aggregator_only" and has_date:
        return "medium"
    return "low"


def main():
    with open(os.path.join(PROCESSED, "rounds.json")) as fh:
        scrape = json.load(fh)
    consulted = scrape["collected_at"][:10]

    dashboard_path = os.path.join(IMPORTED, "investment-dashboard-rounds.json")
    dashboard = json.load(open(dashboard_path)) if os.path.exists(dashboard_path) else {"rounds": []}
    research_path = os.path.join(IMPORTED, "investment-dashboard-vc-research.json")
    research = json.load(open(research_path)) if os.path.exists(research_path) else {}

    # Token measurements from the dashboard, keyed by ticker, for token_exists.
    measured_tokens = {}
    for t in ((research.get("token_measurements") or {}).get("tokens") or []):
        if t.get("token_ticker"):
            measured_tokens[t["token_ticker"].upper()] = t

    # Dashboard rows keyed on (fund, project name, month) for the cross-check.
    # Keyed on month, not day. The dashboard only knew month and year, while
    # the scrape delivers exact days via JSON-LD. Matching on the full date
    # would silently disable the cross-check.
    dash_index = {}
    for r in dashboard.get("rounds", []):
        if not r.get("fund_canonical"):
            continue
        month = (r.get("round_date") or "")[:7]
        key = (r["fund_canonical"], r["project_name"].strip().lower(), month)
        dash_index.setdefault(key, []).append(r)

    rounds_out = {}
    investments = []
    projects_out = {}
    conflicts = []
    unknowns = []
    alias_rows = []
    seen_source_names = {}

    for project in scrape["projects"]:
        pslug = project["project_slug"]
        pname = project["project_name"] or project.get("project_url", "")
        ticker = (project.get("token_ticker") or "").strip()
        project_url = "%s/projects/%s/" % (SOURCE_BASE, pslug)

        project_has_selected_fund = False

        for rnd in project["rounds"]:
            round_id = stable_id(pslug, rnd["round_index"], rnd.get("round_date"))
            leads = rnd["leads"]
            participants = rnd["participants"]
            all_investors = leads + participants

            lead_slugs = {x["slug"] for x in leads}
            co_names = [x["name"] for x in all_investors]

            round_type = rnd.get("round_type") or ""
            excluded = is_excluded(round_type)

            rounds_out[round_id] = {
                "round_id": round_id,
                "project_slug": pslug,
                "project_name": pname,
                "round_date": rnd.get("round_date"),
                "date_precision": rnd.get("date_precision"),
                "round_type": round_type,
                "round_size_usd": rnd.get("round_size_usd"),
                "valuation_usd": rnd.get("valuation_usd"),
                "investor_count": len(all_investors),
                "lead_count": len(leads),
                "primary_source_url": rnd.get("details_url") or "",
                "aggregator_source_url": project_url,
                "all_investors": co_names,
                "selected_funds": [],
            }

            for inv in all_investors:
                canonical = canonical_for_slug(inv["slug"])
                if not canonical:
                    continue
                project_has_selected_fund = True

                is_lead = inv["slug"] in lead_slugs
                fund_role = "lead" if is_lead else "participant"
                if is_lead and len(leads) > 1:
                    fund_role = "co-lead"

                investment_id = stable_id(canonical, round_id)
                primary = rnd.get("details_url") or ""
                conflict_flag = False
                notes = []

                if excluded:
                    notes.append(
                        "Round type '%s' falls outside the investment definition in the brief; "
                        "row included for review with status uncertain." % round_type
                    )

                # Cross-check against the previously built dashboard.
                dkey = (canonical, pname.strip().lower(), (rnd.get("round_date") or "")[:7])
                dmatches = dash_index.get(dkey) or []
                for d in dmatches:
                    if d["is_lead"] != is_lead:
                        conflict_flag = True
                        conflicts.append({
                            "investment_id": investment_id,
                            "round_id": round_id,
                            "fund_slug": canonical,
                            "project_name": pname,
                            "field": "is_lead",
                            "value_a": "TRUE" if is_lead else "FALSE",
                            "source_a": project_url,
                            "value_b": "TRUE" if d["is_lead"] else "FALSE",
                            "source_b": "investment-dashboard crypto-vc.html (13 Aug 2026)",
                            "resolution": "Not smoothed over. The current source page was kept "
                                          "for is_lead; the difference stays visible.",
                        })
                    if (d.get("round_size_usd") and rnd.get("round_size_usd")
                            and d["round_size_usd"] != rnd["round_size_usd"]):
                        conflict_flag = True
                        conflicts.append({
                            "investment_id": investment_id,
                            "round_id": round_id,
                            "fund_slug": canonical,
                            "project_name": pname,
                            "field": "round_size_usd",
                            "value_a": rnd["round_size_usd"],
                            "source_a": project_url,
                            "value_b": d["round_size_usd"],
                            "source_b": "investment-dashboard crypto-vc.html (13 Aug 2026)",
                            "resolution": "Not smoothed over. The current source page was kept.",
                        })

                status = verification_status(bool(primary), True, conflict_flag)
                if excluded:
                    status = "uncertain"
                conf = confidence_for(status, bool(rnd.get("round_date")),
                                      bool(rnd.get("round_size_usd")))

                if rnd.get("date_precision") == "month":
                    notes.append("Source gave only month and year; date is set to the first of the month.")
                if not round_type:
                    notes.append("Source did not state a round type.")

                token_meta = measured_tokens.get(ticker.upper()) if ticker else None
                token_exists = bool(ticker)

                others = [x["name"] for x in all_investors if x["slug"] != inv["slug"]]

                investments.append({
                    "investment_id": investment_id,
                    "round_id": round_id,
                    "fund_slug": canonical,
                    "fund_name": FUNDS[canonical]["fund_name"],
                    "fund_name_in_source": inv["name"],
                    "project_slug": pslug,
                    "project_name": pname,
                    "project_name_in_source": pname,
                    "previous_project_name": "",
                    "announcement_date": rnd.get("round_date") if primary else None,
                    "round_date": rnd.get("round_date"),
                    "round_type": round_type,
                    "investment_type": "unknown" if excluded else classify_investment_type(round_type),
                    "fund_role": fund_role,
                    "is_lead": is_lead,
                    "round_size_usd": rnd.get("round_size_usd"),
                    "valuation_usd": rnd.get("valuation_usd"),
                    "valuation_type": "unknown" if rnd.get("valuation_usd") else "",
                    "fund_ticket_usd": None,
                    "currency_original": "USD" if rnd.get("round_size_usd") else "",
                    "amount_original": rnd.get("round_size_usd"),
                    "country": "",
                    "sector": "",
                    "chain_or_ecosystem": "",
                    "token_ticker": ticker,
                    "token_exists": token_exists,
                    "acquisition_or_exit": "",
                    "acquirer": "",
                    "exit_price_usd": None,
                    "primary_source_url": primary,
                    "secondary_source_url": "",
                    "aggregator_source_url": project_url,
                    "source_consulted_date": consulted,
                    "verification_status": status,
                    "confidence": conf,
                    "conflict_flag": conflict_flag,
                    "co_investors": "; ".join(others),
                    "notes": " ".join(notes),
                    "_token_measurement": token_meta,
                })

                rounds_out[round_id]["selected_funds"].append(canonical)
                seen_source_names.setdefault((canonical, inv["name"]), 0)
                seen_source_names[(canonical, inv["name"])] += 1

                if not rnd.get("round_size_usd") or not rnd.get("round_date") or not round_type:
                    unknowns.append({
                        "investment_id": investment_id,
                        "fund_slug": canonical,
                        "project_name": pname,
                        "round_date": rnd.get("round_date"),
                        "missing_fields": ", ".join(
                            f for f, present in [
                                ("round_date", bool(rnd.get("round_date"))),
                                ("round_type", bool(round_type)),
                                ("round_size_usd", bool(rnd.get("round_size_usd"))),
                                ("valuation_usd", bool(rnd.get("valuation_usd"))),
                            ] if not present
                        ),
                        "attempted": "Read the round page and JSON-LD on crypto-fundraising.info; "
                                     "followed the Details link where present.",
                        "source_url": project_url,
                    })

        if project_has_selected_fund:
            projects_out[pslug] = {
                "project_slug": pslug,
                "project_name": pname,
                "token_ticker": ticker,
                "token_exists": bool(ticker),
                "description": (project.get("description") or "")[:400],
                "project_website": project.get("project_website") or "",
                "source_url": project_url,
            }

    # Alias overview
    for canonical, meta in FUNDS.items():
        source_variants = sorted({
            name for (c, name) in seen_source_names if c == canonical
        })
        alias_rows.append({
            "fund_slug": canonical,
            "canonical_name": meta["fund_name"],
            "source_slugs": ", ".join(meta["source_slugs"]),
            "aliases": ", ".join(meta["aliases"]),
            "names_seen_in_source": ", ".join(source_variants),
            "alias_evidence": meta["alias_evidence"],
            "official_portfolio_url": meta["official_portfolio_url"],
            "cryptorank_url": meta["cryptorank_url"],
        })

    # Only keep rounds that contain a selected fund.
    kept_rounds = {rid: r for rid, r in rounds_out.items() if r["selected_funds"]}
    for r in kept_rounds.values():
        r["selected_fund_count"] = len(set(r["selected_funds"]))
        r["selected_funds"] = ", ".join(sorted(set(r["selected_funds"])))
        r["all_investors"] = "; ".join(r["all_investors"])

    dataset = {
        "generated_at": date.today().isoformat(),
        "source_consulted_date": consulted,
        "scrape": {
            "projects_parsed": scrape["projects_parsed"],
            "projects_failed": scrape["projects_failed"],
            "rounds_total_in_source": scrape["rounds_total"],
            "investor_edges_total": scrape["investor_edges_total"],
        },
        "funds": [
            {
                "fund_slug": slug,
                "fund_name": meta["fund_name"],
                "source_slugs": ", ".join(meta["source_slugs"]),
                "official_portfolio_url": meta["official_portfolio_url"],
                "cryptorank_url": meta["cryptorank_url"],
                "aggregator_fund_url": "%s/funds/%s/" % (SOURCE_BASE, meta["source_slugs"][0]),
            }
            for slug, meta in FUNDS.items()
        ],
        "investments": investments,
        "rounds": list(kept_rounds.values()),
        "projects": list(projects_out.values()),
        "conflicts": conflicts,
        "unknowns": unknowns,
        "aliases": alias_rows,
    }

    out = os.path.join(PROCESSED, "dataset.json")
    with open(out, "w") as fh:
        json.dump(dataset, fh, indent=1, ensure_ascii=False)

    print("Written: %s" % out)
    print("  investments %d" % len(investments))
    print("  rounds      %d" % len(kept_rounds))
    print("  companies   %d" % len(projects_out))
    print("  conflicts   %d" % len(conflicts))
    print("  unknown     %d" % len(unknowns))


if __name__ == "__main__":
    main()
