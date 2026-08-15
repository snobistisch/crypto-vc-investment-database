"""Tests op de genormaliseerde dataset en op de parserlogica.

De parsertests draaien op vastgelegde HTML-fragmenten, zodat ze zonder netwerk
werken en een verandering aan de bronsite zichtbaar wordt als een falende test
in plaats van als stille datavervuiling.
"""

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import fetch_crypto_fundraising as fetcher  # noqa: E402
import normalize_funds as norm  # noqa: E402
from funds import FUNDS, canonical_for_name, canonical_for_slug  # noqa: E402

DATASET = os.path.join(ROOT, "data", "processed", "dataset.json")


@pytest.fixture(scope="module")
def dataset():
    if not os.path.exists(DATASET):
        pytest.skip("dataset.json ontbreekt; draai eerst normalize_funds.py")
    with open(DATASET) as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# aliassen
# --------------------------------------------------------------------------

def test_twintig_fondsen():
    assert len(FUNDS) == 20


def test_geen_bronslug_bij_twee_fondsen():
    seen = {}
    for slug, meta in FUNDS.items():
        for s in meta["source_slugs"]:
            assert s not in seen, "bronslug %s hoort bij %s en %s" % (s, seen.get(s), slug)
            seen[s] = slug


def test_alias_varianten_wijzen_naar_hetzelfde_fonds():
    assert canonical_for_name("Dragonfly Capital") == canonical_for_name("Dragonfly")
    assert canonical_for_name("Maven 11 Capital") == canonical_for_name("Maven11")
    assert canonical_for_name("cyber•Fund") == canonical_for_name("cyber Fund")
    assert canonical_for_slug("dragonfly-capital") == "dragonfly"


def test_onbekende_naam_wordt_niet_gegokt():
    assert canonical_for_name("Dragonfly Adjacent Capital") is None
    assert canonical_for_slug("bain-capital-ventures") is None
    assert canonical_for_name("") is None


def test_iedere_alias_heeft_bewijs():
    for slug, meta in FUNDS.items():
        assert meta["alias_evidence"].strip(), slug


# --------------------------------------------------------------------------
# parser
# --------------------------------------------------------------------------

BLOCK = '''
<div class="newrisedblock">
  <div class="raise_date_value">
    <div class="raisedin"> Raised Nov 2025 </div>
    <div class="raisedinvalue"><span class="abbrusd"> 68000000 </span></div>
    <div class="roundtype">Series B</div>
    <div class="roundvalua">Round valuation: <b class="abbrusd">1500000000</b></div>
    <a href="https://example.com/press" target="_blank" class="raisedinlink">Details</a>
  </div>
  <div class="newrised_investors">
    <div class="newrised_investors lead">
      <div class="newrised_subtitle">Lead Investors</div>
      <a title="Founders fund" class="investlogo-newrised" href="/funds/founders-fund"></a>
    </div>
    <div class="newrised_investors">
      <div class="newrised_subtitle">Investors</div>
      <a title="HAUN Ventures" class="investlogo-newrised" href="/funds/haun-ventures"></a>
      <a title="Robinhood" class="investlogo-newrised" href="/funds/robinhood"></a>
    </div>
  </div>
</div>
'''


def test_blok_parser_splitst_lead_en_deelnemer():
    blocks = fetcher.parse_blocks(BLOCK)
    assert len(blocks) == 1
    b = blocks[0]
    assert [x["slug"] for x in b["leads"]] == ["founders-fund"]
    assert [x["slug"] for x in b["participants"]] == ["haun-ventures", "robinhood"]
    assert b["round_size_usd"] == 68000000
    assert b["valuation_usd"] == 1500000000
    assert b["round_type"] == "Series B"
    assert b["details_url"] == "https://example.com/press"
    assert (b["year"], b["month"]) == (2025, 11)


def test_bedrag_nul_wordt_onbekend_en_niet_nul():
    assert fetcher.to_int("0") is None
    assert fetcher.to_int("") is None
    assert fetcher.to_int(None) is None
    assert fetcher.to_int("1,500,000") == 1500000


