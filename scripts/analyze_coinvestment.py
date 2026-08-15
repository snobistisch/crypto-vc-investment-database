#!/usr/bin/env python3
"""Measures which funds co-invest more, or less, than chance.

Raw shared-round counts answer the wrong question. Coinbase Ventures sits in
497 rounds, so it pairs with everyone often; a small fund pairs with nobody
often. Ranking on the raw count re-ranks portfolio size and calls it a
relationship.

## The null model, and why the obvious one is wrong

The obvious null is independence: expected = (rounds_a x rounds_b) / N. Its
median lift can land anywhere depending on how much of the round universe is
multi-fund at the current fund count — sometimes far from 1, sometimes close
to it by coincidence. That is not the reason it is rejected. A closed-form
formula produces one number, not a distribution, so it has no way to say how
surprising an observed count is; there is no p-value to compute from it. The
real problem is structural: rounds cannot absorb co-occurrence the way
independent draws assume, and turning the formula's output into a p-value
would require pretending otherwise.

This script uses a **degree-preserving permutation null** instead. Fund-round
memberships are shuffled by repeated edge swaps that hold two things fixed:

  - every fund keeps exactly its own number of rounds;
  - every round keeps exactly its own number of these funds.

Swaps are further restricted to rounds **within the same calendar year**, so a
fund's activity window is preserved too. Without that, a fund active only in
2018-2025 could be shuffled into another's 2023-2026 rounds and their
non-overlap would read as avoidance when it is only vintage.

Expected co-occurrence is then the mean across permutation samples, and the
p-value is empirical: the share of samples at least as extreme as observed.
p-values are corrected with Benjamini-Hochberg FDR across every pair tested —
without it, some pairs would look significant by chance alone.

## What this still cannot say

Co-occurrence is not collaboration. Two funds in one cap table may never have
spoken. A low score can reflect stage, sector or geography rather than any
decision to stay apart. Every label in the output says co-occurrence.

Input   data/processed/dataset.json
Output  data/processed/coinvestment.json
"""

import json
import math
import os
import random
import sys
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import FUNDS  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(PROCESSED, "coinvestment.json")

N_PAIRS = len(FUNDS) * (len(FUNDS) - 1) // 2

# Sample count is set by the resolution the test needs, not by taste, and it
# scales with how many pairs are being tested. The smallest empirical p
# reachable is 1/(SAMPLES+1); Benjamini-Hochberg over N_PAIRS pairs requires a
# p at or below (1/N_PAIRS) x FDR_ALPHA for anything to clear the strictest
# rank. SAFETY_MARGIN below sets how far under that threshold the floor sits —
# at 20 funds (190 pairs) this formula gives roughly the same 10,000 samples
# that were hand-picked and verified for that case; at 59 funds (1,711 pairs)
# it scales up automatically so the test does not silently lose the power to
# ever call anything significant.
FDR_ALPHA = 0.05
SAFETY_MARGIN = 3
SAMPLES = max(2000, math.ceil(SAFETY_MARGIN * N_PAIRS / FDR_ALPHA))
BURN_IN_MULT = 10       # swap attempts per edge before the first sample
THIN_MULT = 1           # swap attempts per edge between samples
SEED = 20260815         # fixed so the published figures are reproducible

# A pair needs this much expected co-occurrence before a low count can mean
# anything. Below it, "they never co-invest" is indistinguishable from "they
# were never both likely to appear anyway".
MIN_EXPECTED_FOR_AVOIDANCE = 3.0


def benjamini_hochberg(pvalues, alpha=FDR_ALPHA):
    """Largest p-value that survives BH at the given FDR, or 0.0 if none."""
    if not pvalues:
        return 0.0
    ordered = sorted(pvalues)
    m = len(ordered)
    threshold = 0.0
    for i, p in enumerate(ordered, start=1):
        if p <= (i / m) * alpha:
            threshold = p
    return threshold


def pair_key(a, b):
    return (a, b) if a < b else (b, a)


def count_pairs(round_members, into):
    """Adds every within-round fund pair into a counter."""
    for members in round_members:
        n = len(members)
        if n < 2:
            continue
        m = sorted(members)
        for i in range(n):
            for j in range(i + 1, n):
                into[(m[i], m[j])] += 1


