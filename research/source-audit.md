# Source Audit

What was tested, what worked, and what did not. Status codes are outcomes of
actual requests as of the cutoff date, not assumptions.

## Structured APIs

| Source | Endpoint | Outcome |
| --- | --- | --- |
| crypto-fundraising.info | `/wp-json/wp/v2/projects` | **200**, `x-wp-total: 6411`, 65 pages — open and enumerable |
| crypto-fundraising.info | `/wp-json/wp/v2/funds` | **200**, searchable by name; used to verify source slugs |
| crypto-fundraising.info | ACF relation fields via REST | `acf` comes back blank; the relation IS in the rendered HTML |
| CryptoRank | `__NEXT_DATA__` on the fund page | **200**, contains `investments` — CryptoRank's own count |
| RootData | public portfolio page | no count derivable without a key or JavaScript |
| DefiLlama Raises | `api.llama.fi/raises` | paid since 2026 (established in the earlier dashboard research) |
| Crunchbase, CB Insights, PitchBook | — | key or enterprise contract required |

## robots.txt and rate limiting

`https://crypto-fundraising.info/robots.txt` contains `User-agent: *` with
`Disallow:` — no path excluded, plus a sitemap reference.

The site does rate-limit on speed, though. At nine concurrent connections,
**HTTP 429** responses came back; throughput stayed stuck around one and a
half requests per second. The scrape therefore runs on four workers with a
pause per request and six attempts with exponential backoff. A page that does
not come in after six attempts is registered as failed and not processed as
blank.

Every page is gzip-cached in `data/raw/`, outside Git. A repeat run therefore
makes no redundant request at all and only fetches the missing pages.

## The fund page as a control list

Measured on `https://crypto-fundraising.info/funds/paradigm/`: ten unique
project links. CryptoRank counts 121 investments for the same fund. The
difference is not a data error but a display limit, and it is the reason this
dataset was not built per fund.

The same limitation applies to the public CryptoRank portfolio list, which
shows ten rows. The `investments` field in `__NEXT_DATA__` IS a total,
though, and was used as a control figure — not as a source of individual
rounds.

## Official portfolio pages

Of the 59 funds, 7 serve a portfolio list in static HTML that this script's
domain-counting heuristic could read. The rest render client-side; there a
blank cell with the reason is recorded.
Where a list is readable, the number of unique outbound domains was counted
as an approximation of the number of portfolio names. That is an
approximation and is noted as such in the column note.

A fund's portfolio page is a control list either way, not a primary source:
funds remove written-off companies.

## Reuse from the investment dashboard

153 fund-round pairs were carried over from `SOURCE_REPOSITORY` (Haun
Ventures and Paradigm, scraped on 13 August 2026), plus five token
measurements and the CryptoRank slice counts per fund. Those 153 rows were
not blindly merged in but used as a **cross-check**: where lead status or
round size deviates from the current source page, the difference is on the
`Conflicts` sheet and is not smoothed over.

`data/imported/source-manifest.json` records the source repository, the Git
commit, the import date, a SHA-256 per source file, and the parser warnings.

The source repository was read only. No file there was changed, no branch
was created, and nothing was committed.

## Known limitations of the source

1. Press releases name the lead and "others"; the "others" drop out and
   appear in no database.
2. Unannounced pre-seed rounds do not exist in public sources.
3. Secondary purchases and SAFT takeovers make a fund invisible as an
   investor anywhere.
4. Some rounds carry no round type in the source; that cell stays blank.
5. Where the source gives only month and year, the date is set to the first
   of the month with `date_precision = month`.

Not investment advice.
