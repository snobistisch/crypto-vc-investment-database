"""Tests on the normalised dataset and on the parser logic.

The parser tests run against captured HTML fragments, so they work without
the network and a change on the source site shows up as a failing test
instead of as silent data corruption.
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
        pytest.skip("dataset.json is missing; run normalize_funds.py first")
    with open(DATASET) as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# aliases
# --------------------------------------------------------------------------

def test_twenty_funds():
    assert len(FUNDS) == 20


def test_no_source_slug_belongs_to_two_funds():
    seen = {}
    for slug, meta in FUNDS.items():
        for s in meta["source_slugs"]:
            assert s not in seen, "source slug %s belongs to both %s and %s" % (s, seen.get(s), slug)
            seen[s] = slug


def test_alias_variants_point_to_the_same_fund():
    assert canonical_for_name("Dragonfly Capital") == canonical_for_name("Dragonfly")
    assert canonical_for_name("Maven 11 Capital") == canonical_for_name("Maven11")
    assert canonical_for_name("cyber•Fund") == canonical_for_name("cyber Fund")
    assert canonical_for_slug("dragonfly-capital") == "dragonfly"


def test_unknown_name_is_not_guessed():
    assert canonical_for_name("Dragonfly Adjacent Capital") is None
    assert canonical_for_slug("bain-capital-ventures") is None
    assert canonical_for_name("") is None


def test_every_alias_has_evidence():
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


def test_block_parser_splits_lead_and_participant():
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


def test_zero_amount_becomes_unknown_not_zero():
    assert fetcher.to_int("0") is None
    assert fetcher.to_int("") is None
    assert fetcher.to_int(None) is None
    assert fetcher.to_int("1,500,000") == 1500000


def test_tbd_block_yields_no_amount():
    tbd = BLOCK.replace('<span class="abbrusd"> 68000000 </span>',
                        '<span style="x">TBD</span>')
    b = fetcher.parse_blocks(tbd)[0]
    assert b["round_size_usd"] is None


def test_jsonld_zero_amount_becomes_blank():
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


def test_month_label_without_day():
    assert fetcher.parse_month_label("Raised Apr 2019") == (2019, 4)
    assert fetcher.parse_month_label("Raised") == (None, None)


# --------------------------------------------------------------------------
# classification
# --------------------------------------------------------------------------

def test_round_type_to_investment_type():
    assert norm.classify_investment_type("Seed") == "equity"
    assert norm.classify_investment_type("Series A") == "equity"
    assert norm.classify_investment_type("Public sale") == "public_sale"
    assert norm.classify_investment_type("Strategic") == "strategic"
    assert norm.classify_investment_type("") == "unknown"


def test_grants_are_excluded():
    assert norm.is_excluded("Grant")
    assert not norm.is_excluded("Seed")


def test_verification_status():
    assert norm.verification_status(True, True, False) == "verified_primary"
    assert norm.verification_status(False, True, False) == "verified_aggregator_only"
    assert norm.verification_status(True, True, True) == "conflict"


# --------------------------------------------------------------------------
# dataset
# --------------------------------------------------------------------------

def test_dataset_keys_unique(dataset):
    ids = [r["investment_id"] for r in dataset["investments"]]
    assert len(ids) == len(set(ids))
    pairs = [(r["fund_slug"], r["round_id"]) for r in dataset["investments"]]
    assert len(pairs) == len(set(pairs))


def test_every_row_has_a_source(dataset):
    for r in dataset["investments"]:
        assert r["primary_source_url"] or r["aggregator_source_url"], r["investment_id"]


def test_fund_ticket_not_equal_to_round_size(dataset):
    for r in dataset["investments"]:
        if r["fund_ticket_usd"] is not None:
            assert r["fund_ticket_usd"] != r["round_size_usd"]


def test_no_zero_as_unknown(dataset):
    for r in dataset["investments"]:
        for f in ("round_size_usd", "valuation_usd", "fund_ticket_usd"):
            assert r[f] is None or r[f] > 0


def test_lead_consistent_with_role(dataset):
    for r in dataset["investments"]:
        assert r["is_lead"] == (r["fund_role"] in ("lead", "co-lead"))


def test_round_with_multiple_funds_appears_once_in_rounds(dataset):
    counts = {}
    for r in dataset["investments"]:
        counts[r["round_id"]] = counts.get(r["round_id"], 0) + 1
    multi = [rid for rid, n in counts.items() if n > 1]
    assert multi, "expected at least one round with multiple selected funds"
    round_ids = [r["round_id"] for r in dataset["rounds"]]
    assert len(round_ids) == len(set(round_ids))
    for rid in multi:
        assert rid in set(round_ids)


def test_all_funds_in_dataset(dataset):
    assert {f["fund_slug"] for f in dataset["funds"]} == set(FUNDS)


def test_conflicts_have_a_row(dataset):
    flagged = {r["investment_id"] for r in dataset["investments"] if r["conflict_flag"]}
    listed = {c["investment_id"] for c in dataset["conflicts"]}
    assert flagged <= listed