def permute(edges, round_members, round_of_edge, fund_of_edge, edge_set,
            year_buckets, rng, attempts):
    """Degree-preserving double-edge swaps, restricted to same-year rounds.

    Picks two edges whose rounds fall in the same calendar year and exchanges
    their funds. Rejects a swap that would duplicate an existing membership,
    which keeps the bipartite graph simple and both degree sequences exact.
    """
    done = 0
    for _ in range(attempts):
        bucket = year_buckets[rng.randrange(len(year_buckets))]
        if len(bucket) < 2:
            continue
        e1 = bucket[rng.randrange(len(bucket))]
        e2 = bucket[rng.randrange(len(bucket))]
        if e1 == e2:
            continue
        f1, r1 = fund_of_edge[e1], round_of_edge[e1]
        f2, r2 = fund_of_edge[e2], round_of_edge[e2]
        if f1 == f2 or r1 == r2:
            continue
        if (f1, r2) in edge_set or (f2, r1) in edge_set:
            continue
        edge_set.discard((f1, r1))
        edge_set.discard((f2, r2))
        edge_set.add((f1, r2))
        edge_set.add((f2, r1))
        round_members[r1].discard(f1)
        round_members[r1].add(f2)
        round_members[r2].discard(f2)
        round_members[r2].add(f1)
        fund_of_edge[e1], fund_of_edge[e2] = f1, f2
        round_of_edge[e1], round_of_edge[e2] = r2, r1
        done += 1
    return done


