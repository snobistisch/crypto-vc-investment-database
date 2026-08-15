# Which crypto VC funds are missing from this database

**Consulted:** 2026-08-15 · **Source universe:** `data/processed/rounds.json`
(6,410 projects, 10,395 rounds, 48,588 investor relations, scraped 2026-08-15)

**Status:** the Tier 1 recommendations below (38 funds) plus Animoca Brands
Japan were added to `scripts/funds.py` on 2026-08-15, taking the database
from 20 to 59 funds. Tier 2 and the individuals in "Considered and rejected"
were not added.

**Follow-up finding on the Animoca Brands / Animoca Brands Japan question
below:** after adding both as separate entries, `analyze_coinvestment.py`
measured them as the single strongest pair in the whole 59-fund set — 104
shared rounds against 13.5 expected under the permutation null, lift 7.7x,
the highest of any pair including ones with far more raw overlap. That is
evidence toward the two moving as one investment decision rather than two
independent ones, which sharpens the merge question this report left open
below rather than closing it — the database still lists them separately.

## How the candidates were found

Candidate generation needed no network access. `rounds.json` already holds
every investor on every round in the source, not only the twenty. Counting
distinct rounds per investor slug and removing everything already mapped in
`scripts/funds.py` gives **7,556 candidate slugs**.

The scale of what the current selection leaves out:

| | |
| --- | ---: |
| Investor slots across the whole source | 48,588 |
| Held by the current twenty | 2,947 (6.1%) |
| Held by everyone else | 45,641 (93.9%) |
| Rounds in the source | 10,395 |
| Rounds containing at least one of the twenty | 2,040 (19.6%) |

**Distribution of the 7,556 candidates by round count:**

| Rounds in source | Slugs |
| ---: | ---: |
| ≥ 300 | 1 |
| ≥ 200 | 9 |
| ≥ 150 | 19 |
| ≥ 100 | 59 |
| ≥ 50 | 162 |
| ≥ 20 | 469 |
| ≥ 10 | 919 |

**The line is drawn at 100 rounds** — 59 slugs. That is the point where the
count stops being an accident of a busy year: every slug above it is active
across at least four calendar years. Adding all 59 would take coverage from
2,040 to 5,106 rounds, a 150% increase, because 3,066 rounds in the source
contain one of them and none of the current twenty.

Applying the exclusion rules to those 59 leaves **54 recommended additions**,
of which 27 are unambiguous crypto VC funds and the rest need a stated
decision on shape.

---

## 1. Recommended additions

Ordered by how much each one's absence distorts the existing analysis:
`shared` counts rounds the candidate already shares with one of the twenty, so
a high number means the current co-investment results are drawn with that fund
silently deleted from the cap table.

### Tier 1 — highest distortion, unambiguous investors

