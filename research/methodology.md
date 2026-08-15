# Methodology

## The choice that determines everything: the round is the unit, not the fund

Fund pages are the obvious entry point and the wrong one. Two measured
properties make them unsuitable as a primary source:

1. **Display limit.** The fund page on crypto-fundraising.info shows ten
   rounds. Measured on `https://crypto-fundraising.info/funds/paradigm/`:
   exactly ten unique project links, while CryptoRank counts 121 investments
   for the same fund. Pagination parameters redirect back to page one.
2. **Survivorship bias.** A fund that maintains its own portfolio page has no
   reason to keep written-off companies listed. The same bias sits in the
   public CryptoRank view, which shows ten liquid names.

Both effects point the same way: scraping per fund measures the winners and
calls that a portfolio.

The dataset was therefore built in a single pass over **all 6,411 project
pages**. All investors were parsed per round; the index was then inverted to
fund → investments. A fund appears in this dataset because it was in a round,
not because it put itself on a list.

## Two representations per page, checked against each other

Every project page carries the same rounds twice, in different form. The
parser reads both and merges them.

| | JSON-LD `funding[]` | HTML `newrisedblock` |
| --- | --- | --- |
| Round date | exact, `startDate: 2024-04-09` | month only, `Raised Apr 2024` |
| Round type | `name`, sometimes `Unknown` | `roundtype`, missing more often |
| Amount | `amount.value` | `abbrusd` |
| Valuation | — | `roundvalua` |
| Lead vs. participant | — | `Lead Investors` / `Investors` |
| Original source | — | `raisedinlink` → press release |

The two lists are in the same order, newest first, and are aligned by index.
The alignment is checked: the exact date from JSON-LD is only used when month
and year match the HTML label. On a mismatch, the date falls back to the
first of the month and `date_precision` is set to `month` with a warning
recorded.

Lead assignment happens by position: every investor link gets the role of the
nearest preceding heading. That is more robust than cutting on nested `div`
blocks, which are not consistently closed in the source.

## What counts as an investment

Included: equity rounds, pre-seed through late stage, strategic investments,
announced token and SAFT investments, public token sales with demonstrable
participation, follow-on financing, and incubations with demonstrable
capital.

Not included: grants, accelerator participation without investment,
partnerships, market making, ecosystem incentives, tokens bought only on the
open market, and advisory roles. Round types listed as a grant or airdrop in
the source get `verification_status = uncertain` with the reason in `notes`;
they are not silently removed and not presented as a confirmed investment.

## Amounts: three fields that are not the same

`round_size_usd` is the size of the whole round. `fund_ticket_usd` is what the
fund itself put in. `valuation_usd` is the valuation of the round, with
`valuation_type` next to it.

`fund_ticket_usd` is blank almost everywhere in this dataset, and that is the
correct outcome: none of the sources used publish what an individual fund put
into a round. Copying the round size into that field would produce a number
that looks right and is wrong.

`valuation_usd` is never filled in with a current token FDV. A valuation from
2021 and today's market cap are different quantities.

## Missing values

A missing value is a blank cell. Not zero, not `null`, not estimated. The
source uses `0` and `TBD` for unknown; the parser converts both to blank.
Every row with a missing field is on the `Unknown` sheet with what was
attempted.

## Aliases

Fund names were merged on the basis of the source slug, not name similarity.
Every merge is recorded in `scripts/funds.py` with a reason, and that reason
is also on the `Aliases` sheet. Three decisions are worth calling out:

- **Bain Capital Ventures was not merged with Bain Capital Crypto.** The
  source carries two funds; they are two funds with separate mandates.
- **Figment (staking operator) was not merged with Figment Capital.**
- **Delphi Ventures, Delphi Digital and Delphi Labs WERE merged.** The three
  names are used interchangeably in fundraising sources for the same
  cap-table rows. `fund_name_in_source` keeps visible which name was there,
  so the merge is reversible.

## Verification status

`verified_primary` means the aggregator page carries a Details link to the
original announcement or press release and that link was recorded.
`verified_aggregator_only` means only the aggregator page confirms the round.
`verified_two_sources` is never assigned by the scripts — the script does not
itself establish a second independent primary source, and a status handed out
automatically is not verification.

## Measuring coverage instead of claiming it

Four numbers sit side by side per fund on the `Coverage` sheet: the own
count, the aggregator's fund page, the official portfolio page, and
CryptoRank's count. Where a source is not readable — client-side rendered
portfolio pages, RootData without a key — that is recorded as such, with a
blank cell instead of an estimate.

This file carries no overall coverage percentage. A percentage presupposes a
known denominator, and the denominator is exactly what is not known.

## Completeness

> Complete within the publicly accessible and named sources as of the
> cutoff date. Unannounced rounds, secondary transactions, liquid market
> positions, and investors that press releases lump under 'others' remain
> structurally invisible.

Not investment advice.
