# Crypto VC Investment Database

Reproducible database of publicly known investments by 59 crypto venture
capital funds. One row per combination of fund and funding round, every row
traceable to a source URL.

The database started at 20 funds (the brief) and was expanded to 59 using
[`research/missing-funds.md`](research/missing-funds.md) — a study of which
funds were absent from the round-level source but appeared repeatedly as
co-investors. Adding the 39 new funds needed no new scraping: they were
already present as investors on rounds the original scrape had captured, just
not yet mapped in `scripts/funds.py`.

> **Completeness.** Complete within the publicly accessible and named
> sources as of the cutoff date. Unannounced rounds, secondary transactions,
> liquid market positions, and investors that press releases lump under
> 'others' remain structurally invisible.

## Output

| File | Contents |
| --- | --- |
| `docs/index.html` | Interactive frontend: filterable explorer, fund profiles, co-investment network. Self-contained, no external requests |
| `outputs/vc-investments-full.xlsx` | All 59 funds. Ten sheets: README, Funds, Investments, Rounds, Portfolio Companies, Coverage, Sources, Conflicts, Unknown, Aliases |
| `outputs/vc-investments-full.csv` | Flat export of the `Investments` sheet |
| `outputs/per-fund/vc-investments-<fund>.xlsx` | 59 files, one per fund, with the same sheets and columns |

The per-fund files are the same dataset with a fund filter, not a second
build: identical columns, identical formatting rules. Two things are
deliberately not filtered along:

- The **Rounds** sheet shows ALL investors in the same round, including funds
  outside that file. The rest of the cap table is exactly the interesting
  part.
- The **Coverage** sheet keeps the external control totals, so a standalone
  fund file also shows where it deviates.

Validation checks that the fund files sum to the overview and that no file
contains a row belonging to another fund.

## The funds

**The original twenty:** Paradigm · cyber•Fund · Robot Ventures · Framework
Ventures · Electric Capital · Bain Capital Crypto · Dragonfly · Maven11 ·
Lemniscap · Haun Ventures · Multicoin Capital · Figment Capital · a16z crypto ·
Founders Fund · Polychain · Pantera · Semantic Ventures · GnosisVC · Coinbase
Ventures · Delphi Ventures

**Added from `research/missing-funds.md`:** Alameda Research · The Spartan
Group · Digital Currency Group · Animoca Brands · ParaFi Capital · Galaxy
Digital · Sequoia Capital · GSR · Blockchain Capital · Hashed · Solana
Ventures · Mechanism Capital · CoinFund · CMS Holdings · Alliance DAO · IOSG
Ventures · OKX Ventures · Circle Ventures · HashKey Capital · 1kx · Hack VC ·
Hypersphere · CMT Digital · Mirana Ventures · Arrington Capital · Jump Crypto ·
Amber Group · Polygon Ventures · HTX Ventures · Fenbushi Capital · Big Brain
Holdings · YZi Labs · SevenX Ventures · Sfermion · LongHash Ventures ·
Foresight Ventures · Borderless Capital · MH Ventures · Animoca Brands Japan

Full evidence, round counts and the funds that were considered and rejected
are in [`research/missing-funds.md`](research/missing-funds.md). Three of the
additions carry an explicit caveat in `scripts/funds.py`: GSR, CMS Holdings
and Amber Group are trading firms with low lead rates (6, 7 and 15 leads
across 194, 187 and 126 rounds), included on a stated venture line for GSR and
on source-observed investing behaviour for the other two, not on a verified
dedicated fund structure for any of the three. Alameda Research is included
deliberately despite being defunct since the FTX collapse in November
2022 — a database built to resist survivorship bias cannot omit the firms
that failed.

## Why the round is the unit, not the fund

The fund page on crypto-fundraising.info shows ten rounds. Measured on
Paradigm: exactly ten project links, while CryptoRank counts 121 investments
for the same fund. Pagination parameters redirect back to page one. On top of
that, funds remove written-off companies from their own portfolio page.
Whoever scrapes per fund measures the survivors.