| Fund | source slug | rounds | lead | shared | active | why it belongs | source |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Alameda Research | `alameda-research` | 207 | 27 | 109 | 2020–2022 | Collapsed with FTX in Nov 2022; its 207 rounds are exactly the kind of record a survivorship-safe database exists to keep | [fund page](https://crypto-fundraising.info/funds/alameda-research/) |
| The Spartan Group | `the-spartan-group` | 235 | 39 | 103 | 2018–2026 | Crypto VC and advisory; CryptoRank tier 1 with 233 portfolio companies | [CryptoRank](https://cryptorank.io/funds) |
| Digital Currency Group | `digital-currency-group` | 284 | 26 | 101 | 2013–2026 | Holding company and one of the oldest crypto venture investors | [fund page](https://crypto-fundraising.info/funds/digital-currency-group/) |
| Animoca Brands | `animoca-brands` | 442 | 116 | 83 | 2018–2026 | "We build, invest, and accelerate"; states "Backing 600+ builders". Largest single omission by round count and by lead count | [animocabrands.com](https://www.animocabrands.com/) |
| ParaFi Capital | `parafi-capital` | 136 | 28 | 83 | 2020–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/parafi-capital/) |
| Galaxy Digital | `galaxy-digital` | 170 | 50 | 81 | 2017–2026 | Financial services firm with a venture arm; CryptoRank tier 1 | [CryptoRank](https://cryptorank.io/funds) |
| Sequoia Capital | `sequoia` | 123 | 36 | 76 | 2017–2026 | Generalist with a substantial crypto book — the same shape as Founders Fund, already included | [CryptoRank](https://cryptorank.io/funds) |
| GSR | `gsr-markets-ltd` | 194 | 6 | 75 | 2021–2026 | Runs a dedicated venture line: "Investing in early-stage companies with capital and 13 years of experience" | [gsr.io](https://www.gsr.io/) |
| Blockchain Capital | `blockchain-capital` | 139 | 48 | 74 | 2014–2026 | "Partners to crypto builders since 2013"; CryptoRank tier 1 | [blockchaincapital.com](https://blockchaincapital.com/) |
| Hashed | `hashed` | 173 | 51 | 73 | 2017–2026 | Seoul-headquartered crypto VC with offices in five regions | [hashed.com](https://www.hashed.com/) |
| Solana Ventures | `solana-ventures` | 144 | 12 | 73 | 2021–2026 | Ecosystem investment arm — the same shape as GnosisVC, already included | [fund page](https://crypto-fundraising.info/funds/solana-ventures/) |
| Mechanism Capital | `mechanism-capital` | 130 | 24 | 73 | 2020–2025 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/mechanism-capital/) |
| CoinFund | `coin-fund` | 136 | 39 | 65 | 2017–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/coin-fund/) |
| CMS Holdings | `cms` | 187 | 7 | 64 | 2019–2026 | Trading firm that invests; low lead rate, see caveat below | [fund page](https://crypto-fundraising.info/funds/cms/) |
| Alliance DAO | `alliance-dao` | 127 | 11 | 63 | 2020–2026 | Accelerator **with** demonstrated investment: "$400,000 … at a $4M post-money valuation via SAFE" | [alliance.xyz](https://alliance.xyz/) |
| IOSG Ventures | `iosg-venture` | 140 | 19 | 62 | 2017–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/iosg-venture/) |
| OKX Ventures | `okx-blockdream-ventures` | 223 | 42 | 62 | 2020–2026 | Exchange venture arm — the same shape as Coinbase Ventures, already included | [fund page](https://crypto-fundraising.info/funds/okx-blockdream-ventures/) |
| Circle Ventures | `circle-ventures` | 101 | 6 | 62 | 2021–2026 | Corporate venture arm; CryptoRank tier 1 | [CryptoRank](https://cryptorank.io/funds) |
| HashKey Capital | `hashkey-capital` | 250 | 26 | 61 | 2018–2026 | Crypto VC; CryptoRank tier 1 with 288 portfolio companies | [CryptoRank](https://cryptorank.io/funds) |
| 1kx | `1kx` | 126 | 56 | 61 | 2018–2026 | Crypto VC; leads 44% of its rounds, one of the highest lead rates in the candidate set | [fund page](https://crypto-fundraising.info/funds/1kx/) |
| Hack VC | `hack-vc` | 117 | 50 | 58 | 2018–2026 | Crypto VC; 43% lead rate | [fund page](https://crypto-fundraising.info/funds/hack-vc/) |
| Hypersphere | `hypersphere` | 112 | 15 | 58 | 2020–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/hypersphere/) |
| CMT Digital | `cmt-digital` | 142 | 9 | 57 | 2017–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/cmt-digital/) |
| Mirana Ventures | `mirana-ventures` | 132 | 14 | 54 | 2021–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/mirana-ventures/) |
| Arrington Capital | `arrington-capital` | 126 | 25 | 47 | 2018–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/arrington-capital/) |
| Jump Crypto | `jump-crypto` | 110 | 33 | 46 | 2018–2026 | Trading firm's crypto arm with a substantial venture book; 30% lead rate | [fund page](https://crypto-fundraising.info/funds/jump-crypto/) |
| Amber Group | `amber-group` | 126 | 15 | 44 | 2020–2026 | Trading firm that invests; see caveat below | [fund page](https://crypto-fundraising.info/funds/amber-group/) |
| P2 Ventures (Polygon) | `polygon-ventures` | 154 | 11 | 44 | 2021–2026 | Ecosystem arm — same shape as GnosisVC | [fund page](https://crypto-fundraising.info/funds/polygon-ventures/) |
| HTX Ventures | `huobi-ventures` | 117 | 5 | 44 | 2018–2026 | Exchange venture arm | [fund page](https://crypto-fundraising.info/funds/huobi-ventures/) |
| Fenbushi Capital | `fenbushi-capital` | 147 | 14 | 43 | 2016–2026 | Crypto VC, active since 2016 | [fund page](https://crypto-fundraising.info/funds/fenbushi-capital/) |
| Big Brain Holdings | `big-brain-holdings` | 177 | 16 | 43 | 2021–2026 | Investment firm | [fund page](https://crypto-fundraising.info/funds/big-brain-holdings/) |
| YZi Labs (ex Binance Labs) | `yzi-labs` | 238 | 90 | 38 | 2018–2026 | Exchange venture arm; CryptoRank tier 1 with 292 portfolio companies. 90 leads — third-highest in the candidate set | [CryptoRank](https://cryptorank.io/funds) |
| SevenX Ventures | `sevenx-ventures` | 124 | 20 | 36 | 2020–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/sevenx-ventures/) |
| Sfermion | `sfermion` | 106 | 12 | 36 | 2021–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/sfermion/) |
| LongHash Ventures | `longhash-ventures` | 103 | 10 | 36 | 2020–2025 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/longhash-ventures/) |
| Foresight Ventures | `foresight-ventures` | 102 | 13 | 31 | 2021–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/foresight-ventures/) |
| Borderless Capital | `borderless-capital` | 137 | 42 | 30 | 2020–2026 | Crypto VC; 31% lead rate | [fund page](https://crypto-fundraising.info/funds/borderless-capital/) |
| MH Ventures | `mh-ventures` | 143 | 12 | 30 | 2021–2026 | Crypto VC | [fund page](https://crypto-fundraising.info/funds/mh-ventures/) |

### Tier 2 — above the threshold, lower overlap with the current twenty

These are real investing entities by the same bar but sit further from the
existing selection, so adding them widens the database more than it corrects
it. Round counts are from the source; none has been verified beyond its fund
page.

| Fund | source slug | rounds | lead | shared | active |
| --- | --- | ---: | ---: | ---: | --- |
| NGC Ventures | `ngc-ventures` | 261 | 22 | 43 | 2018–2026 |
| Shima Capital | `shima-capital` | 205 | 35 | 45 | 2021–2025 |
| Liquid Capital (LD Capital) | `ld-capital` | 190 | 12 | 14 | 2019–2026 |
| AU21 Capital | `au21-capital` | 189 | 6 | 8 | 2018–2025 |
| Genesis Block Ventures | `gbv-capital` | 163 | 5 | 16 | 2020–2025 |
| Morningstar Ventures | `morningstar-ventures` | 155 | 9 | 26 | 2018–2026 |
| x21 Digital | `x21-digital` | 129 | 5 | 3 | 2020–2026 |
| Signum Capital | `signum-capital` | 125 | 8 | 17 | 2018–2026 |
| SNZ Holding | `snz-holding` | 124 | 5 | 23 | 2019–2026 |
| Spark Digital Capital | `spark-digital-capital` | 124 | 6 | 11 | 2018–2025 |
| Digital Finance Group | `dfg` | 108 | 16 | 11 | 2017–2025 |
| Genblock Capital | `genblock-capital` | 108 | 1 | 16 | 2020–2024 |
| NxGen | `nxgen` | 107 | 2 | 20 | 2020–2025 |
| Waterdrip Capital | `waterdrip-capital` | 105 | 9 | 5 | 2018–2026 |
| Kenetic | `kenetic` | 105 | 11 | 17 | 2017–2026 |
| Cogitent Ventures | `cogitent-ventures` | 101 | 5 | 7 | 2022–2026 |
| SkyVision Capital | `skyvision-capital` | 101 | 4 | 26 | 2021–2025 |
| Infinity Ventures Crypto | `infinity-ventures-crypto` | 101 | 13 | 17 | 2021–2026 |

---

## 2. Alias fixes

Slugs that are an existing fund under another name, or a decision already taken
that the round counts suggest revisiting. None of these is a new fund.

| Slug | Name | Rounds | Belongs to | Status |
| --- | --- | ---: | --- | --- |
| `a16z-crypto-startup-accelerator` | a16z Crypto Startup Accelerator (CSX) | 38 | a16z crypto | **Revisit.** `funds.py` excludes it as "a different programme". CSX takes equity, so under this brief's own rule — accelerators *with* demonstrated investment count — it arguably belongs, either merged into a16z crypto or as its own entry. 38 rounds is material against a16z's 294. |
| `coinbase` | Coinbase | 15 | Coinbase Ventures | **Revisit.** `funds.py` excludes it because "'Coinbase' as the exchange entity is not an investor", yet the source records it as an investor in 15 rounds. CryptoRank also lists "Coinbase" separately with 18 portfolio companies. Worth checking whether these are genuine parent-entity investments. |
| `a16z-crypto-startup-school-css` | a16z Crypto Startup School | 6 | a16z crypto | Programme, not an investor. Current exclusion stands. |
| `a16z-games`, `a16z-games-speedrun` | a16z Games | 1, 5 | — | Separate gaming funds. Current exclusion stands. |
| `figment`, `figment-io` | Figment / Figment.io | 3, 1 | — | The staking operator, not Figment Capital. Current exclusion stands. |
| `safe-ex-gnosis-safe` | Safe (ex Gnosis Safe) | 10 | — | Spun-off project. Current exclusion stands. |
| `bain-capital-ventures` | Bain Capital Ventures (BCV) | 23 | — | Separate fund with its own mandate. Current exclusion stands. |

**Checked and confirmed as different firms despite similar names:** `maven-capital`
(50 rounds) is not Maven 11; `paradigm-capital`, `paradigm-co` and
`paradigm-shift-capital` are not Paradigm; `blockchain-founders-fund` is not
Founders Fund; the eleven `cyber*` slugs are not cyber•Fund.

---

## 3. Considered and rejected

| Candidate | Rounds | Rule applied |
| --- | ---: | --- |
| Balaji Srinivasan | 138 | Individual angel. Note: CryptoRank lists him as a tier-1 "fund" with 156 portfolio companies — an argument for a person-level dataset, not for this one. |
| Sandeep Nailwal | 129 | Individual angel |
| Anatoly Yakovenko | 39 | Individual angel |
| Paul Taylor | 19 | Individual angel |
| Marc Andreessen | 1 | Individual angel |
| Katie Haun | 1 | Individual angel; her fund, Haun Ventures, is already included |
| Y Combinator | 89 | Below the 100-round line, and a generalist accelerator rather than a crypto investor. CryptoRank lists it tier 1, so this is a close call — flagged rather than settled |
| VanEck | 24 | Below the line; asset manager |
| Cyberport Hong Kong | 3 | Government-backed programme, not a fund |
| Animoca Brands Japan | 107 | **Not rejected — flagged.** A separate legal entity with its own capital (raised $45M from MUFG at a $500M pre-money valuation), not a naming variant of the parent. Merging it into Animoca Brands would misstate both; keeping it separate double-counts the group. Needs a decision, and whichever way it goes should be written into `alias_evidence`. |

---

## 4. Ready-to-paste entries

Five representative entries, one per shape encountered. The remaining
recommendations follow the same pattern; `official_portfolio_url` and
`cryptorank_url` need filling per fund.

```python
    "blockchain-capital": {
        "fund_name": "Blockchain Capital",
        "source_slugs": ["blockchain-capital"],
        "aliases": ["Blockchain Capital", "BCap"],
        "official_portfolio_url": "https://blockchaincapital.com/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/blockchain-capital/portfolio",
        "alias_evidence": (
            "One fund page on crypto-fundraising.info. `ok-blockchain-capital` and "
            "`avant-blockchain-capital` are different firms and are not merged."
        ),
    },
    "alameda-research": {
        "fund_name": "Alameda Research",
        "source_slugs": ["alameda-research"],
        "aliases": ["Alameda Research", "Alameda"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/alameda-research/portfolio",
        "alias_evidence": (
            "Defunct since the FTX collapse in November 2022; the source records no "
            "round after 2022. Included deliberately: a database built to resist "
            "survivorship bias cannot omit the firms that failed. No official "
            "portfolio page survives, so the aggregator is the only control list."
        ),
    },
    "yzi-labs": {
        "fund_name": "YZi Labs",
        "source_slugs": ["yzi-labs"],
        "aliases": ["YZi Labs", "Binance Labs", "YZi Labs (ex Binance Labs)"],
        "official_portfolio_url": "https://www.yzilabs.com/",
        "cryptorank_url": "https://cryptorank.io/funds/binance-labs/portfolio",
        "alias_evidence": (
            "Binance Labs was renamed YZi Labs; the source carries one slug for both "
            "and the name change is why `fund_name_in_source` will vary by round."
        ),
    },
    "alliance-dao": {
        "fund_name": "Alliance DAO",
        "source_slugs": ["alliance-dao"],
        "aliases": ["Alliance DAO", "DeFi Alliance", "Alliance"],
        "official_portfolio_url": "https://alliance.xyz/",
        "cryptorank_url": "https://cryptorank.io/funds/alliance-dao/portfolio",
        "alias_evidence": (
            "An accelerator, but one with demonstrated capital investment: it states "
            "it invests $400,000 per admitted startup at a $4M post-money valuation "
            "via SAFE. Formerly DeFi Alliance."
        ),
    },
    "sequoia": {
        "fund_name": "Sequoia Capital",
        "source_slugs": ["sequoia"],
        "aliases": ["Sequoia Capital", "Sequoia"],
        "official_portfolio_url": "https://www.sequoiacap.com/companies/",
        "cryptorank_url": "https://cryptorank.io/funds/sequoia-capital/portfolio",
        "alias_evidence": (
            "A generalist fund with a substantial crypto book, the same shape as "
            "Founders Fund. `hongshan-ex-sequoia-china` and `peak-xv-partners-ex-as-"
            "sequoia-india-south-east-asia` are the demerged regional firms and are "
            "NOT merged in — they are separate partnerships since 2023."
        ),
    },
```

---

## 5. What this cannot settle

**One source decides the ranking.** Every round count here comes from
crypto-fundraising.info. A fund that is significant but poorly covered by that
site ranks low on this list, and this method cannot see it. The CryptoRank
cross-check found no such case among tier-1 names, which is reassuring but far
from proof — CryptoRank and crypto-fundraising.info may simply share the same
blind spots.

**The 100-round line is a judgement, not a finding.** 162 slugs clear 50 rounds
and 469 clear 20. Nothing in the data marks 100 as the natural break; it was
chosen because every slug above it spans at least four years. A different line
gives a different answer, and a database aiming at completeness rather than at
the twenty's peer group would set it far lower.

**Shape verification is thin below tier 1.** For the tier-2 table and the
smaller tier-1 entries I confirmed the slug resolves and read the fund page, but
I did not open each firm's own site. Several are plausibly market makers,
family offices or syndicates rather than funds, and that would change their
classification. Each needs its own check before it goes into `funds.py`.

**Trading firms are the weakest category.** GSR, CMS Holdings, Amber Group and
Jump Crypto all trade and all invest. GSR publishes a dedicated venture line, so
it clears the bar; for CMS and Amber I am relying on their appearance as
investors in the source rather than on a stated venture programme. Their low
lead rates — 7 leads in 187 rounds for CMS, 6 in 194 for GSR — are consistent
with balance-sheet participation rather than a venture practice, and the brief's
own rule excludes "market makers appearing as counterparties rather than
investors". A reader could reasonably reject all four.

**Adding these changes the existing findings.** The co-investment analysis in
section 04 of the frontend scores pairs against a null that holds each round's
number of *selected* funds fixed. Adding 54 funds changes that quantity for
nearly every round, so every lift figure would need recomputing. The current
result that Robot Ventures and Figment Capital co-invest at 4.5× chance is
conditional on the present selection and should not be quoted after an
expansion without rerunning `analyze_coinvestment.py`.

Not investment advice.
