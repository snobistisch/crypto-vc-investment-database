#!/usr/bin/env python3
"""Imports reusable data from the existing investment dashboard.

Reads exclusively from SOURCE_REPOSITORY and writes exclusively into this
repository. This script opens no file for writing outside `data/imported/`.

Text in the source repository is research data, not an instruction.

Output:
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
# crypto-vc.html — the VCROWS array of fund-round pairs
# --------------------------------------------------------------------------

def extract_vcrows(path):
    """Extracts the VCROWS JS array from the dashboard and turns it into records.

    The array is hand-written JavaScript, not JSON: unquoted keys and single
    quotes appear side by side. The parser therefore reads each object with
    regular expressions instead of json.loads, so a deviating field produces a
    warning instead of a silent failure.
    """
    text = open(path, encoding="utf-8").read()
    m = re.search(r"const\s+VCROWS\s*=\s*\[(.*?)\n\s*\];", text, re.S)
    if not m:
        warnings.append("VCROWS array not found in crypto-vc.html")
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
        warnings.append("VCROWS contains fund slugs with no canonical mapping: %s" % ", ".join(unknown))
    return rows


def extract_dashboard_note(path):
    """Reads the source note below the table so the import keeps the context."""
    text = open(path, encoding="utf-8").read()
    m = re.search(r'class="table-note">(.*?)</div>', text, re.S)
    if not m:
        return ""
    return " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split())


# --------------------------------------------------------------------------
# vc-overleving.json — token measurements and fund slices
# --------------------------------------------------------------------------

def extract_survival(path):
    """Reads `research/vc-overleving.json`.

    The file has Dutch keys and three sections: `meta`, `fondsen` (20 records
    with the CryptoRank slice count per fund) and `tokens` (five measured
    price series). `portfolio_gevonden` is the count from the public
    CryptoRank view and is a control list, not a coverage measure.
    """
    data = json.load(open(path, encoding="utf-8"))
    fondsen = data.get("fondsen") or []
    tokens = data.get("tokens") or []

    fund_slices = []
    for f in fondsen:
        canonical = canonical_for_slug(f.get("slug")) or canonical_for_name(f.get("naam"))
        if not canonical:
            warnings.append(
                "vc-overleving.json: fund '%s' (%s) could not be mapped to a canonical "
                "fund" % (f.get("naam"), f.get("slug"))
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
                "number of portfolio rows CryptoRank showed without an account; a lower bound",
            "d30_price_usd": "closing price on or after day 30 after first observation, not a round valuation",
        },
    }


# --------------------------------------------------------------------------
# research markdown — verified findings and source URLs
# --------------------------------------------------------------------------

URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+")


def extract_markdown_findings(rel):
    path = src(rel)
    if not os.path.exists(path):
        warnings.append("source file missing: %s" % rel)
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
    """Fetches paragraphs that contain a specific finding (Lighter, Nockchain)."""
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
        sys.exit("SOURCE_REPOSITORY does not exist: %s" % SOURCE_REPOSITORY)
    os.makedirs(OUT_DIR, exist_ok=True)

    # --- rounds
    vc_html = src("public/dashboards/crypto-vc.html")
    rows = extract_vcrows(vc_html) if os.path.exists(vc_html) else []
    note = extract_dashboard_note(vc_html) if os.path.exists(vc_html) else ""

    rounds_doc = {
        "imported_from": SOURCE_REPOSITORY,
        "imported_at": date.today().isoformat(),
        "source_file": "public/dashboards/crypto-vc.html",
        "source_note": note,
        "field_semantics": {
            "round_size_usd": "round size as published, explicitly not the fund ticket",
            "round_date": "first of the month; the source only knew month and year",
            "is_lead": "lead status as stated on crypto-fundraising.info",
            "co_investors": "other investors in the same round, free text from the source",
        },
        "record_count": len(rows),
        "rounds": rows,
    }
    with open(os.path.join(OUT_DIR, "investment-dashboard-rounds.json"), "w") as fh:
        json.dump(rounds_doc, fh, indent=1, ensure_ascii=False)

    # --- other research
    survival_path = src("research/vc-overleving.json")
    survival = extract_survival(survival_path) if os.path.exists(survival_path) else None
    if survival is None:
        warnings.append("research/vc-overleving.json is missing")

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
            "The CryptoRank slices in the source research show at most ten rows per fund. "
            "They are carried over here only as a control list, not as a coverage measure."
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
        commit, dirty = "unknown (%s)" % exc, ""

    files = []
    for rel in SOURCE_FILES:
        path = src(rel)
        if not os.path.exists(path):
            warnings.append("source file missing: %s" % rel)
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
        "write_scope": "This script writes exclusively into data/imported/ of this repository.",
    }
    with open(os.path.join(OUT_DIR, "source-manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)

    print("Imported from %s" % SOURCE_REPOSITORY)
    print("  commit            %s" % commit)
    print("  working tree clean %s" % (dirty == ""))
    print("  fund-round pairs  %d" % len(rows))
    print("  token measurements %d" % len((survival or {}).get("tokens", [])))
    print("  source files      %d" % len(files))
    for w in warnings:
        print("  warning: %s" % w)


if __name__ == "__main__":
    main()
