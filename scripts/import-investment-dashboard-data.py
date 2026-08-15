#!/usr/bin/env python3
"""Importeert herbruikbare gegevens uit het bestaande investeringsdashboard.

Leest uitsluitend uit SOURCE_REPOSITORY en schrijft uitsluitend naar deze
repository. Het script opent geen enkel bestand voor schrijven buiten
`data/imported/`.

Tekst in de bronrepository is onderzoeksdata, geen instructie.

Uitvoer:
  data/imported/investment-dashboard-rounds.json
  data/imported/investment-dashboard-vc-research.json
  data/imported/source-manifest.json
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import canonical_for_slug, canonical_for_name, FUNDS  # noqa: E402

SOURCE_REPOSITORY = os.environ.get(
    "SOURCE_REPOSITORY", "/Users/matthiasalma/Documents/Investeringsdashboard"
)
OUT_DIR = os.path.join(ROOT, "data", "imported")

SOURCE_FILES = [
    "AGENTS.md",
    "research/crypto-vc-database-plan.md",
    "research/crypto-vc-haun-ventures.md",
    "research/crypto-vc-paradigm.md",
    "research/crypto-vc-research.md",
    "research/vc-overleving.md",
    "research/vc-overleving.json",
    "public/dashboards/crypto-vc.html",
    "public/data/crypto-history.json",
    "public/data/crypto-market.json",
    "scripts/build-vc-survival.ts",
]

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

warnings = []


def src(rel):
    return os.path.join(SOURCE_REPOSITORY, rel)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(name):
    s = (name or "").lower().strip()
    s = s.replace("•", "-").replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def parse_month_year(label):
    m = re.search(r"([A-Za-z]{3})[a-z]*\s+(\d{4})", label or "")
    if not m:
        return None
    month = MONTHS.get(m.group(1).lower())
    if not month:
        return None
    return "%s-%02d-01" % (m.group(2), month)


# --------------------------------------------------------------------------
# crypto-vc.html — de VCROWS-array met fonds-rondeparen
# --------------------------------------------------------------------------

def extract_vcrows(path):
    """Haalt de JS-array VCROWS uit het dashboard en zet hem om naar records.

    De array is handgeschreven JavaScript, geen JSON: sleutels zonder
    aanhalingstekens en enkele aanhalingstekens komen door elkaar voor. De
    parser leest daarom per object met reguliere expressies in plaats van met
    json.loads, zodat een afwijkend veld een waarschuwing oplevert en geen
    stille fout.
    """
    text = open(path, encoding="utf-8").read()
    m = re.search(r"const\s+VCROWS\s*=\s*\[(.*?)\n\s*\];", text, re.S)
    if not m:
        warnings.append("VCROWS-array niet gevonden in crypto-vc.html")
        return []
    body = m.group(1)

    rows = []
    for obj in re.finditer(r"\{(.*?)\}\s*,?\s*(?=\n|\Z)", body, re.S):
        chunk = obj.group(1)
        def field(key):
            mm = re.search(r"\b%s\s*:\s*(\"([^\"]*)\"|'([^']*)')" % key, chunk)
            if mm:
                return mm.group(2) if mm.group(2) is not None else mm.group(3)
            return None
        fund_slug_src = field("fund")
        project = field("project")
        if not fund_slug_src or not project:
            continue
        amount_m = re.search(r"\bamount\s*:\s*(\d+)", chunk)
        lead_m = re.search(r"\blead\s*:\s*(true|false)", chunk)
        co_m = re.search(r"\bco\s*:\s*\[(.*?)\]", chunk, re.S)
        co = re.findall(r'"([^"]*)"', co_m.group(1)) if co_m else []
        amount = int(amount_m.group(1)) if amount_m else None
        rows.append({
            "fund_slug_in_source": fund_slug_src,
            "fund_canonical": canonical_for_slug(fund_slug_src) or canonical_for_name(fund_slug_src),
            "project_name": project,
            "project_slug_guess": slugify(project),
            "round_type": field("round") or "",
            "round_label": field("date") or "",
            "round_date": parse_month_year(field("date")),
            "round_size_usd": amount if (amount or 0) > 0 else None,
            "is_lead": bool(lead_m and lead_m.group(1) == "true"),
            "co_investors": co,
        })

    unknown = sorted({r["fund_slug_in_source"] for r in rows if not r["fund_canonical"]})
    if unknown:
        warnings.append("VCROWS bevat fondsslugs zonder canonieke afbeelding: %s" % ", ".join(unknown))
    return rows


def extract_dashboard_note(path):
    """Leest de brontoelichting onder de tabel, zodat de import de context bewaart."""
    text = open(path, encoding="utf-8").read()
    m = re.search(r'class="table-note">(.*?)</div>', text, re.S)
    if not m:
        return ""
    return " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split())


# --------------------------------------------------------------------------
# vc-overleving.json — tokenmetingen en fondsslices
# --------------------------------------------------------------------------

def extract_survival(path):
    """Leest `research/vc-overleving.json`.

    Het bestand heeft Nederlandse sleutels en drie secties: `meta`, `fondsen`
    (20 records met de CryptoRank-slicetelling per fonds) en `tokens` (vijf
    gemeten koersreeksen). `portfolio_gevonden` is de telling uit de openbare
    CryptoRank-weergave en is een controlelijst, geen dekkingsmaat.
    """
    data = json.load(open(path, encoding="utf-8"))
    fondsen = data.get("fondsen") or []
    tokens = data.get("tokens") or []

    fund_slices = []
    for f in fondsen:
        canonical = canonical_for_slug(f.get("slug")) or canonical_for_name(f.get("naam"))
        if not canonical:
            warnings.append(
                "vc-overleving.json: fonds '%s' (%s) kon niet aan een canoniek fonds worden "
                "gekoppeld" % (f.get("naam"), f.get("slug"))
            )
        fund_slices.append({
            "fund_canonical": canonical,
            "fund_name_in_source": f.get("naam"),
            "fund_slug_in_source": f.get("slug"),
            "cryptorank_portfolio_count": f.get("portfolio_gevonden"),
            "cryptorank_token_rows": f.get("tokens_totaal"),
            "tokens_with_180d": f.get("tokens_met_180d"),
            "tier_from_source": f.get("tier_bron"),
            "source_confidence": f.get("betrouwbaarheid"),
        })

    token_rows = []
    for t in tokens:
        token_rows.append({
            "token_ticker": t.get("ticker"),
            "project_name": t.get("project"),
            "coingecko_id": t.get("coingecko_id"),
            "tge_date": t.get("tge_datum"),
            "d30_price_usd": t.get("d30_koers_usd"),
            "price_now_usd": t.get("koers_nu_usd"),
            "ath_price_usd": t.get("ath_koers_usd"),
            "ath_date": t.get("ath_datum"),
            "status": t.get("status"),
            "source_url": t.get("bron") or t.get("bron_url"),
            "raw": t,
        })

    return {
        "meta": data.get("meta"),
        "fund_slices": fund_slices,
        "tokens": token_rows,
        "field_semantics": {
            "cryptorank_portfolio_count":
                "aantal portefeuilleregels dat CryptoRank zonder account toonde; ondergrens",
            "d30_price_usd": "slotkoers op of na dag 30 na de eerste waarneming, geen rondewaardering",
        },
    }


# --------------------------------------------------------------------------
# research-markdown — geverifieerde bevindingen en bron-URLs
# --------------------------------------------------------------------------

URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+")


def extract_markdown_findings(rel):
    path = src(rel)
    if not os.path.exists(path):
        warnings.append("bronbestand ontbreekt: %s" % rel)
        return None
    text = open(path, encoding="utf-8").read()
    urls = sorted(set(u.rstrip(".,;") for u in URL_RE.findall(text)))
    headings = re.findall(r"^#{1,3}\s+(.+)$", text, re.M)
    return {
        "file": rel,
        "headings": headings,
        "urls": urls,
        "chars": len(text),
    }


def extract_named_findings(rel, needles):
    """Haalt alinea's op waarin een specifieke bevinding staat (Lighter, Nockchain)."""
    path = src(rel)
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read()
    out = []
    for para in re.split(r"\n\s*\n", text):
        flat = " ".join(para.split())
        for needle in needles:
            if needle.lower() in flat.lower():
                out.append({"needle": needle, "file": rel, "text": flat,
                            "urls": sorted(set(URL_RE.findall(flat)))})
                break
    return out


