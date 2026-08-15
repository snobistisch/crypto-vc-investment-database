"""Tests on the co-investment analysis.

The claims this analysis makes are statistical, so the tests target the places
a statistical claim can quietly go wrong: a null model that does not preserve
what it promises, a p-value floor the significance threshold cannot reach, and
a lift that disagrees with its own inputs.
"""

import json
import os
import random
import sys
from collections import Counter

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import analyze_coinvestment as co  # noqa: E402

RESULT = os.path.join(ROOT, "data", "processed", "coinvestment.json")


@pytest.fixture(scope="module")
def result():
    if not os.path.exists(RESULT):
        pytest.skip("coinvestment.json is missing; run analyze_coinvestment.py first")
    return json.load(open(RESULT))


# --------------------------------------------------------------------------
# the null model
# --------------------------------------------------------------------------

def build_toy():
    """A small bipartite graph: 4 funds over 6 rounds, all in one year."""
    rounds = [{0, 1}, {0, 2}, {1, 2}, {0, 3}, {1}, {2, 3}]
    fund_of_edge, round_of_edge = [], []
    for ri, members in enumerate(rounds):
        for f in sorted(members):
            fund_of_edge.append(f)
            round_of_edge.append(ri)
    edges = list(range(len(fund_of_edge)))
    edge_set = set(zip(fund_of_edge, round_of_edge))
    buckets = [edges]
    return rounds, edges, fund_of_edge, round_of_edge, edge_set, buckets


def test_permutation_preserves_both_degree_sequences():
    """Every fund keeps its round count and every round keeps its fund count.

    This is the whole justification for the null; if a swap leaked, the
    expected values would be measuring a different graph than the observed.
    """
    rounds, edges, fo, ro, es, buckets = build_toy()
    work = [set(m) for m in rounds]
    before_fund = Counter(fo)
    before_round = [len(m) for m in work]

    rng = random.Random(7)
    co.permute(edges, work, ro, fo, es, buckets, rng, 3000)

    assert Counter(fo) == before_fund
    assert [len(m) for m in work] == before_round


def test_permutation_keeps_the_graph_simple():
    """No round may end up holding the same fund twice."""
    rounds, edges, fo, ro, es, buckets = build_toy()
    work = [set(m) for m in rounds]
    rng = random.Random(11)
    co.permute(edges, work, ro, fo, es, buckets, rng, 3000)

    pairs = list(zip(fo, ro))
    assert len(pairs) == len(set(pairs))
    assert sum(len(m) for m in work) == len(pairs)


def test_permutation_actually_moves_something():
    rounds, edges, fo, ro, es, buckets = build_toy()
    work = [set(m) for m in rounds]
    rng = random.Random(3)
    moved = co.permute(edges, work, ro, fo, es, buckets, rng, 3000)
    assert moved > 0


def test_year_buckets_confine_swaps():
    """Edges in different years must never exchange funds.

    Without this, a fund could be shuffled into years it was never active in
    and its non-overlap with another fund would read as avoidance.
    """
    rounds = [{0, 1}, {2, 3}]
    fo = [0, 1, 2, 3]
    ro = [0, 0, 1, 1]
    es = set(zip(fo, ro))
    work = [set(m) for m in rounds]
    # each round sits in its own year, so each bucket has no swappable partner
    buckets = [[0, 1], [2, 3]]
    rng = random.Random(5)
    co.permute(list(range(4)), work, ro, fo, es, buckets, rng, 500)
    assert work[0] == {0, 1} and work[1] == {2, 3}


# --------------------------------------------------------------------------
# multiple testing
# --------------------------------------------------------------------------

def test_benjamini_hochberg_basics():
    assert co.benjamini_hochberg([]) == 0.0
    # nothing passes when every p is large
    assert co.benjamini_hochberg([0.9, 0.8, 0.7]) == 0.0
    # a single tiny p against few tests does pass
    assert co.benjamini_hochberg([0.001, 0.9, 0.9]) == 0.001


def test_sample_count_can_reach_the_correction_threshold():
    """The smallest reachable p must sit below the strictest BH rank.

    At 1000 samples the floor is 1/1001, which is above (1/190)*0.05 — no pair
    could ever be called significant regardless of how extreme it was. This
    test pins the relationship so a future reduction in SAMPLES fails loudly.
    """
    pairs = 190
    floor = 1.0 / (co.SAMPLES + 1)
    strictest = (1.0 / pairs) * co.FDR_ALPHA
    assert floor < strictest, (
        "SAMPLES=%d gives a p-value floor of %.5f, above the strictest BH rank "
        "of %.5f" % (co.SAMPLES, floor, strictest))


# --------------------------------------------------------------------------
# the produced result
# --------------------------------------------------------------------------

def test_every_pair_scored_once(result):
    n = len(result["funds"])
    assert len(result["pairs"]) == n * (n - 1) // 2
    keys = {(p["a"], p["b"]) for p in result["pairs"]}
    assert len(keys) == len(result["pairs"])
    for a, b in keys:
        assert a < b


def test_lift_matches_its_inputs(result):
    """Recomputing lift from the published shared/expected must reproduce it.

    Relative tolerance, because the absolute gap grows with the magnitude of
    the ratio and a pair at 7x would otherwise need impossible precision.
    """
    for p in result["pairs"]:
        if p["lift"] is None or not p["expected"]:
            continue
        recomputed = p["shared"] / p["expected"]
        assert abs(p["lift"] - recomputed) <= 0.005 * max(1.0, recomputed), p


def test_significance_flags_agree_with_direction(result):
    for p in result["pairs"]:
        if p["sig_more"]:
            assert p["lift"] > 1, p
        if p["sig_less"]:
            assert p["lift"] < 1, p
            assert p["expected"] >= result["method"]["min_expected_for_avoidance"], p


def test_no_zero_pvalues(result):
    """An empirical p can never honestly be zero with finite samples."""
    for p in result["pairs"]:
        assert p["p_more"] > 0 and p["p_less"] > 0


def test_permutation_null_beats_naive_calibration(result):
    """The median pair should land nearer chance under the permutation null.

    This is the measured reason the naive independence model was rejected; if
    it ever stops holding, the choice of null needs revisiting.
    """
    perm = result["totals"]["median_lift"]
    naive = result["totals"]["median_lift_naive"]
    assert abs(perm - 1.0) < abs(naive - 1.0), (perm, naive)


def test_profiles_cover_every_fund(result):
    assert len(result["profiles"]) == len(result["funds"])
    for p in result["profiles"]:
        assert p["rounds"] > 0
        assert 0 <= p["solo_rate"] <= 100
        assert p["solo_rounds"] <= p["rounds"]
        assert p["distinct_partners"] <= len(result["funds"]) - 1


def test_method_states_the_caveat(result):
    m = result["method"]
    assert "not collaboration" in m["caveat"]
    assert m["samples"] == co.SAMPLES
    assert "permutation" in m["null"] or "swap" in m["null"]
