#!/usr/bin/env python3
"""Haalt controletotalen per fonds op bij derde bronnen.

Deze cijfers zijn *controlelijsten*, geen waarheid. Ze dienen om te meten waar
de eigen dataset afwijkt, niet om die aan te vullen. Waar een bron niet
leesbaar is, wordt dat als zodanig vastgelegd; er wordt niets geschat.

Bronnen:
  crypto-fundraising.info/funds/<slug>/  — toont structureel tien regels; de
      telling die hier wordt vastgelegd is dus het displaymaximum, niet het
      portefeuilletotaal. Dat is precies de reden dat de dataset via
      rondepagina's is opgebouwd.
  cryptorank.io/funds/<slug>/portfolio   — `__NEXT_DATA__` bevat een veld
      `investments` met het door CryptoRank zelf getelde aantal investeringen.
  officiële portfoliopagina                — statische HTML wordt geteld op
      unieke uitgaande links; SPA's leveren niets en worden als 'niet leesbaar'
      genoteerd.
  rootdata.com                             — vereist een sleutel of JavaScript;
      uitkomst wordt genoteerd zoals waargenomen.

Uitvoer: data/processed/coverage-controls.json
"""

import json
import os
import re
import sys
import time
from datetime import date
from urllib.parse import urlparse

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import FUNDS  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(sess, url, timeout=25):
    try:
        r = sess.get(url, timeout=timeout, allow_redirects=True)
        return r
    except requests.RequestException as exc:
        return exc


def source_fund_page(sess, source_slug):
    url = "https://crypto-fundraising.info/funds/%s/" % source_slug
    r = get(sess, url)
    if not hasattr(r, "status_code"):
        return {"url": url, "status": "fout: %s" % type(r).__name__, "visible_rows": None}
    if r.status_code != 200:
        return {"url": url, "status": "HTTP %d" % r.status_code, "visible_rows": None}
    rows = len(set(re.findall(r'href="/projects/([a-z0-9\-]+)"', r.text)))
    return {
        "url": url,
        "status": "HTTP 200",
        "visible_rows": rows,
        "note": ("Fondspagina toont een vast maximum aantal regels; dit is een "
                 "displaylimiet en geen portefeuilletotaal."),
    }


def cryptorank(sess, url):
    r = get(sess, url)
    if not hasattr(r, "status_code"):
        return {"url": url, "status": "fout: %s" % type(r).__name__, "investments": None}
    if r.status_code != 200:
        return {"url": url, "status": "HTTP %d" % r.status_code, "investments": None}
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                  r.text, re.S)
    if not m:
        return {"url": url, "status": "HTTP 200, geen __NEXT_DATA__", "investments": None}
    try:
        data = json.loads(m.group(1))
        fund = data["props"]["pageProps"]["fund"]
    except (json.JSONDecodeError, KeyError):
        return {"url": url, "status": "HTTP 200, fondsobject niet gevonden", "investments": None}
    return {
        "url": url,
        "status": "HTTP 200",
        "investments": fund.get("investments"),
        "country": fund.get("country") or "",
        "tier": fund.get("tier"),
        "note": ("`investments` is CryptoRanks eigen telling. De zichtbare "
                 "portefeuillelijst toont zonder account maar tien regels; die "
                 "lijst is niet gebruikt."),
    }


def official_portfolio(sess, url):
    r = get(sess, url)
    if not hasattr(r, "status_code"):
        return {"url": url, "status": "fout: %s" % type(r).__name__, "names_found": None}
    if r.status_code != 200:
        return {"url": url, "status": "HTTP %d" % r.status_code, "names_found": None}
    host = urlparse(url).netloc
    hrefs = re.findall(r'href="(https?://[^"]+)"', r.text)
    external = set()
    for h in hrefs:
        netloc = urlparse(h).netloc
        if netloc and host not in netloc and "twitter" not in netloc and "x.com" not in netloc \
                and "linkedin" not in netloc and "youtube" not in netloc:
            external.add(netloc.lower().replace("www.", ""))
    body = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S)
    text_len = len(re.sub(r"<[^>]+>", " ", body).split())
    readable = len(external) >= 15
    return {
        "url": url,
        "status": "HTTP 200",
        "names_found": len(external) if readable else None,
        "words_in_page": text_len,
        "note": ("Unieke uitgaande domeinen als benadering van portefeuillenamen."
                 if readable else
                 "Pagina levert geen leesbare portefeuillelijst in statische HTML "
                 "(client-side gerenderd). Niet geteld; geen schatting gemaakt."),
    }


def rootdata(sess, fund_name):
    url = "https://www.rootdata.com/search?k=%s" % requests.utils.quote(fund_name)
    r = get(sess, url)
    if not hasattr(r, "status_code"):
        return {"url": url, "status": "fout: %s" % type(r).__name__, "investments": None}
    if r.status_code != 200:
        return {"url": url, "status": "HTTP %d" % r.status_code, "investments": None,
                "note": "Geen telling verkregen; niet geschat."}
    has_data = bool(re.search(r"investment", r.text, re.I))
    return {
        "url": url,
        "status": "HTTP 200",
        "investments": None,
        "note": ("Pagina geladen maar de portefeuillelijst wordt client-side "
                 "opgebouwd; zonder API-sleutel is geen telling af te leiden. "
                 "Niet geschat." if has_data else
                 "Geen bruikbare inhoud in statische HTML. Niet geschat."),
    }


def main():
    sess = requests.Session()
    sess.headers.update({"User-Agent": UA, "Accept-Language": "en"})

    out = {"collected_at": date.today().isoformat(), "funds": {}}
    for slug, meta in FUNDS.items():
        sys.stderr.write("  %s ...\n" % slug)
        rec = {
            "fund_name": meta["fund_name"],
            "crypto_fundraising": source_fund_page(sess, meta["source_slugs"][0]),
            "cryptorank": cryptorank(sess, meta["cryptorank_url"]),
            "official_portfolio": official_portfolio(sess, meta["official_portfolio_url"]),
            "rootdata": rootdata(sess, meta["fund_name"]),
        }
        out["funds"][slug] = rec
        time.sleep(0.6)

    path = os.path.join(PROCESSED, "coverage-controls.json")
    os.makedirs(PROCESSED, exist_ok=True)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("Geschreven: %s" % path)
    for slug, rec in out["funds"].items():
        print("  %-20s cf=%-4s cr=%-5s off=%-5s" % (
            slug,
            rec["crypto_fundraising"].get("visible_rows"),
            rec["cryptorank"].get("investments"),
            rec["official_portfolio"].get("names_found"),
        ))


if __name__ == "__main__":
    main()