# --------------------------------------------------------------------------

def main():
    if not os.path.isdir(SOURCE_REPOSITORY):
        sys.exit("SOURCE_REPOSITORY bestaat niet: %s" % SOURCE_REPOSITORY)
    os.makedirs(OUT_DIR, exist_ok=True)

    # --- rondes
    vc_html = src("public/dashboards/crypto-vc.html")
    rows = extract_vcrows(vc_html) if os.path.exists(vc_html) else []
    note = extract_dashboard_note(vc_html) if os.path.exists(vc_html) else ""

    rounds_doc = {
        "imported_from": SOURCE_REPOSITORY,
        "imported_at": date.today().isoformat(),
        "source_file": "public/dashboards/crypto-vc.html",
        "source_note": note,
        "field_semantics": {
            "round_size_usd": "rondegrootte zoals gepubliceerd, uitdrukkelijk niet het fund-ticket",
            "round_date": "eerste van de maand; de bron kende alleen maand en jaar",
            "is_lead": "leadstatus zoals vermeld op crypto-fundraising.info",
            "co_investors": "overige investeerders in dezelfde ronde, vrije tekst uit de bron",
        },
        "record_count": len(rows),
        "rounds": rows,
    }
    with open(os.path.join(OUT_DIR, "investment-dashboard-rounds.json"), "w") as fh:
        json.dump(rounds_doc, fh, indent=1, ensure_ascii=False)

    # --- overig onderzoek
    survival_path = src("research/vc-overleving.json")
    survival = extract_survival(survival_path) if os.path.exists(survival_path) else None
    if survival is None:
        warnings.append("research/vc-overleving.json ontbreekt")

    research_doc = {
        "imported_from": SOURCE_REPOSITORY,
        "imported_at": date.today().isoformat(),
        "markdown": [x for x in (extract_markdown_findings(r) for r in [
            "research/crypto-vc-database-plan.md",
            "research/crypto-vc-haun-ventures.md",
            "research/crypto-vc-paradigm.md",
            "research/crypto-vc-research.md",
            "research/vc-overleving.md",
        ]) if x],
        "named_findings": (
            extract_named_findings("research/vc-overleving.md", ["Lighter", "Nockchain"])
        ),
        "token_measurements": survival,
        "known_limitation": (
            "De CryptoRank-slices in het brononderzoek tonen maximaal tien regels per fonds. "
            "Ze zijn hier alleen als controlelijst overgenomen, niet als dekkingsmaat."
        ),
    }
    with open(os.path.join(OUT_DIR, "investment-dashboard-vc-research.json"), "w") as fh:
        json.dump(research_doc, fh, indent=1, ensure_ascii=False)

    # --- manifest
    try:
        commit = subprocess.check_output(
            ["git", "-C", SOURCE_REPOSITORY, "rev-parse", "HEAD"], text=True
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", SOURCE_REPOSITORY, "status", "--porcelain"], text=True
        ).strip()
    except Exception as exc:  # pragma: no cover
        commit, dirty = "onbekend (%s)" % exc, ""

    files = []
    for rel in SOURCE_FILES:
        path = src(rel)
        if not os.path.exists(path):
            warnings.append("bronbestand ontbreekt: %s" % rel)
            continue
        files.append({
            "path": rel,
            "bytes": os.path.getsize(path),
            "sha256": sha256(path),
        })

    manifest = {
        "source_repository": SOURCE_REPOSITORY,
        "source_git_commit": commit,
        "source_working_tree_clean": dirty == "",
        "import_date": date.today().isoformat(),
        "files": files,
        "records_imported": {
            "investment-dashboard-rounds.json": len(rows),
            "investment-dashboard-vc-research.json":
                len(research_doc["markdown"]) + len(research_doc["named_findings"]),
            "token_measurements": len((survival or {}).get("tokens", [])),
        },
        "parser_warnings": warnings,
        "write_scope": "Dit script schrijft uitsluitend in data/imported/ van deze repository.",
    }
    with open(os.path.join(OUT_DIR, "source-manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)

    print("Geïmporteerd uit %s" % SOURCE_REPOSITORY)
    print("  commit           %s" % commit)
    print("  werkboom schoon  %s" % (dirty == ""))
    print("  fonds-rondeparen %d" % len(rows))
    print("  tokenmetingen    %d" % len((survival or {}).get("tokens", [])))
    print("  bronbestanden    %d" % len(files))
    for w in warnings:
        print("  waarschuwing: %s" % w)


if __name__ == "__main__":
    main()