The dataset was therefore built in a single pass over every project page,
after which the index was inverted to fund → investments. Official portfolio
pages and CryptoRank were used exclusively as a control list.

In depth: [`research/methodology.md`](research/methodology.md) and
[`research/source-audit.md`](research/source-audit.md).

## Pipeline

```bash
python -m venv .venv && ./.venv/bin/pip install -e .

./.venv/bin/python scripts/import-investment-dashboard-data.py   # 1
./.venv/bin/python scripts/fetch_crypto_fundraising.py           # 2
./.venv/bin/python scripts/fetch_coverage_controls.py            # 3
./.venv/bin/python scripts/normalize_funds.py                    # 4
./.venv/bin/python scripts/build_workbook.py                     # 5
./.venv/bin/python scripts/build_coverage_report.py              # 6
./.venv/bin/python scripts/analyze_coinvestment.py               # 7
./.venv/bin/python scripts/build_frontend.py                     # 8
./.venv/bin/python scripts/validate_dataset.py                   # 9
./.venv/bin/python -m pytest tests -q                            # 10
```

1. Reads reusable data from the existing investment dashboard and records a
   manifest with a SHA-256 per source file.
2. Fetches every project page and parses the investors per round. Pages are
   gzip-cached in `data/raw/`, outside Git; a repeat run only fetches the
   missing pages.
3. Fetches per-fund control totals from the aggregators and the official
   portfolio pages.
4. Inverts the index to fund-round pairs and builds the alias table.
5. Builds the Excel file and the CSV entirely from the dataset.
6. Generates `research/coverage-report.md` from the dataset — no typed-in
   figures.
7. Scores every fund pair on how often they share a round against a
   permutation null. See *Who co-invests with whom* below.
8. Injects the dataset into `frontend/template.html` and writes
   `docs/index.html`. The payload is index-compressed: fund, investor,
   project and round-type strings are stored once and referenced by integer,
   which keeps the page under 1 MB despite carrying every row.
9. Validates the dataset and the workbook. Exits with code 1 on failure.

Step 2 takes roughly an hour: the source rate-limits to about one and a half
requests per second and responds with HTTP 429 at higher concurrency. The
scrape runs on four workers with backoff.

## Field meaning

Three amount fields that often get mixed up:

- `round_size_usd` — size of the whole round.
- `fund_ticket_usd` — what this fund itself put in. Almost always blank: none
  of the sources used publish this. It is not filled in with the round size.
- `valuation_usd` — valuation of the round, with `valuation_type` next to it.
  Never a current token FDV.

A missing value is a blank cell. Not zero, not `null`, not estimated. The
source uses `0` and `TBD` for unknown; both are converted to blank.

Allowed categories:

```text
fund_role            lead | co-lead | participant | incubator | unknown
investment_type      equity | token | SAFT | public_sale | strategic | incubated | unknown
verification_status  verified_primary | verified_two_sources | verified_aggregator_only
                     single_source | conflict | uncertain
confidence           high | medium | low
valuation_type       pre_money | post_money | FDV | enterprise_value | unknown
```

`verified_two_sources` does not occur in the generated data. The scripts do
not themselves establish a second independent primary source, and a status
handed out automatically is not verification.

## Relationship to the investment dashboard

`/Users/matthiasalma/Documents/Investeringsdashboard` was used exclusively as
a read source. No file there was changed, no branch was created, and nothing
was committed. The 153 previously scraped fund-round pairs were not blindly
merged in but used as a cross-check; deviations are on the `Conflicts` sheet
and are not smoothed over.

`data/imported/source-manifest.json` records the source repository, Git
commit, import date, SHA-256 per source file, and parser warnings.

## Repository structure

```text
data/imported/    imported dashboard data and the source manifest
data/raw/         gzip cache of fetched pages (not in Git)
data/processed/   round universe, normalised dataset, control totals
scripts/          import, scrape, normalisation, workbook, analysis, frontend, validation
frontend/         template.html — markup, styling and behaviour, no data
research/         methodology, source audit, coverage report
outputs/          xlsx and csv
docs/             index.html — the generated frontend, servable as GitHub Pages
tests/            parser, dataset and workbook tests
```

