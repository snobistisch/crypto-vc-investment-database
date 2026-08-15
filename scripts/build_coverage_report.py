#!/usr/bin/env python3
"""Genereert research/coverage-report.md uit de dataset.

Elk getal in het rapport komt uit `dataset.json` of `coverage-controls.json`.
Er wordt geen cijfer met de hand ingetypt.
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
    "Volledig binnen de publiek toegankelijke en genoemde bronnen op de peildatum. "
    "Niet-aangekondigde rondes, secundaire transacties, liquide marktposities en "
    "investeerders die in persberichten onder 'others' vallen, blijven structureel "
    "onzichtbaar."
)


def fmt(value):
    return "—" if value in (None, "") else ("{:,}".format(value).replace(",", ".")
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
    add("# Dekkingsrapport")
    add("")
    add("**Peildatum bron:** %s" % ds["source_consulted_date"])
    add("**Rapport gegenereerd:** %s" % date.today().isoformat())
    add("")
    add("> %s" % STATEMENT)
    add("")
    add("Alle cijfers hieronder zijn gegenereerd uit `data/processed/dataset.json` en")
    add("`data/processed/coverage-controls.json`. Er staat bewust geen algemeen")
    add("dekkingspercentage in dit rapport: een percentage veronderstelt een bekende")
    add("noemer, en de noemer is precies wat niet bekend is.")
    add("")

    add("## Wat de scrape heeft doorzocht")
    add("")
    add("| | |")
    add("| --- | ---: |")
    add("| Projectpagina's geparsed | %s |" % fmt(ds["scrape"]["projects_parsed"]))
    add("| Pagina's mislukt | %s |" % fmt(len(ds["scrape"]["projects_failed"])))
    add("| Rondes in de bron | %s |" % fmt(ds["scrape"]["rounds_total_in_source"]))
    add("| Investeerdersrelaties in de bron | %s |" % fmt(ds["scrape"]["investor_edges_total"]))
    add("| Investeringsregels na filtering op de twintig fondsen | %s |" % fmt(len(inv)))
    add("| Unieke rondes met minstens één geselecteerd fonds | %s |" % fmt(len(ds["rounds"])))
    add("| Unieke portefeuillebedrijven | %s |" % fmt(len(ds["projects"])))
    add("")

    add("## Rondes en bedrijven per fonds")
    add("")
    add("| Fonds | Rondes | Unieke bedrijven | Waarvan lead | Actief in |")
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

    add("## Eigen telling naast de controlebronnen")
    add("")
    add("De kolom *fondspagina bron* is een displaylimiet, geen portefeuilletotaal.")
    add("De kolom *CryptoRank* is de eigen telling van CryptoRank uit `__NEXT_DATA__`,")
    add("niet de zichtbare lijst van tien regels.")
    add("")
    add("| Fonds | Eigen bedrijven | Fondspagina bron | Officiële pagina | RootData | CryptoRank | Verschil eigen − CryptoRank |")
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

    add("## Datakwaliteit per fonds")
    add("")
    add("| Fonds | Regels | Met rondegrootte | Met waardering | Met rondetype | Met primaire bron-URL |")
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
    add("## Verificatie en betrouwbaarheid")
    add("")
    add("| Verificatiestatus | Regels |")
    add("| --- | ---: |")
    for k, v in sorted(status_counts.items(), key=lambda kv: -kv[1]):
        add("| %s | %s |" % (k, fmt(v)))
    add("")
    add("| Betrouwbaarheid | Regels |")
    add("| --- | ---: |")
    for k in ("high", "medium", "low"):
        add("| %s | %s |" % (k, fmt(conf_counts.get(k, 0))))
    add("")
    add("`verified_two_sources` komt niet voor. De scripts stellen zelf geen tweede")
    add("onafhankelijke primaire bron vast, en een status die automatisch wordt")
    add("uitgedeeld is geen verificatie.")
    add("")

    add("## Resterende datagaten")
    add("")
    missing = {}
    for u in ds["unknowns"]:
        for field in u["missing_fields"].split(", "):
            if field:
                missing[field] = missing.get(field, 0) + 1
    add("| Ontbrekend veld | Investeringsregels |")
    add("| --- | ---: |")
    for k, v in sorted(missing.items(), key=lambda kv: -kv[1]):
        add("| %s | %s |" % (k, fmt(v)))
    add("")
    add("Structureel leeg, met reden:")
    add("")
    add("- `fund_ticket_usd` — geen enkele gebruikte bron publiceert wat een individueel")
    add("  fonds in een ronde inlegde. De rondegrootte hier overnemen zou een getal")
    add("  opleveren dat er goed uitziet en fout is.")
    add("- `country`, `sector`, `chain_or_ecosystem` — de projectpagina's van de bron")
    add("  voeren geen land-, sector- of ecosysteemtaxonomie. Niet ingevuld op gevoel.")
    add("- `acquisition_or_exit`, `acquirer`, `exit_price_usd` — vereisen een aparte")
    add("  exitdataset; die valt buiten deze opdracht.")
    add("- `secondary_source_url` — vereist handmatige verificatie per regel.")
    add("")
    add("## Bronconflicten")
    add("")
    add("Er staan %s conflictregels op het tabblad `Conflicten`. Ze zijn niet"
        % fmt(len(ds["conflicts"])))
    add("gladgestreken: de actuele bronpagina is in de datavelden aangehouden en de")
    add("afwijkende waarde uit het eerdere dashboardonderzoek blijft ernaast staan.")
    add("")
    add("Geen beleggingsadvies.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("Geschreven: %s" % OUT)


if __name__ == "__main__":
    main()