def main():
    ds = json.load(open(os.path.join(PROCESSED, "dataset.json")))
    rng = random.Random(SEED)

    slugs = [f["fund_slug"] for f in ds["funds"]]
    names = {f["fund_slug"]: f["fund_name"] for f in ds["funds"]}
    idx = {s: i for i, s in enumerate(slugs)}

    # ---- observed structure ---------------------------------------------
    rounds, years = [], []
    for r in ds["rounds"]:
        sel = {idx[s.strip()] for s in (r.get("selected_funds") or "").split(",")
               if s.strip() and s.strip() in idx}
        if not sel:
            continue
        rounds.append(set(sel))
        years.append((r.get("round_date") or "")[:4] or "unknown")

    observed = Counter()
    count_pairs(rounds, observed)

    rounds_by_fund = Counter()
    years_by_fund = defaultdict(set)
    solo = Counter()
    for members, year in zip(rounds, years):
        for f in members:
            rounds_by_fund[f] += 1
            years_by_fund[f].add(year)
        if len(members) == 1:
            solo[next(iter(members))] += 1

    partners = defaultdict(Counter)
    for members in rounds:
        m = sorted(members)
        for i in range(len(m)):
            for j in range(len(m)):
                if i != j:
                    partners[m[i]][m[j]] += 1

    # naive independence expectation, kept only to show it is the wrong null
    N = len(rounds)
    naive = {}
    for i in range(len(slugs)):
        for j in range(i + 1, len(slugs)):
            naive[(i, j)] = rounds_by_fund[i] * rounds_by_fund[j] / N if N else 0.0

    # ---- permutation null -----------------------------------------------
    edges, fund_of_edge, round_of_edge = [], [], []
    for ri, members in enumerate(rounds):
        for f in members:
            edges.append(len(edges))
            fund_of_edge.append(f)
            round_of_edge.append(ri)
    edge_set = set(zip(fund_of_edge, round_of_edge))
    E = len(edges)

    buckets = defaultdict(list)
    for e in range(E):
        buckets[years[round_of_edge[e]]].append(e)
    year_buckets = [b for b in buckets.values() if len(b) >= 2]

    work = [set(m) for m in rounds]
    fo, ro = list(fund_of_edge), list(round_of_edge)
    es = set(edge_set)

    sys.stderr.write("  burn-in (%d swap attempts) ...\n" % (E * BURN_IN_MULT))
    permute(edges, work, ro, fo, es, year_buckets, rng, E * BURN_IN_MULT)

    totals = Counter()
    at_least = Counter()
    at_most = Counter()
    for s in range(SAMPLES):
        permute(edges, work, ro, fo, es, year_buckets, rng, E * THIN_MULT)
        sample = Counter()
        count_pairs(work, sample)
        for key in naive:
            v = sample.get(key, 0)
            totals[key] += v
            o = observed.get(key, 0)
            if v >= o:
                at_least[key] += 1
            if v <= o:
                at_most[key] += 1
        if (s + 1) % 200 == 0:
            sys.stderr.write("  sample %d/%d\n" % (s + 1, SAMPLES))

    # ---- assemble pairs --------------------------------------------------
    raw = []
    for (i, j) in sorted(naive):
        o = observed.get((i, j), 0)
        exp = totals[(i, j)] / SAMPLES
        # +1 smoothing: an empirical p can never honestly be 0 with finite samples
        p_more = (at_least[(i, j)] + 1) / (SAMPLES + 1)
        p_less = (at_most[(i, j)] + 1) / (SAMPLES + 1)
        union = rounds_by_fund[i] + rounds_by_fund[j] - o
        raw.append({
            "a": i, "b": j,
            "shared": o,
            # Four decimals, not two: a reader recomputing lift from the
            # published expected value must land on the published lift. At two
            # decimals a pair with expected 0.26 reproduced 7.69 against a
            # stored 7.73.
            "expected": round(exp, 4),
            "expected_naive": round(naive[(i, j)], 4),
            "lift": round(o / exp, 3) if exp > 0 else None,
            "jaccard": round(o / union, 4) if union else 0.0,
            "a_rounds": rounds_by_fund[i],
            "b_rounds": rounds_by_fund[j],
            "p_more": round(p_more, 5),
            "p_less": round(p_less, 5),
            "window_from": min(years_by_fund[i] | years_by_fund[j]) if (years_by_fund[i] or years_by_fund[j]) else "",
            "window_to": max(years_by_fund[i] | years_by_fund[j]) if (years_by_fund[i] or years_by_fund[j]) else "",
            "reason": "",
        })

    more_cut = benjamini_hochberg([e["p_more"] for e in raw])
    less_cut = benjamini_hochberg([e["p_less"] for e in raw])
    for e in raw:
        e["sig_more"] = bool(e["p_more"] <= more_cut and e["lift"] and e["lift"] > 1)
        e["sig_less"] = bool(e["p_less"] <= less_cut and e["expected"] >= MIN_EXPECTED_FOR_AVOIDANCE
                             and e["lift"] is not None and e["lift"] < 1)
        if e["expected"] < MIN_EXPECTED_FOR_AVOIDANCE:
            e["reason"] = ("too little expected overlap to read a low count as "
                           "avoidance (expected %.1f)" % e["expected"])

    scored = [e for e in raw if e["lift"] is not None]
    together = sorted([e for e in scored if e["sig_more"]], key=lambda e: -e["lift"])
    apart = sorted([e for e in scored if e["sig_less"]], key=lambda e: e["lift"])

    # ---- per-fund profile ------------------------------------------------
    lift_by_fund = defaultdict(list)
    for e in scored:
        lift_by_fund[e["a"]].append(e["lift"])
        lift_by_fund[e["b"]].append(e["lift"])

    profiles = []
    for i, s in enumerate(slugs):
        p = partners[i]
        total_pairings = sum(p.values())
        top = p.most_common(1)
        lifts = sorted(lift_by_fund[i])
        yrs = sorted(years_by_fund[i])
        profiles.append({
            "slug": s, "name": names[s],
            "rounds": rounds_by_fund[i],
            "solo_rounds": solo[i],
            "solo_rate": round(100.0 * solo[i] / rounds_by_fund[i]) if rounds_by_fund[i] else 0,
            "distinct_partners": len(p),
            "pairings": total_pairings,
            "top_partner": names[slugs[top[0][0]]] if top else "",
            "top_partner_rounds": top[0][1] if top else 0,
            "top_partner_share": round(100.0 * top[0][1] / total_pairings) if total_pairings and top else 0,
            "median_lift": round(lifts[len(lifts) // 2], 3) if lifts else None,
            "sig_more_count": sum(1 for e in together if i in (e["a"], e["b"])),
            "sig_less_count": sum(1 for e in apart if i in (e["a"], e["b"])),
            "first_year": yrs[0] if yrs else "",
            "last_year": yrs[-1] if yrs else "",
        })

    lifts_all = sorted(e["lift"] for e in scored)
    naive_lifts = sorted((e["shared"] / e["expected_naive"]) for e in scored if e["expected_naive"] > 0)

    payload = {
        "generated_at": date.today().isoformat(),
        "cutoff": ds["source_consulted_date"],
        "method": {
            "unit": "round containing at least one of the %d funds" % len(slugs),
            "null": ("degree-preserving edge-swap permutation, restricted to rounds in the "
                     "same calendar year; every fund keeps its round count, every round "
                     "keeps its number of these %d funds, and activity windows are held" % len(slugs)),
            "samples": SAMPLES,
            "seed": SEED,
            "lift": "observed shared rounds / mean shared rounds across permutations; 1.0 is chance",
            "significance": "empirical p from the permutations, Benjamini-Hochberg FDR at %.2f" % FDR_ALPHA,
            "min_expected_for_avoidance": MIN_EXPECTED_FOR_AVOIDANCE,
            "why_not_independence": (
                "Independence expects (rounds_a x rounds_b)/N. Its median lift here is %.2f, "
                "against %.2f under the permutation null — sometimes close to that null's "
                "median, sometimes not, depending on how much of the round universe is "
                "multi-fund at the current fund count. That closeness is not why independence "
                "is rejected: a point-estimate formula has no null distribution to draw a "
                "p-value from at all. The permutation null does, because it builds an actual "
                "constrained sample space that respects each fund's true round count, each "
                "round's true fund count, and each fund's active years — which is what makes "
                "any of the p-values in this file valid, regardless of where the two medians "
                "happen to land." % (
                    naive_lifts[len(naive_lifts)//2] if naive_lifts else 0,
                    lifts_all[len(lifts_all)//2] if lifts_all else 0)),
            "caveat": ("Co-occurrence is not collaboration. Two funds in one cap table may "
                       "never have spoken, and a low score can reflect stage, sector or "
                       "geography rather than any decision to stay apart."),
        },
        "totals": {
            "funds": len(slugs),
            "rounds_scored": len(rounds),
            "multi_fund_rounds": sum(1 for m in rounds if len(m) > 1),
            "pairs": len(raw),
            "significant_together": len(together),
            "significant_apart": len(apart),
            "fdr_threshold_more": round(more_cut, 5),
            "fdr_threshold_less": round(less_cut, 5),
            "median_lift": round(lifts_all[len(lifts_all)//2], 3) if lifts_all else None,
            "median_lift_naive": round(naive_lifts[len(naive_lifts)//2], 3) if naive_lifts else None,
        },
        "funds": [{"slug": s, "name": names[s]} for s in slugs],
        "pairs": raw,
        "together": together[:25],
        "apart": apart[:25],
        "profiles": profiles,
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)

    print("Written: %s" % OUT)
    print("  %d pairs, %d rounds, %d with more than one selected fund"
          % (len(raw), len(rounds), payload["totals"]["multi_fund_rounds"]))
    print("  median lift %.2f under the permutation null, %.2f under naive independence"
          % (payload["totals"]["median_lift"], payload["totals"]["median_lift_naive"]))
    print("  %d pairs co-invest significantly more than chance, %d significantly less"
          % (len(together), len(apart)))
    print()
    print("  Together more than chance:")
    for e in together[:8]:
        print("    %-21s + %-21s lift %5.2f  (%d shared, %.1f expected, p=%.4f)"
              % (names[slugs[e["a"]]], names[slugs[e["b"]]], e["lift"],
                 e["shared"], e["expected"], e["p_more"]))
    print()
    print("  Apart more than chance:")
    for e in apart[:8]:
        print("    %-21s + %-21s lift %5.2f  (%d shared, %.1f expected, p=%.4f)"
              % (names[slugs[e["a"]]], names[slugs[e["b"]]], e["lift"],
                 e["shared"], e["expected"], e["p_less"]))


if __name__ == "__main__":
    main()
