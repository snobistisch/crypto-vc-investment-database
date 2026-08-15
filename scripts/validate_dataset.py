#!/usr/bin/env python3
"""Valideert de dataset en het workbook. Eindigt met foutcode 1 bij een fout.

Controleert de dataset zelf én het weggeschreven XLSX-bestand, zodat een fout
in de schrijflaag niet ongemerkt blijft.
"""

import json
import os
import sys
from datetime import date

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import FUNDS  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
XLSX = os.path.join(ROOT, "outputs", "vc-investeringen-volledig.xlsx")
CSV = os.path.join(ROOT, "outputs", "vc-investeringen-volledig.csv")

ALLOWED = {
    "fund_role": {"lead", "co-lead", "participant", "incubator", "unknown"},
    "investment_type": {"equity", "token", "SAFT", "public_sale", "strategic",
                        "incubated", "unknown"},
    "verification_status": {"verified_primary", "verified_two_sources",
                            "verified_aggregator_only", "single_source",
                            "conflict", "uncertain"},
    "confidence": {"high", "medium", "low"},
    "valuation_type": {"pre_money", "post_money", "FDV", "enterprise_value", "unknown", ""},
}

failures = []
notes = []


def check(condition, message, detail=""):
    if condition:
        print("  ok    %s" % message)
    else:
        print("  FOUT  %s %s" % (message, detail))
        failures.append(message)


