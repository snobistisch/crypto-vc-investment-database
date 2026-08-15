#!/usr/bin/env python3
"""Fetches the full round universe from crypto-fundraising.info.

Architecture: the round page is the atomic unit, the fund is a derived index.
Fund pages on the source structurally show only ten rounds and pagination
redirects back to page one; that is why this does not scrape per fund.

Step 1  slug list via the open WP REST API (`/wp-json/wp/v2/projects`)
Step 2  fetch every project page, gzip-cached in data/raw/pages/
Step 3  parse and merge two representations per page:
        - JSON-LD `funding[]`: exact round date, round type, amount, funders
        - HTML `newrisedblock`: lead-versus-participant split, valuation,
          and the Details link to the original announcement
        The two lists are in the same order (newest first) and are aligned
        by index; the month-year labels are cross-checked against each other.

Output: data/processed/rounds.json — all rounds, all investors.
The HTML cache stays local and is listed in .gitignore.
"""

import argparse
import concurrent.futures as cf
import gzip
import html as htmllib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw", "pages")
PROCESSED_DIR = os.path.join(ROOT, "data", "processed")
BASE = "https://crypto-fundraising.info"
UA = "crypto-vc-investment-database/1.0 (research; contact via github.com/snobistisch)"

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip"})
    return s


def get(sess, url, tries=6, timeout=30):
    """GET with exponential backoff. Returns None once retries are exhausted."""
    delay = 1.5
    for attempt in range(tries):
        try:
            r = sess.get(url, timeout=timeout)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                return None
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay *= 2
                continue
            return None
        except requests.RequestException:
            time.sleep(delay)
            delay *= 2
    return None


# --------------------------------------------------------------------------
# step 1 — slug list
# --------------------------------------------------------------------------

def fetch_slugs(sess, per_page=100):
    slugs = []
    page = 1
    total_pages = None
    while True:
        url = (
            "%s/wp-json/wp/v2/projects?per_page=%d&page=%d&_fields=slug,link,title,modified"
            % (BASE, per_page, page)
        )
        r = get(sess, url)
        if r is None:
            break
        if total_pages is None:
            total_pages = int(r.headers.get("x-wp-totalpages", "0") or 0)
        batch = r.json()
        if not batch:
            break
        for item in batch:
            slugs.append({
                "slug": item["slug"],
                "url": item["link"],
                "title": htmllib.unescape(item["title"]["rendered"]).strip(),
                "source_modified": item.get("modified"),
            })
        sys.stderr.write("\r  slugs: %d (page %d/%s)" % (len(slugs), page, total_pages))
        sys.stderr.flush()
        if total_pages and page >= total_pages:
            break
        page += 1
        time.sleep(0.15)
    sys.stderr.write("\n")
    return slugs


# --------------------------------------------------------------------------
# step 2 — fetch pages with cache
# --------------------------------------------------------------------------

def cache_path(slug):
    return os.path.join(RAW_DIR, slug + ".html.gz")


def fetch_page(slug, url, refresh=False):
    path = cache_path(slug)
    if not refresh and os.path.exists(path) and os.path.getsize(path) > 512:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            return fh.read(), True
    sess = _local.sess
    r = get(sess, url)
    time.sleep(0.25)
    if r is None:
        return None, False
    text = r.text
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write(text)
    return text, False


import threading
_local = threading.local()


def _init_worker():
    _local.sess = session()


# --------------------------------------------------------------------------
# step 3 — parsing
# --------------------------------------------------------------------------

