# Crypto VC Investment Database

Reproducible database of publicly known investments by twenty crypto venture
capital funds. One row per combination of fund and funding round, every row
traceable to a source URL.

> **Completeness.** Complete within the publicly accessible and named
> sources as of the cutoff date. Unannounced rounds, secondary transactions,
> liquid market positions, and investors that press releases lump under
> 'others' remain structurally invisible.

## Output

| File | Contents |
| --- | --- |
| `docs/index.html` | Interactive frontend: filterable explorer, fund profiles, co-investment network. Self-contained, no external requests |
| `outputs/vc-investments-full.xlsx` | All twenty funds. Ten sheets: README, Funds, Investments, Rounds, Portfolio Companies, Coverage, Sources, Conflicts, Unknown, Aliases |
| `outputs/vc-investments-full.csv` | Flat export of the `Investments` sheet |
| `outputs/per-fund/vc-investments-<fund>.xlsx` | Twenty files, one per fund, with the same sheets and columns |

The per-fund files are the same dataset with a fund filter, not a second
build: identical columns, identical formatting rules. Two things are
deliberately not filtered along:

- The **Rounds** sheet shows ALL investors in the same round, including funds
  outside that file. The rest of the cap table is exactly the interesting
  part.
- The **Coverage** sheet keeps the external control totals, so a standalone
  fund file also shows where it deviates.

Validation checks that the twenty fund files sum to the overview and that no
file contains a row belonging to another fund.

## The funds

Paradigm · cyber•Fund · Robot Ventures · Framework Ventures · Electric Capital ·
Bain Capital Crypto · Dragonfly · Maven11 · Lemniscap · Haun Ventures ·
Multicoin Capital · Figment Capital · a16z crypto · Founders Fund · Polychain ·
Pantera · Semantic Ventures · GnosisVC · Coinbase Ventures · Delphi Ventures

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
./.venv/bin/python scripts/build_frontend.py                     # 7
./.venv/bin/python scripts/validate_dataset.py                   # 8
./.venv/bin/python -m pytest tests -q                            # 9
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
7. Injects the dataset into `frontend/template.html` and writes
   `docs/index.html`. The payload is index-compressed: fund, investor,
   project and round-type strings are stored once and referenced by integer,
   which keeps the page under 1 MB despite carrying every row.
8. Validates the dataset and the workbook. Exits with code 1 on failure.

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
scripts/          import, scrape, normalisation, workbook, frontend, validation
frontend/         template.html — markup, styling and behaviour, no data
research/         methodology, source audit, coverage report
outputs/          xlsx and csv
docs/             index.html — the generated frontend, servable as GitHub Pages
tests/            parser, dataset and workbook tests
```

## Frontend

`docs/index.html` is one self-contained file. It embeds the full dataset, so
it opens from disk with no server and makes no external requests.

- **Explorer** — all 2,947 fund-round pairs. Filter by fund, round type,
  investment type, year, lead or participant, minimum round size, and whether
  a valuation is known. Free-text search covers project names, tickers, fund
  names and co-investors. Every column sorts; blanks always sink to the
  bottom rather than sorting as zero, because a blank is "not disclosed" and
  not the smallest deal. Clicking a row opens the full record with its
  source links.
- **Fund profiles** — twenty cards with companies, rounds, lead rate, median
  round, most common round types, and CryptoRank's count as a coverage
  contrast. Clicking a card filters the explorer.
- **Co-investment network** — a matrix and ranked list of how often two of
  the twenty funds appear in the same round. Labelled as co-occurrence:
  sharing a cap table is not evidence of a syndicate or of influence over
  the outcome.

To serve it locally:

```bash
python3 -m http.server 8931 --directory docs
```

## Licence

MIT for the scripts. The underlying factual data comes from third parties;
check their terms of use before redistributing the datasets further. The
HTML cache is deliberately not committed.

Not investment advice.