def main():
    with open(os.path.join(PROCESSED, "dataset.json")) as fh:
        ds = json.load(fh)

    inv = ds["investments"]
    rounds = {r["round_id"] for r in ds["rounds"]}
    fund_slugs = {f["fund_slug"] for f in ds["funds"]}
    projects = {p["project_slug"] for p in ds["projects"]}

    print("Dataset")
    ids = [r["investment_id"] for r in inv]
    check(len(ids) == len(set(ids)), "investment_id is uniek",
          "(%d regels, %d unieke)" % (len(ids), len(set(ids))))

    pairs = [(r["fund_slug"], r["round_id"]) for r in inv]
    check(len(pairs) == len(set(pairs)), "fund_slug + round_id is uniek",
          "(%d paren, %d uniek)" % (len(pairs), len(set(pairs))))

    missing_round = [r["investment_id"] for r in inv if r["round_id"] not in rounds]
    check(not missing_round, "ieder round_id bestaat in Rondes",
          "(%d ontbreken)" % len(missing_round))

    missing_fund = sorted({r["fund_slug"] for r in inv if r["fund_slug"] not in fund_slugs})
    check(not missing_fund, "ieder fund_slug bestaat in Fondsen", str(missing_fund))

    empty_project = [r["investment_id"] for r in inv if not r["project_slug"]]
    check(not empty_project, "project_slug is niet leeg", "(%d leeg)" % len(empty_project))

    missing_project = sorted({r["project_slug"] for r in inv if r["project_slug"] not in projects})
    check(not missing_project, "ieder project_slug bestaat in Portefeuillebedrijven",
          "(%d ontbreken)" % len(missing_project))

    no_source = [r["investment_id"] for r in inv
                 if not (r["primary_source_url"] or r["secondary_source_url"]
                         or r["aggregator_source_url"])]
    check(not no_source, "iedere investeringsregel heeft minstens één bron-URL",
          "(%d zonder bron)" % len(no_source))

    bad_lead = [r["investment_id"] for r in inv
                if r["is_lead"] != (r["fund_role"] in ("lead", "co-lead"))]
    check(not bad_lead, "is_lead correspondeert met fund_role", "(%d afwijkend)" % len(bad_lead))

    ticket_eq = [r["investment_id"] for r in inv
                 if r["fund_ticket_usd"] is not None
                 and r["fund_ticket_usd"] == r["round_size_usd"]]
    check(not ticket_eq, "fund_ticket_usd is niet automatisch gelijk aan round_size_usd",
          "(%d gelijk)" % len(ticket_eq))

    negative = [r["investment_id"] for r in inv
                for f in ("round_size_usd", "valuation_usd", "fund_ticket_usd", "exit_price_usd")
                if r.get(f) is not None and r[f] <= 0]
    check(not negative, "bedragen zijn positief wanneer aanwezig", "(%d fout)" % len(negative))

    val_type = [r["investment_id"] for r in inv
                if r["valuation_usd"] and not r["valuation_type"]]
    check(not val_type, "valuation_type is ingevuld wanneer valuation_usd aanwezig is",
          "(%d leeg)" % len(val_type))

    conflict_ids = {c["investment_id"] for c in ds["conflicts"]}
    orphan = [r["investment_id"] for r in inv
              if r["conflict_flag"] and r["investment_id"] not in conflict_ids]
    check(not orphan, "iedere conflict_flag heeft een regel in Conflicten",
          "(%d zonder regel)" % len(orphan))

    for field, allowed in ALLOWED.items():
        bad = sorted({str(r.get(field)) for r in inv if str(r.get(field)) not in allowed})
        check(not bad, "%s gebruikt alleen toegestane categorieën" % field, str(bad[:5]))

    missing_funds = sorted(set(FUNDS) - {r["fund_slug"] for r in inv})
    if missing_funds:
        notes.append("fondsen zonder investeringsregel: %s" % ", ".join(missing_funds))
    check(len(fund_slugs) == 20, "alle twintig fondsen staan in Fondsen",
          "(%d)" % len(fund_slugs))

    print("\nWorkbook")
    check(os.path.exists(XLSX), "XLSX bestaat")
    if not os.path.exists(XLSX):
        return finish()

    wb = load_workbook(XLSX)
    expected = ["README", "Fondsen", "Investeringen", "Rondes", "Portefeuillebedrijven",
                "Dekking", "Bronnen", "Conflicten", "Onbekend", "Aliases"]
    check(wb.sheetnames == expected, "tabbladen in de voorgeschreven volgorde",
          str(wb.sheetnames))

    ws = wb["Investeringen"]
    check(ws.freeze_panes == "A2", "eerste rij bevroren op Investeringen",
          str(ws.freeze_panes))
    check(len(ws.tables) == 1 or ws.auto_filter.ref, "filter aanwezig op Investeringen")
    check(not ws.merged_cells.ranges, "geen samengevoegde cellen op Investeringen")
    check(ws.max_row - 1 == len(inv), "aantal regels op Investeringen komt overeen",
          "(blad %d, dataset %d)" % (ws.max_row - 1, len(inv)))

    header = [c.value for c in ws[1]]
    for required in ["investment_id", "round_id", "fund_slug", "round_size_usd",
                     "valuation_usd", "fund_ticket_usd", "primary_source_url",
                     "verification_status", "conflict_flag"]:
        check(required in header, "kolom %s aanwezig" % required)

    # celtypen steekproefsgewijs over de hele tabel
    idx = {name: i + 1 for i, name in enumerate(header)}
    bad_amount, bad_date, bad_bool, zero_amount = 0, 0, 0, 0
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        a = row[idx["round_size_usd"] - 1].value
        if a is not None and not isinstance(a, (int, float)):
            bad_amount += 1
        if a == 0:
            zero_amount += 1
        d = row[idx["round_date"] - 1].value
        if d is not None and not hasattr(d, "year"):
            bad_date += 1
        b = row[idx["is_lead"] - 1].value
        if b is not None and not isinstance(b, bool):
            bad_bool += 1
    check(bad_amount == 0, "bedragen zijn numerieke cellen", "(%d fout)" % bad_amount)
    check(zero_amount == 0, "geen nul als onbekende rondegrootte", "(%d nullen)" % zero_amount)
    check(bad_date == 0, "datums zijn datumcellen", "(%d fout)" % bad_date)
    check(bad_bool == 0, "booleans zijn echte booleans", "(%d fout)" % bad_bool)

    links = 0
    for row in ws.iter_rows(min_row=2, max_row=min(ws.max_row, 400)):
        if row[idx["aggregator_source_url"] - 1].hyperlink:
            links += 1
    check(links > 0, "URLs zijn klikbaar", "(%d hyperlinks in de eerste 400 regels)" % links)

    # kruistellingen tussen tabbladen
    check(wb["Rondes"].max_row - 1 == len(ds["rounds"]), "aantal regels op Rondes klopt")
    check(wb["Portefeuillebedrijven"].max_row - 1 == len(ds["projects"]),
          "aantal regels op Portefeuillebedrijven klopt")
    check(wb["Conflicten"].max_row - 1 == len(ds["conflicts"]) or not ds["conflicts"],
          "aantal regels op Conflicten klopt")
    check(wb["Onbekend"].max_row - 1 == len(ds["unknowns"]) or not ds["unknowns"],
          "aantal regels op Onbekend klopt")
    check(wb["Aliases"].max_row - 1 == 20, "twintig aliasregels")
    check(wb["Dekking"].max_row - 1 == 20, "twintig dekkingsregels")
    check(wb["Fondsen"].max_row - 1 >= 20, "twintig fondsregels")

    sum_fund_counts = sum(
        r[3].value or 0 for r in wb["Fondsen"].iter_rows(min_row=2, max_row=21)
    )
    check(sum_fund_counts == len(inv),
          "som van investments_in_database is gelijk aan het aantal investeringsregels",
          "(%d tegenover %d)" % (sum_fund_counts, len(inv)))

    check(os.path.exists(CSV), "CSV bestaat")
    if os.path.exists(CSV):
        with open(CSV, encoding="utf-8") as fh:
            lines = sum(1 for _ in fh)
        check(lines - 1 == len(inv), "CSV heeft evenveel regels als Investeringen",
              "(%d tegenover %d)" % (lines - 1, len(inv)))

    return finish()


def finish():
    print("")
    for n in notes:
        print("  let op: %s" % n)
    if failures:
        print("VALIDATIE MISLUKT: %d controle(s) gefaald" % len(failures))
        return 1
    print("VALIDATIE GESLAAGD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