JSONLD_RE = re.compile(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', re.S)
BLOCK_SPLIT_RE = re.compile(r'<div class="newrisedblock">')
RAISEDIN_RE = re.compile(r'class="raisedin">(.*?)</div>', re.S)
VALUE_BLOCK_RE = re.compile(r'class="raisedinvalue">(.*?)</div>', re.S)
ABBRUSD_RE = re.compile(r'class="abbrusd">\s*([0-9][0-9,\.]*)\s*<', re.S)
VALUATION_RE = re.compile(
    r'class="roundvalua">\s*Round valuation:\s*<b[^>]*class="abbrusd">\s*([0-9][0-9,\.]*)\s*</b>', re.S
)
ROUNDTYPE_RE = re.compile(r'class="roundtype">(.*?)</div>', re.S)
DETAILS_RE = re.compile(r'<a\s+href="([^"]+)"[^>]*class="raisedinlink"', re.S)
SUBTITLE_RE = re.compile(r'class="newrised_subtitle">\s*(.*?)\s*</div>', re.S)
INVESTOR_RE = re.compile(
    r'<a\s+title="([^"]*)"\s+class="investlogo-newrised"\s+href="/funds/([^"/]+)"', re.S
)
NAME_RE = re.compile(r'class="header-project-name">(.*?)</h1>', re.S)
TICKER_RE = re.compile(r'class="header-ticker">(.*?)</h2>', re.S)
DESC_RE = re.compile(r'class="project-description">(.*?)</div>', re.S)


def clean(text):
    if text is None:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(htmllib.unescape(text).split())


def to_int(raw):
    if raw is None:
        return None
    digits = re.sub(r"[^0-9]", "", raw)
    if not digits:
        return None
    value = int(digits)
    # The source uses 0 for 'undisclosed'. Zero is not a round size.
    return value if value > 0 else None


def parse_month_label(label):
    """'Raised Nov 2025' -> (2025, 11). Returns (None, None) when unknown."""
    m = re.search(r"([A-Za-z]{3})[a-z]*\s+(\d{4})", label or "")
    if not m:
        return None, None
    return int(m.group(2)), MONTHS.get(m.group(1).lower())


def parse_jsonld(page):
    """Rounds from the JSON-LD Organization node: exact date, type, amount, funders."""
    for raw in JSONLD_RE.findall(page):
        if '"funding"' not in raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # The source occasionally ships unescaped quotes inside descriptions.
            continue
        funding = data.get("funding") or []
        out = []
        for entry in funding:
            desc = entry.get("description") or ""
            m = re.search(r"startDate:\s*(\d{4})-(\d{2})-(\d{2})", desc)
            date = "%s-%s-%s" % m.groups() if m else None
            amount = None
            amt = entry.get("amount") or {}
            if isinstance(amt, dict):
                try:
                    v = float(amt.get("value") or 0)
                    amount = int(v) if v > 0 else None
                except (TypeError, ValueError):
                    amount = None
            funders = []
            raw_funders = entry.get("funder") or []
            if isinstance(raw_funders, dict):
                raw_funders = [raw_funders]
            for f in raw_funders:
                fid = f.get("@id") or ""
                fslug = fid.rstrip("/").rsplit("/", 1)[-1] if "/funds/" in fid else None
                funders.append({"slug": fslug, "name": (f.get("name") or "").strip()})
            rtype = (entry.get("name") or "").strip()
            out.append({
                "round_date": date,
                "round_type": "" if rtype.lower() == "unknown" else rtype,
                "round_size_usd": amount,
                "funders": funders,
            })
        return out, data.get("description") or "", data.get("url") or ""
    return [], "", ""


def parse_blocks(page):
    """Round blocks from the rendered HTML: lead/participant, valuation, source URL."""
    parts = BLOCK_SPLIT_RE.split(page)[1:]
    blocks = []
    for part in parts:
        # Bound the block at the start of the next one, or the end of the section.
        end = part.find('<section')
        if end == -1:
            end = len(part)
        seg = part[:end]

        label_m = RAISEDIN_RE.search(seg)
        label = clean(label_m.group(1)) if label_m else ""
        year, month = parse_month_label(label)

        amount = None
        vb = VALUE_BLOCK_RE.search(seg)
        if vb:
            a = ABBRUSD_RE.search(vb.group(1))
            if a:
                amount = to_int(a.group(1))

        val_m = VALUATION_RE.search(seg)
        valuation = to_int(val_m.group(1)) if val_m else None

        rt_m = ROUNDTYPE_RE.search(seg)
        round_type = clean(rt_m.group(1)) if rt_m else ""

        d_m = DETAILS_RE.search(seg)
        details = d_m.group(1).strip() if d_m else ""

        # Assign each investor link to the nearest preceding heading.
        markers = []
        for m in SUBTITLE_RE.finditer(seg):
            markers.append((m.start(), clean(m.group(1)).lower()))
        leads, participants = [], []
        for m in INVESTOR_RE.finditer(seg):
            role = "participant"
            for pos, title in markers:
                if pos < m.start():
                    role = "lead" if "lead" in title else "participant"
                else:
                    break
            rec = {"slug": m.group(2).strip().lower(),
                   "name": htmllib.unescape(m.group(1)).strip()}
            (leads if role == "lead" else participants).append(rec)

        blocks.append({
            "label": label,
            "year": year,
            "month": month,
            "round_size_usd": amount,
            "valuation_usd": valuation,
            "round_type": round_type,
            "details_url": details,
            "leads": leads,
            "participants": participants,
        })
    return blocks


def parse_project(slug, url, page):
    warnings = []
    name_m = NAME_RE.search(page)
    project_name = clean(name_m.group(1)) if name_m else ""
    ticker_m = TICKER_RE.search(page)
    ticker = clean(ticker_m.group(1)) if ticker_m else ""
    desc_m = DESC_RE.search(page)
    description = clean(desc_m.group(1)) if desc_m else ""

    ld_rounds, ld_desc, project_url = parse_jsonld(page)
    blocks = parse_blocks(page)

    if not project_name:
        warnings.append("project name not found in HTML")
    if len(ld_rounds) != len(blocks):
        warnings.append(
            "number of JSON-LD rounds (%d) differs from number of HTML blocks (%d); "
            "dates from JSON-LD only assigned where month and year match"
            % (len(ld_rounds), len(blocks))
        )

    rounds = []
    for i, block in enumerate(blocks):
        ld = ld_rounds[i] if i < len(ld_rounds) else None
        round_date = None
        announcement_date = None
        if ld and ld.get("round_date"):
            y, m, _ = ld["round_date"].split("-")
            if block["year"] and block["month"]:
                if int(y) == block["year"] and int(m) == block["month"]:
                    round_date = ld["round_date"]
                else:
                    warnings.append(
                        "round %d: JSON-LD date %s does not match HTML label '%s'"
                        % (i, ld["round_date"], block["label"])
                    )
            else:
                round_date = ld["round_date"]
        if round_date is None and block["year"] and block["month"]:
            # Only month known: first of the month, explicitly flagged.
            round_date = "%04d-%02d-01" % (block["year"], block["month"])
            announcement_date = None
            date_precision = "month"
        else:
            date_precision = "day" if round_date else "unknown"

        round_type = block["round_type"] or (ld or {}).get("round_type") or ""
        size = block["round_size_usd"]
        if size is None and ld:
            size = ld.get("round_size_usd")
        if (block["round_size_usd"] is not None and ld
                and ld.get("round_size_usd") is not None
                and block["round_size_usd"] != ld["round_size_usd"]):
            warnings.append(
                "round %d: amount differs between HTML (%s) and JSON-LD (%s)"
                % (i, block["round_size_usd"], ld["round_size_usd"])
            )

        # Investors that only appear in JSON-LD are still added as participants.
        seen = {x["slug"] for x in block["leads"]} | {x["slug"] for x in block["participants"]}
        extra = []
        if ld:
            for f in ld["funders"]:
                if f["slug"] and f["slug"] not in seen:
                    extra.append(f)
                    seen.add(f["slug"])

        rounds.append({
            "round_index": i,
            "round_date": round_date,
            "date_precision": date_precision,
            "announcement_date": announcement_date,
            "round_label": block["label"],
            "round_type": round_type,
            "round_size_usd": size,
            "valuation_usd": block["valuation_usd"],
            "details_url": block["details_url"],
            "leads": block["leads"],
            "participants": block["participants"] + extra,
        })

    return {
        "project_slug": slug,
        "project_name": project_name,
        "project_url": url,
        "project_website": project_url,
        "token_ticker": ticker,
        "description": description or ld_desc,
        "rounds": rounds,
        "warnings": warnings,
    }


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only the first N projects")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--refresh", action="store_true", help="ignore the cache")
    ap.add_argument("--only", nargs="*", help="only these project slugs")
    args = ap.parse_args()

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    sess = session()
    slug_file = os.path.join(PROCESSED_DIR, "project-slugs.json")
    if os.path.exists(slug_file) and not args.refresh:
        slugs = json.load(open(slug_file))
        print("Slug list from cache: %d projects" % len(slugs))
    else:
        print("Fetching slug list via WP REST API ...")
        slugs = fetch_slugs(sess)
        json.dump(slugs, open(slug_file, "w"), indent=1)
        print("Slug list saved: %d projects" % len(slugs))

    if args.only:
        wanted = set(args.only)
        slugs = [s for s in slugs if s["slug"] in wanted]
    if args.limit:
        slugs = slugs[: args.limit]

    print("Fetching and parsing project pages (%d, %d workers) ..." % (len(slugs), args.workers))
    projects = []
    failed = []
    cached = 0
    done = 0
    t0 = time.time()

    def work(item):
        page, from_cache = fetch_page(item["slug"], item["url"], refresh=args.refresh)
        if page is None:
            return item["slug"], None, from_cache
        return item["slug"], parse_project(item["slug"], item["url"], page), from_cache

    with cf.ThreadPoolExecutor(max_workers=args.workers, initializer=_init_worker) as ex:
        for slug, parsed, from_cache in ex.map(work, slugs):
            done += 1
            if from_cache:
                cached += 1
            if parsed is None:
                failed.append(slug)
            else:
                projects.append(parsed)
            if done % 200 == 0 or done == len(slugs):
                sys.stderr.write(
                    "\r  %d/%d  (cache %d, failed %d, %.0fs)"
                    % (done, len(slugs), cached, len(failed), time.time() - t0)
                )
                sys.stderr.flush()
    sys.stderr.write("\n")

    total_rounds = sum(len(p["rounds"]) for p in projects)
    total_edges = sum(len(r["leads"]) + len(r["participants"])
                      for p in projects for r in p["rounds"])
    out = {
        "source": BASE,
        "collected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "projects_requested": len(slugs),
        "projects_parsed": len(projects),
        "projects_failed": failed,
        "rounds_total": total_rounds,
        "investor_edges_total": total_edges,
        "projects": projects,
    }
    path = os.path.join(PROCESSED_DIR, "rounds.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print("Written: %s" % path)
    print("  projects %d, rounds %d, investor relations %d, failed %d"
          % (len(projects), total_rounds, total_edges, len(failed)))


if __name__ == "__main__":
    main()