## Frontend

`docs/index.html` is one self-contained file. It embeds the full dataset, so
it opens from disk with no server and makes no external requests.

- **Explorer** — all fund-round pairs. Filter by fund, round type, investment
  type, year, lead or participant, minimum round size, and whether a
  valuation is known. Free-text search covers project names, tickers, fund
  names and co-investors. Every column sorts; blanks always sink to the
  bottom rather than sorting as zero, because a blank is "not disclosed" and
  not the smallest deal. Clicking a row opens the full record with its
  source links.
- **Fund profiles** — one card per fund with companies, rounds, lead rate,
  median round, most common round types, and CryptoRank's count as a
  coverage contrast. Clicking a card filters the explorer.
- **Co-investment charts** — four views of which funds cluster and which do
  not. See below.

To serve it locally:

```bash
python3 -m http.server 8931 --directory docs
```

## Who co-invests with whom

`scripts/analyze_coinvestment.py` scores every fund pair — 1,711 of them at
59 funds. Counting shared rounds on its own answers the wrong question:
Coinbase Ventures is in 497 rounds, so it pairs with everyone often, and a
ranking by raw count is close to a ranking of portfolio size. Measured: of
the ten pairs sharing the most rounds and the ten with the strongest
affinity, **only one pair appears on both lists.**

**The null model.** The obvious null — expected = (rounds_a x rounds_b) / N —
is not rejected because its numbers look wrong; it is rejected because a
closed-form formula produces one point estimate, not a distribution, so
there is no null to draw a p-value from. (Its median lift here is 0.88,
close to the permutation null's 0.85 — that near-agreement is itself only
true at this fund count; at the original 20 funds the naive median was 0.55
against the permutation null's 0.89. Proximity to 1 was never the argument
for either model; it just happened to be a stark illustration at n=20.)

Instead the script shuffles fund-round memberships by repeated edge swaps that
hold three things fixed:

- every fund keeps its own number of rounds;
- every round keeps its own number of these 59 funds;
- swaps stay within a calendar year, so each fund's active window survives —
  without this, a fund active only 2018–2025 could be shuffled into another's
  2023–2026 rounds and their non-overlap would read as avoidance when it is
  only vintage.

`lift` is observed / expected under this null; 1.0 is exactly chance.

**Significance.** p-values are empirical, corrected with Benjamini-Hochberg
at a 5% FDR across all 1,711 pairs. The sample count is derived from the
correction, not fixed by taste: it scales as roughly `3 × pairs / FDR_ALPHA`,
which is why 20 funds needed 10,000 permutations and 59 funds needed
102,660 — enough that the smallest reachable p-value still clears the
strictest Benjamini-Hochberg rank. A test pins this relationship so a future
change that under-samples fails loudly instead of silently returning "not
significant" for everything.

**Result.** 63 pairs co-invest significantly more than chance, 23
significantly less. The strongest is **Animoca Brands + Animoca Brands
Japan at 7.7x** (104 shared rounds against 13.5 expected) — the two entities
`research/missing-funds.md` flagged as a judgement call on whether to merge;
this result is evidence toward treating them as the same investment decision
rather than independent ones, though the database still lists them
separately, on the reasoning recorded in `scripts/funds.py`. Robot Ventures +
Figment Capital (6.1x) and Robot Ventures + Bain Capital Crypto (6.0x)
follow. On the other side, six pairs — including Paradigm + The Spartan
Group and a16z crypto + The Spartan Group — share exactly zero rounds
against 7–14 expected.

**What it cannot say.** Co-occurrence is not collaboration. Two funds in one
cap table may never have spoken. The null holds size and vintage fixed but
cannot hold stage, sector or geography, so a pair below chance may simply be
writing different cheques rather than avoiding each other.

## Licence

MIT for the scripts. The underlying factual data comes from third parties;
check their terms of use before redistributing the datasets further. The
HTML cache is deliberately not committed.

Not investment advice.
