"""Tests on the generated frontend page.

The page carries the whole dataset inline, so the risks worth testing are:
the payload not matching the dataset, the page reaching out to the network,
and the placeholder surviving into the output.
"""

import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

PAGE = os.path.join(ROOT, "docs", "index.html")
TEMPLATE = os.path.join(ROOT, "frontend", "template.html")
DATASET = os.path.join(ROOT, "data", "processed", "dataset.json")


@pytest.fixture(scope="module")
def html():
    if not os.path.exists(PAGE):
        pytest.skip("docs/index.html is missing; run build_frontend.py first")
    return open(PAGE, encoding="utf-8").read()


@pytest.fixture(scope="module")
def payload(html):
    m = re.search(r'<script id="payload" type="application/json">(.*?)</script>',
                  html, re.S)
    assert m, "payload block not found"
    return json.loads(m.group(1).replace("<\\/", "</"))


@pytest.fixture(scope="module")
def dataset():
    if not os.path.exists(DATASET):
        pytest.skip("dataset.json is missing")
    return json.load(open(DATASET))


def test_placeholder_is_replaced(html):
    assert "__PAYLOAD__" not in html


def test_template_keeps_its_placeholder():
    assert "__PAYLOAD__" in open(TEMPLATE, encoding="utf-8").read()


def test_page_is_self_contained(html):
    """No external stylesheet, script, image or font may be referenced.

    The page must open from disk with no network. Anchor hrefs to real
    sources are expected and excluded — they are links the reader clicks,
    not resources the page loads.
    """
    for attr in ("src", "href"):
        for m in re.finditer(r'<(\w+)[^>]*\b%s="(https?:)?//[^"]+"' % attr, html):
            tag = m.group(1).lower()
            assert tag == "a", "external %s on <%s>: %s" % (attr, tag, m.group(0)[:110])
    assert "fetch(" not in html
    assert "XMLHttpRequest" not in html


def test_row_count_matches_dataset(payload, dataset):
    assert len(payload["rows"]) == len(dataset["investments"])
    assert payload["meta"]["investments"] == len(dataset["investments"])
    assert payload["meta"]["rounds"] == len(dataset["rounds"])
    assert payload["meta"]["companies"] == len(dataset["projects"])


def test_all_funds_with_matching_totals(payload, dataset):
    assert len(payload["funds"]) == len(dataset["funds"])
    expected = {}
    for r in dataset["investments"]:
        expected[r["fund_slug"]] = expected.get(r["fund_slug"], 0) + 1
    for f in payload["funds"]:
        assert f["rounds"] == expected.get(f["slug"], 0), f["slug"]
    assert sum(f["rounds"] for f in payload["funds"]) == len(dataset["investments"])


def test_fund_row_indices_are_valid(payload):
    n = len(payload["funds"])
    for row in payload["rows"]:
        assert 0 <= row[0] < n


def test_lookup_indices_resolve(payload):
    L = payload["lookups"]
    for row in payload["rows"]:
        assert L["projects"][row[1]]
        assert L["project_meta"][row[1]] is not None
        assert row[3] < len(L["round_types"])
        assert row[4] < len(L["investment_types"])
        assert row[5] < len(L["roles"])
        for ci in row[13]:
            assert L["investors"][ci]


def test_blank_amounts_are_zero_not_null(payload):
    """The page treats 0 as 'not disclosed' and renders an em dash for it.

    What must never happen is a real amount of zero reaching the payload,
    which would be indistinguishable from unknown.
    """
    for row in payload["rows"]:
        assert isinstance(row[7], int) and row[7] >= 0
        assert isinstance(row[8], int) and row[8] >= 0


def test_lead_flag_matches_role(payload):
    roles = payload["lookups"]["roles"]
    for row in payload["rows"]:
        assert bool(row[6]) == (roles[row[5]] in ("lead", "co-lead"))


def test_every_row_has_a_source(payload):
    for row in payload["rows"]:
        assert row[11] or row[12]


def test_network_pairs_are_ordered_and_valid(payload):
    n = len(payload["funds"])
    counts = [p[2] for p in payload["pairs"]]
    assert counts == sorted(counts, reverse=True)
    for a, b, c in payload["pairs"]:
        assert 0 <= a < n and 0 <= b < n and a != b and c > 0


def test_completeness_statement_present(html, payload):
    assert "structurally invisible" in payload["meta"]["completeness"]
    assert "Not investment advice" in html


def test_no_hardcoded_headline_numbers(html):
    """Narrative figures must come from the payload, not the template.

    Guards the rule that no number is typed by hand: the counts should not
    appear as literals in the template's prose.
    """
    template = open(TEMPLATE, encoding="utf-8").read()
    for literal in ("2,947", "6,410", "1,505", "2,040"):
        assert literal not in template, literal