def test_tbd_blok_levert_geen_bedrag():
    tbd = BLOCK.replace('<span class="abbrusd"> 68000000 </span>',
                        '<span style="x">TBD</span>')
    b = fetcher.parse_blocks(tbd)[0]
    assert b["round_size_usd"] is None


def test_jsonld_nulbedrag_wordt_leeg():
    page = '''<script type="application/ld+json">{"@context":"https://schema.org",
    "funding":[{"@type":"MonetaryGrant","name":"Unknown","description":"startDate: 2024-05-21",
    "amount":{"@type":"MonetaryAmount","value":0,"currency":"USD"},
    "funder":[{"@type":"Organization","@id":"https://crypto-fundraising.info/funds/paradigm",
    "name":"Paradigm"}]}]}</script>'''
    rounds, _desc, _url = fetcher.parse_jsonld(page)
    assert len(rounds) == 1
    assert rounds[0]["round_size_usd"] is None
    assert rounds[0]["round_date"] == "2024-05-21"
    assert rounds[0]["round_type"] == ""
    assert rounds[0]["funders"][0]["slug"] == "paradigm"


def test_maandlabel_zonder_dag():
    assert fetcher.parse_month_label("Raised Apr 2019") == (2019, 4)
    assert fetcher.parse_month_label("Raised") == (None, None)


# --------------------------------------------------------------------------
# classificatie
# --------------------------------------------------------------------------

def test_rondetype_naar_investment_type():
    assert norm.classify_investment_type("Seed") == "equity"
    assert norm.classify_investment_type("Series A") == "equity"
    assert norm.classify_investment_type("Public sale") == "public_sale"
    assert norm.classify_investment_type("Strategic") == "strategic"
    assert norm.classify_investment_type("") == "unknown"


def test_grants_worden_uitgesloten():
    assert norm.is_excluded("Grant")
    assert not norm.is_excluded("Seed")


def test_verificatiestatus():
    assert norm.verification_status(True, True, False) == "verified_primary"
    assert norm.verification_status(False, True, False) == "verified_aggregator_only"
    assert norm.verification_status(True, True, True) == "conflict"


# --------------------------------------------------------------------------
# dataset
# --------------------------------------------------------------------------

def test_dataset_sleutels_uniek(dataset):
    ids = [r["investment_id"] for r in dataset["investments"]]
    assert len(ids) == len(set(ids))
    pairs = [(r["fund_slug"], r["round_id"]) for r in dataset["investments"]]
    assert len(pairs) == len(set(pairs))


def test_iedere_regel_heeft_bron(dataset):
    for r in dataset["investments"]:
        assert r["primary_source_url"] or r["aggregator_source_url"], r["investment_id"]


def test_fund_ticket_niet_gelijk_aan_rondegrootte(dataset):
    for r in dataset["investments"]:
        if r["fund_ticket_usd"] is not None:
            assert r["fund_ticket_usd"] != r["round_size_usd"]


def test_geen_nul_als_onbekend(dataset):
    for r in dataset["investments"]:
        for f in ("round_size_usd", "valuation_usd", "fund_ticket_usd"):
            assert r[f] is None or r[f] > 0


def test_lead_consistent_met_rol(dataset):
    for r in dataset["investments"]:
        assert r["is_lead"] == (r["fund_role"] in ("lead", "co-lead"))


def test_ronde_met_meerdere_fondsen_staat_een_keer_in_rondes(dataset):
    counts = {}
    for r in dataset["investments"]:
        counts[r["round_id"]] = counts.get(r["round_id"], 0) + 1
    multi = [rid for rid, n in counts.items() if n > 1]
    assert multi, "verwacht minstens één ronde met meerdere geselecteerde fondsen"
    round_ids = [r["round_id"] for r in dataset["rounds"]]
    assert len(round_ids) == len(set(round_ids))
    for rid in multi:
        assert rid in set(round_ids)


def test_alle_fondsen_in_dataset(dataset):
    assert {f["fund_slug"] for f in dataset["funds"]} == set(FUNDS)


def test_conflicten_hebben_een_regel(dataset):
    flagged = {r["investment_id"] for r in dataset["investments"] if r["conflict_flag"]}
    listed = {c["investment_id"] for c in dataset["conflicts"]}
    assert flagged <= listed
