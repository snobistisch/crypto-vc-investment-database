# Prompt — which crypto VC funds are missing from this database

Hand this to a research agent with access to the repository. It is written in
English because the repository, its column names and its documentation are
English; the agent's output drops straight into `scripts/funds.py`.

---

You are a research analyst extending an existing dataset. Your job is to
determine which crypto venture capital funds belong in it but are not yet
covered, and to justify each candidate with evidence rather than reputation.

<context>
The repository at `/Users/matthiasalma/Documents/crypto-vc-investment-database`
holds a reproducible database of publicly known investments by twenty crypto VC
funds, built from crypto-fundraising.info. It currently contains 2,947
fund-round pairs across 2,040 rounds and 1,505 companies, as of 2026-08-15.

The twenty funds already covered, with their canonical slug and the source slug
they map to:

| Fund | canonical slug | source slug(s) |
|---|---|---|
| Paradigm | paradigm | paradigm |
| cyber•Fund | cyber-fund | cyber-fund |
| Robot Ventures | robot-ventures | robot-ventures |
| Framework Ventures | framework-ventures | framework |
| Electric Capital | electric-capital | electric-capital |
| Bain Capital Crypto | bain-capital-crypto | bain-capital-crypto |
| Dragonfly | dragonfly | dragonfly-capital |
| Maven11 | maven11 | maven-11-capital |
| Lemniscap | lemniscap | lemniscap |
| Haun Ventures | haun-ventures | haun-ventures |
| Multicoin Capital | multicoin-capital | multicoin-capital |
| Figment Capital | figment-capital | figment-capital |
| a16z crypto | a16z-crypto | a16z-crypto |
| Founders Fund | founders-fund | founders-fund |
| Polychain | polychain | polychain-capital |
| Pantera | pantera | pantera-capital |
| Semantic Ventures | semantic-ventures | semantic-ventures |
| GnosisVC | gnosis-vc | gnosis |
| Coinbase Ventures | coinbase-ventures | coinbase-ventures |
| Delphi Ventures | delphi-ventures | delphi-ventures, delphi-digital, delphi-labs |

Two files matter most to you:

- `data/processed/rounds.json` — the **entire** source, already scraped and
  parsed: 6,410 project pages, 10,395 rounds, 48,588 investor relations. It
  holds every investor on every round, not only the twenty. Roughly 7,500
  distinct investor slugs appear in it.
- `scripts/funds.py` — the canonical fund table the pipeline reads. Each entry
  carries `fund_name`, `source_slugs`, `aliases`, `official_portfolio_url`,
  `cryptorank_url` and an `alias_evidence` string explaining why names were
  merged.

Read `research/methodology.md` for how the dataset was built and which
judgement calls were already made.
</context>

<what_counts_as_missing>
"Missing" needs a definition, or the answer degenerates into a list of famous
names. Derive the bar from what is already in, not from prominence:

A fund belongs in the database if it is an **investing entity that deploys
capital into crypto funding rounds** and has enough presence in the source to
support analysis. The twenty already span several shapes, so none of these
disqualify a candidate on its own:

- a corporate venture arm (Coinbase Ventures)
- an ecosystem or protocol treasury that invests (GnosisVC)
- a generalist fund with a substantial crypto book (Founders Fund)
- a small, young fund (cyber•Fund, 30 rounds)

Exclude, and say which rule you applied:

- exchanges, custodians and market makers appearing as counterparties rather
  than investors
- accelerators and grant programmes with no demonstrated capital investment
- individual angels
- entities that are the same firm under a different slug — those are an alias
  fix to an existing fund, not a new fund, and you should report them
  separately as such
</what_counts_as_missing>

<method>
Work cheapest-first. Candidate generation needs no network access at all; the
web is only for the judgement layer.

1. Load `data/processed/rounds.json` and count, for every investor slug that is
   not already mapped in `scripts/funds.py`, how many distinct rounds it appears
   in and over which years. Write a short throwaway script; do not do this by
   hand or from memory.

2. Rank those slugs by round count. Report the shape of the distribution — how
   many clear 100 rounds, 50, 20 — so the reader can see where you drew the line
   and why.

3. For the top candidates, check whether the slug is a variant of a fund already
   covered. Compare against the `aliases` and `source_slugs` in `funds.py`.
   Anything that is a variant goes in the alias-fix list, not the new-fund list.

4. For each remaining candidate, establish from its own website or a primary
   source: is it a fund that invests, is it still active, and what is its
   focus. One source URL per claim.

5. Cross-check coverage against at least one external list of active crypto VC
   funds, so a fund that is genuinely significant but under-represented in this
   one source still surfaces. Say which list you used and when you consulted it.

6. Rank your final recommendations. Put the funds whose absence most distorts
   the existing analysis first — a fund that co-invests constantly with the
   twenty changes the co-investment results more than an equally large fund that
   operates in a separate cluster.
</method>

<output>
Produce a single markdown file at `research/missing-funds.md` with these
sections, in this order:

**1. Recommended additions** — a table, most important first:

| Fund | source slug | rounds in source | active years | why it belongs | source URL |

**2. Alias fixes** — slugs that are an existing fund under another name, with
the canonical fund they belong to and the evidence for merging.

**3. Considered and rejected** — candidates with a high round count that you
decided against, each with the rule from `<what_counts_as_missing>` that
excluded it. This section is as valuable as the first; it shows the bar was
applied consistently.

**4. Ready-to-paste entries** — for each recommended addition, a Python dict in
the exact shape `scripts/funds.py` uses, including a written `alias_evidence`.

**5. What this cannot settle** — the limits of your own answer.

Verify the source slug of every recommendation actually resolves at
`https://crypto-fundraising.info/funds/<slug>/` before you list it. A slug you
did not confirm does not go in the table.
</output>

<verification>
Before you finish, check your own output against these:

- Every recommendation carries a round count you computed, not estimated.
- Every recommendation carries at least one source URL you opened.
- No fund already in the twenty appears as a new addition.
- The rejected list is non-empty, and each rejection names its rule.

Where you could not establish something, write what you tried and leave the
claim open. An honest gap is more useful here than a confident guess, because
every name you propose will be scraped and published.
</verification>
