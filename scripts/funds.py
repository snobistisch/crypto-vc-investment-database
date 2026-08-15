"""Canonical fund definitions and alias rules.

Single source of truth for every fund in the dataset. Every alias was
manually verified against the source's own fund page; `alias_evidence`
records why a name was merged into a canonical fund.

No automatic merging: a name that is not listed here stays a separate fund
and does not enter the dataset.

The original twenty (brief) are followed by a second block added from
`research/missing-funds.md` — the funds with 100+ rounds in the source that
were not already covered. See that file for the round counts, the exclusion
rules applied, and what was rejected. Several entries below carry a blank
`official_portfolio_url` or `cryptorank_url`: that control-list URL was not
verified during the research pass, so it is left empty rather than guessed.
An empty URL is handled by `fetch_coverage_controls.py` as "not checked", not
as a zero.
"""

# canonical_slug -> definition
FUNDS = {
    "paradigm": {
        "fund_name": "Paradigm",
        "source_slugs": ["paradigm"],
        "aliases": ["Paradigm", "Paradigm Capital"],
        "official_portfolio_url": "https://www.paradigm.xyz/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/paradigm/portfolio",
        "alias_evidence": "One fund page on crypto-fundraising.info; no second Paradigm slug found.",
    },
    "cyber-fund": {
        "fund_name": "cyber•Fund",
        "source_slugs": ["cyber-fund"],
        "aliases": ["cyber•Fund", "cyber Fund", "cyberFund", "Cyber Fund"],
        "official_portfolio_url": "https://cyber.fund/",
        "cryptorank_url": "https://cryptorank.io/funds/cyber-fund/portfolio",
        "alias_evidence": "Source writes 'cyber•Fund'; slug cyber-fund. The dot is styling, not a name difference.",
    },
    "robot-ventures": {
        "fund_name": "Robot Ventures",
        "source_slugs": ["robot-ventures"],
        "aliases": ["Robot Ventures", "Robot VC"],
        "official_portfolio_url": "https://robvc.com/",
        "cryptorank_url": "https://cryptorank.io/funds/robot-ventures/portfolio",
        "alias_evidence": "One fund page; no second slug.",
    },
    "framework-ventures": {
        "fund_name": "Framework Ventures",
        "source_slugs": ["framework"],
        "aliases": ["Framework Ventures", "Framework"],
        "official_portfolio_url": "https://framework.ventures/",
        "cryptorank_url": "https://cryptorank.io/funds/framework-ventures/portfolio",
        "alias_evidence": "Source slug is `framework`, source title 'Framework Ventures'. One fund page.",
    },
    "electric-capital": {
        "fund_name": "Electric Capital",
        "source_slugs": ["electric-capital"],
        "aliases": ["Electric Capital"],
        "official_portfolio_url": "https://www.electriccapital.com/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/electric-capital/portfolio",
        "alias_evidence": "One fund page; no second slug.",
    },
    "bain-capital-crypto": {
        "fund_name": "Bain Capital Crypto",
        "source_slugs": ["bain-capital-crypto"],
        "aliases": ["Bain Capital Crypto", "Bain Capital Ventures"],
        "official_portfolio_url": "https://baincapitalcrypto.com/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/bain-capital-crypto/portfolio",
        "alias_evidence": (
            "The source carries bain-capital-crypto and bain-capital-ventures as two funds. "
            "Only bain-capital-crypto is included: Bain Capital Ventures is a separate fund "
            "with its own mandate and is not in the brief."
        ),
    },
    "dragonfly": {
        "fund_name": "Dragonfly",
        "source_slugs": ["dragonfly-capital"],
        "aliases": ["Dragonfly", "Dragonfly Capital", "Dragonfly Capital Partners"],
        "official_portfolio_url": "https://www.dragonfly.xyz/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/dragon-fly-capital/portfolio",
        "alias_evidence": "The fund dropped 'Capital' from its name; the source slug is still dragonfly-capital.",
    },
    "maven11": {
        "fund_name": "Maven11",
        "source_slugs": ["maven-11-capital"],
        "aliases": ["Maven11", "Maven 11", "Maven 11 Capital"],
        "official_portfolio_url": "https://www.maven11.com/",
        "cryptorank_url": "https://cryptorank.io/funds/maven11/portfolio",
        "alias_evidence": "Spacing and suffix variants of the same Dutch firm.",
    },
    "lemniscap": {
        "fund_name": "Lemniscap",
        "source_slugs": ["lemniscap"],
        "aliases": ["Lemniscap", "Lemniscap Ventures"],
        "official_portfolio_url": "https://lemniscap.com/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/lemniscap/portfolio",
        "alias_evidence": "One fund page; no second slug.",
    },
    "haun-ventures": {
        "fund_name": "Haun Ventures",
        "source_slugs": ["haun-ventures"],
        "aliases": ["Haun Ventures", "HAUN Ventures", "Haun"],
        "official_portfolio_url": "https://www.haun.co/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/haun-ventures/portfolio",
        "alias_evidence": "Source writes 'HAUN Ventures'; capitalisation is styling.",
    },
    "multicoin-capital": {
        "fund_name": "Multicoin Capital",
        "source_slugs": ["multicoin-capital"],
        "aliases": ["Multicoin Capital", "Multicoin"],
        "official_portfolio_url": "https://multicoin.capital/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/multicoin-capital/portfolio",
        "alias_evidence": "One fund page; no second slug.",
    },
    "figment-capital": {
        "fund_name": "Figment Capital",
        "source_slugs": ["figment-capital"],
        "aliases": ["Figment Capital", "Figment"],
        "official_portfolio_url": "https://www.figmentcapital.io/",
        "cryptorank_url": "https://cryptorank.io/funds/figment-capital/portfolio",
        "alias_evidence": (
            "Figment Capital is the investment arm; 'Figment' without a suffix is the "
            "staking operator and is not automatically merged."
        ),
    },
    "a16z-crypto": {
        "fund_name": "a16z crypto",
        "source_slugs": ["a16z-crypto"],
        "aliases": [
            "a16z crypto",
            "a16z Crypto",
            "Andreessen Horowitz Crypto",
            "Andreessen Horowitz (a16z)",
            "a16z",
        ],
        "official_portfolio_url": "https://a16zcrypto.com/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/andreessen-horowitz/portfolio",
        "alias_evidence": (
            "The source carries a single slug a16z-crypto with title 'Andreessen Horowitz "
            "(a16z crypto)'. There is no separate andreessen-horowitz slug for investments; "
            "the a16z Games and accelerator slugs are different programmes and are not included."
        ),
    },
    "founders-fund": {
        "fund_name": "Founders Fund",
        "source_slugs": ["founders-fund"],
        "aliases": ["Founders Fund", "Founders fund"],
        "official_portfolio_url": "https://foundersfund.com/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/founders-fund/portfolio",
        "alias_evidence": "One fund page; capitalisation varies in the source.",
    },
    "polychain": {
        "fund_name": "Polychain",
        "source_slugs": ["polychain-capital"],
        "aliases": ["Polychain", "Polychain Capital"],
        "official_portfolio_url": "https://polychain.capital/",
        "cryptorank_url": "https://cryptorank.io/funds/polychain-capital/portfolio",
        "alias_evidence": "Source slug contains 'capital'; the fund presents itself as Polychain.",
    },
    "pantera": {
        "fund_name": "Pantera",
        "source_slugs": ["pantera-capital"],
        "aliases": ["Pantera", "Pantera Capital"],
        "official_portfolio_url": "https://panteracapital.com/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/pantera-capital/portfolio",
        "alias_evidence": "Source slug contains 'capital'; same firm.",
    },
    "semantic-ventures": {
        "fund_name": "Semantic Ventures",
        "source_slugs": ["semantic-ventures"],
        "aliases": ["Semantic Ventures", "Semantic"],
        "official_portfolio_url": "https://www.semantic.vc/",
        "cryptorank_url": "https://cryptorank.io/funds/semantic-ventures/portfolio",
        "alias_evidence": "One fund page; no second slug.",
    },
    "gnosis-vc": {
        "fund_name": "GnosisVC",
        "source_slugs": ["gnosis"],
        "aliases": ["GnosisVC", "Gnosis VC", "Gnosis", "GnosisDAO"],
        "official_portfolio_url": "https://www.gnosis.io/",
        "cryptorank_url": "https://cryptorank.io/funds/gnosis/portfolio",
        "alias_evidence": (
            "The source has one slug `gnosis` with title 'Gnosis'. GnosisVC from the brief is "
            "the investment arm of that same ecosystem. Safe (ex Gnosis Safe) is a spun-off "
            "project and is not included."
        ),
    },
    "coinbase-ventures": {
        "fund_name": "Coinbase Ventures",
        "source_slugs": ["coinbase-ventures"],
        "aliases": ["Coinbase Ventures", "Coinbase"],
        "official_portfolio_url": "https://www.coinbase.com/ventures",
        "cryptorank_url": "https://cryptorank.io/funds/coinbase-ventures/portfolio",
        "alias_evidence": (
            "'Coinbase' as the exchange entity is not an investor; only the slug "
            "coinbase-ventures is included."
        ),
    },
    "delphi-ventures": {
        "fund_name": "Delphi Ventures",
        "source_slugs": ["delphi-ventures", "delphi-digital", "delphi-labs"],
        "aliases": ["Delphi Ventures", "Delphi Digital", "Delphi Labs", "Delphi"],
        "official_portfolio_url": "https://delphiventures.io/",
        "cryptorank_url": "https://cryptorank.io/funds/delphi-ventures/portfolio",
        "alias_evidence": (
            "Delphi Digital is the research arm, Delphi Ventures the investment arm, Delphi "
            "Labs the builder arm. Fundraising sources use the names interchangeably for the "
            "same cap-table rows; the source name stays visible."
        ),
    },

    # ------------------------------------------------------------------
    # Added from research/missing-funds.md, tier 1 (100+ rounds in the
    # source, shape verified against the fund's own site or CryptoRank).
    # Round counts below are as measured on 2026-08-15 against
    # data/processed/rounds.json and are the basis for inclusion, not an
    # estimate of current activity.
    # ------------------------------------------------------------------

    "alameda-research": {
        "fund_name": "Alameda Research",
        "source_slugs": ["alameda-research"],
        "aliases": ["Alameda Research", "Alameda"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/alameda-research/portfolio",
        "alias_evidence": (
            "One fund page on crypto-fundraising.info, 207 rounds, active 2020-2022. "
            "Defunct since the FTX collapse in November 2022; no round after that year. "
            "Included deliberately: a database built to resist survivorship bias cannot "
            "omit the firms that failed. No official portfolio page survives."
        ),
    },
    "spartan-group": {
        "fund_name": "The Spartan Group",
        "source_slugs": ["the-spartan-group"],
        "aliases": ["The Spartan Group", "Spartan Group", "Spartan"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/spartan-group/portfolio",
        "alias_evidence": (
            "235 rounds, active 2018-2026. CryptoRank tier 1 with 233 portfolio "
            "companies, confirming the source's count independently."
        ),
    },
    "digital-currency-group": {
        "fund_name": "Digital Currency Group",
        "source_slugs": ["digital-currency-group"],
        "aliases": ["Digital Currency Group", "DCG"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": (
            "284 rounds, active 2013-2026 — one of the oldest crypto venture investors "
            "in the source. CryptoRank slug not found in a light probe; left blank "
            "rather than guessed."
        ),
    },
    "animoca-brands": {
        "fund_name": "Animoca Brands",
        "source_slugs": ["animoca-brands"],
        "aliases": ["Animoca Brands"],
        "official_portfolio_url": "https://www.animocabrands.com/",
        "cryptorank_url": "https://cryptorank.io/funds/animoca-brands/portfolio",
        "alias_evidence": (
            "442 rounds and 116 leads, active 2018-2026 — the single largest omission "
            "by round count in the twenty-fund selection. Own site states \"We build, "
            "invest, and accelerate\" and claims 600+ portfolio companies. "
            "`animoca-brands-japan` is a separate legal entity with its own outside "
            "capital (see below) and is not merged into this entry."
        ),
    },
    "parafi-capital": {
        "fund_name": "ParaFi Capital",
        "source_slugs": ["parafi-capital"],
        "aliases": ["ParaFi Capital", "ParaFi"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": "136 rounds, active 2020-2026, 83 shared with the original twenty.",
    },
    "galaxy-digital": {
        "fund_name": "Galaxy Digital",
        "source_slugs": ["galaxy-digital"],
        "aliases": ["Galaxy Digital", "Galaxy"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/galaxy-digital/portfolio",
        "alias_evidence": (
            "170 rounds, active 2017-2026. CryptoRank tier 1. `galaxy-interactive` and "
            "`project-galaxy` are different entities and are not merged in."
        ),
    },
    "sequoia-capital": {
        "fund_name": "Sequoia Capital",
        "source_slugs": ["sequoia"],
        "aliases": ["Sequoia Capital", "Sequoia"],
        "official_portfolio_url": "https://www.sequoiacap.com/companies/",
        "cryptorank_url": "https://cryptorank.io/funds/sequoia-capital/portfolio",
        "alias_evidence": (
            "A generalist fund with a substantial crypto book, the same shape as "
            "Founders Fund, already in the original twenty. 123 rounds, active "
            "2017-2026. `hongshan-ex-sequoia-china` and `peak-xv-partners-ex-as-"
            "sequoia-india-south-east-asia` are the demerged regional firms since "
            "2023 and are deliberately NOT merged in."
        ),
    },
    "gsr": {
        "fund_name": "GSR",
        "source_slugs": ["gsr-markets-ltd"],
        "aliases": ["GSR", "GSR Markets LTD", "GSR Markets"],
        "official_portfolio_url": "https://www.gsr.io/",
        "cryptorank_url": "https://cryptorank.io/funds/gsr/portfolio",
        "alias_evidence": (
            "194 rounds, active 2021-2026, but only 6 leads — consistent with balance-"
            "sheet participation rather than a pure venture practice. Included because "
            "the firm states a dedicated venture line: \"Investing in early-stage "
            "companies with capital and 13 years of experience.\" GSR also trades and "
            "makes markets; readers weighing that against the low lead rate may "
            "reasonably exclude this entry."
        ),
    },
    "blockchain-capital": {
        "fund_name": "Blockchain Capital",
        "source_slugs": ["blockchain-capital"],
        "aliases": ["Blockchain Capital", "BCap"],
        "official_portfolio_url": "https://blockchaincapital.com/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/blockchain-capital/portfolio",
        "alias_evidence": (
            "One fund page on crypto-fundraising.info, 139 rounds, active since 2014. "
            "Own site: \"Partners to crypto builders since 2013.\" `ok-blockchain-"
            "capital` and `avant-blockchain-capital` are different firms and are not "
            "merged."
        ),
    },
    "hashed": {
        "fund_name": "Hashed",
        "source_slugs": ["hashed"],
        "aliases": ["Hashed"],
        "official_portfolio_url": "https://www.hashed.com/",
        "cryptorank_url": "",
        "alias_evidence": (
            "173 rounds, active 2017-2026. Seoul-headquartered with offices in San "
            "Francisco, Singapore, Bangalore and Abu Dhabi per its own site."
        ),
    },
    "solana-ventures": {
        "fund_name": "Solana Ventures",
        "source_slugs": ["solana-ventures"],
        "aliases": ["Solana Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/solana-ventures/portfolio",
        "alias_evidence": (
            "Ecosystem investment arm, the same shape as GnosisVC in the original "
            "twenty. 144 rounds, active 2021-2026."
        ),
    },
    "mechanism-capital": {
        "fund_name": "Mechanism Capital",
        "source_slugs": ["mechanism-capital"],
        "aliases": ["Mechanism Capital"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/mechanism-capital/portfolio",
        "alias_evidence": "130 rounds, active 2020-2025.",
    },
    "coinfund": {
        "fund_name": "CoinFund",
        "source_slugs": ["coin-fund"],
        "aliases": ["CoinFund"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/coin-fund/portfolio",
        "alias_evidence": "136 rounds, active 2017-2026.",
    },
    "cms-holdings": {
        "fund_name": "CMS Holdings",
        "source_slugs": ["cms"],
        "aliases": ["CMS Holdings", "CMS"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/cms-holdings/portfolio",
        "alias_evidence": (
            "187 rounds, active 2019-2026, but only 7 leads — consistent with "
            "balance-sheet participation by a trading firm rather than a venture "
            "practice. No stated venture programme was verified beyond its appearance "
            "as an investor in the source; readers applying the brief's rule against "
            "counting market makers as investors may reasonably exclude this entry."
        ),
    },
    "alliance-dao": {
        "fund_name": "Alliance DAO",
        "source_slugs": ["alliance-dao"],
        "aliases": ["Alliance DAO", "DeFi Alliance", "Alliance"],
        "official_portfolio_url": "https://alliance.xyz/",
        "cryptorank_url": "https://cryptorank.io/funds/alliance-dao/portfolio",
        "alias_evidence": (
            "An accelerator, but one with demonstrated capital investment: its own "
            "FAQ states it invests $400,000 per admitted startup at a $4M post-money "
            "valuation via SAFE. Formerly DeFi Alliance. 127 rounds, active 2020-2026."
        ),
    },
    "iosg-ventures": {
        "fund_name": "IOSG Ventures",
        "source_slugs": ["iosg-venture"],
        "aliases": ["IOSG Ventures", "IOSG"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/iosg/portfolio",
        "alias_evidence": "140 rounds, active 2017-2026.",
    },
    "okx-ventures": {
        "fund_name": "OKX Ventures",
        "source_slugs": ["okx-blockdream-ventures"],
        "aliases": ["OKX Ventures", "OKEx Blockdream Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/okx-ventures/portfolio",
        "alias_evidence": (
            "Exchange venture arm, the same shape as Coinbase Ventures in the "
            "original twenty. 223 rounds, active 2020-2026."
        ),
    },
    "circle-ventures": {
        "fund_name": "Circle Ventures",
        "source_slugs": ["circle-ventures"],
        "aliases": ["Circle Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/circle-ventures/portfolio",
        "alias_evidence": (
            "101 rounds, active 2021-2026. CryptoRank tier 1. `circle-2` and "
            "`merit-circle` are different entities and are not merged in."
        ),
    },
    "hashkey-capital": {
        "fund_name": "HashKey Capital",
        "source_slugs": ["hashkey-capital"],
        "aliases": ["HashKey Capital", "Hashkey Capital"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": (
            "250 rounds, active 2018-2026. CryptoRank tier 1 with 288 portfolio "
            "companies, confirming the source's count independently. `hashkey-group` "
            "is the parent exchange entity and is not merged in."
        ),
    },
    "1kx": {
        "fund_name": "1kx",
        "source_slugs": ["1kx"],
        "aliases": ["1kx"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/1kx/portfolio",
        "alias_evidence": "126 rounds, active 2018-2026, 44% lead rate.",
    },
    "hack-vc": {
        "fund_name": "Hack VC",
        "source_slugs": ["hack-vc"],
        "aliases": ["Hack VC"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/hack-vc/portfolio",
        "alias_evidence": "117 rounds, active 2018-2026, 43% lead rate.",
    },
    "hypersphere": {
        "fund_name": "Hypersphere",
        "source_slugs": ["hypersphere"],
        "aliases": ["Hypersphere", "Hypersphere Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": "112 rounds, active 2020-2026.",
    },
    "cmt-digital": {
        "fund_name": "CMT Digital",
        "source_slugs": ["cmt-digital"],
        "aliases": ["CMT Digital"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/cmt-digital/portfolio",
        "alias_evidence": "142 rounds, active 2017-2026.",
    },
    "mirana-ventures": {
        "fund_name": "Mirana Ventures",
        "source_slugs": ["mirana-ventures"],
        "aliases": ["Mirana Ventures", "Mirana"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/mirana-ventures/portfolio",
        "alias_evidence": "132 rounds, active 2021-2026.",
    },
    "arrington-capital": {
        "fund_name": "Arrington Capital",
        "source_slugs": ["arrington-capital"],
        "aliases": ["Arrington Capital", "Arrington XRP Capital"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": "126 rounds, active 2018-2026.",
    },
    "jump-crypto": {
        "fund_name": "Jump Crypto",
        "source_slugs": ["jump-crypto"],
        "aliases": ["Jump Crypto", "Jump Trading"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/jump-crypto/portfolio",
        "alias_evidence": (
            "Trading firm's crypto venture arm, 110 rounds, active 2018-2026, "
            "30% lead rate."
        ),
    },
    "amber-group": {
        "fund_name": "Amber Group",
        "source_slugs": ["amber-group"],
        "aliases": ["Amber Group"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/amber-group/portfolio",
        "alias_evidence": (
            "126 rounds, active 2020-2026, but only 15 leads. No stated venture "
            "programme was verified beyond its appearance as an investor in the "
            "source; a trading firm, so the same caveat as CMS Holdings applies."
        ),
    },
    "polygon-ventures": {
        "fund_name": "Polygon Ventures",
        "source_slugs": ["polygon-ventures"],
        "aliases": ["Polygon Ventures", "P2 Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/polygon-ventures/portfolio",
        "alias_evidence": (
            "Ecosystem investment arm, the same shape as GnosisVC in the original "
            "twenty. 154 rounds, active 2021-2026."
        ),
    },
    "huobi-ventures": {
        "fund_name": "HTX Ventures",
        "source_slugs": ["huobi-ventures"],
        "aliases": ["HTX Ventures", "Huobi Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": (
            "Exchange venture arm, renamed from Huobi Ventures to HTX Ventures. "
            "117 rounds, active 2018-2026."
        ),
    },
    "fenbushi-capital": {
        "fund_name": "Fenbushi Capital",
        "source_slugs": ["fenbushi-capital"],
        "aliases": ["Fenbushi Capital"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/fenbushi-capital/portfolio",
        "alias_evidence": "147 rounds, active since 2016 — one of the older funds in this batch.",
    },
    "big-brain-holdings": {
        "fund_name": "Big Brain Holdings",
        "source_slugs": ["big-brain-holdings"],
        "aliases": ["Big Brain Holdings"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/big-brain-holdings/portfolio",
        "alias_evidence": "177 rounds, active 2021-2026.",
    },
    "yzi-labs": {
        "fund_name": "YZi Labs",
        "source_slugs": ["yzi-labs"],
        "aliases": ["YZi Labs", "Binance Labs", "YZi Labs (ex Binance Labs)"],
        "official_portfolio_url": "https://www.yzilabs.com/",
        "cryptorank_url": "https://cryptorank.io/funds/binance-labs/portfolio",
        "alias_evidence": (
            "Binance Labs was renamed YZi Labs; the source carries one slug for both, "
            "so `fund_name_in_source` will vary by round. 238 rounds and 90 leads, "
            "active 2018-2026. CryptoRank tier 1 with 292 portfolio companies under "
            "its former name."
        ),
    },
    "sevenx-ventures": {
        "fund_name": "SevenX Ventures",
        "source_slugs": ["sevenx-ventures"],
        "aliases": ["SevenX Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": "124 rounds, active 2020-2026.",
    },
    "sfermion": {
        "fund_name": "Sfermion",
        "source_slugs": ["sfermion"],
        "aliases": ["Sfermion"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/sfermion/portfolio",
        "alias_evidence": "106 rounds, active 2021-2026.",
    },
    "longhash-ventures": {
        "fund_name": "LongHash Ventures",
        "source_slugs": ["longhash-ventures"],
        "aliases": ["LongHash Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "",
        "alias_evidence": "103 rounds, active 2020-2025.",
    },
    "foresight-ventures": {
        "fund_name": "Foresight Ventures",
        "source_slugs": ["foresight-ventures"],
        "aliases": ["Foresight Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/foresight-ventures/portfolio",
        "alias_evidence": "102 rounds, active 2021-2026.",
    },
    "borderless-capital": {
        "fund_name": "Borderless Capital",
        "source_slugs": ["borderless-capital"],
        "aliases": ["Borderless Capital"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/borderless-capital/portfolio",
        "alias_evidence": "137 rounds, active 2020-2026, 31% lead rate.",
    },
    "mh-ventures": {
        "fund_name": "MH Ventures",
        "source_slugs": ["mh-ventures"],
        "aliases": ["MH Ventures"],
        "official_portfolio_url": "",
        "cryptorank_url": "https://cryptorank.io/funds/mh-ventures/portfolio",
        "alias_evidence": "143 rounds, active 2021-2026.",
    },
    "animoca-brands-japan": {
        "fund_name": "Animoca Brands Japan",
        "source_slugs": ["animoca-brands-japan"],
        "aliases": ["Animoca Brands Japan"],
        "official_portfolio_url": "https://animocabrands.co.jp/en/",
        "cryptorank_url": "",
        "alias_evidence": (
            "A separate legal entity from Animoca Brands with its own outside "
            "capital — raised $45M from MUFG and its parent at a $500M pre-money "
            "valuation, per public reporting. Merging it into Animoca Brands would "
            "misstate both entities' figures; kept separate deliberately, at the cost "
            "of the two potentially co-investing in the same round under different "
            "canonical slugs. 107 rounds, active 2018-2024."
        ),
    },
}

# source slug -> canonical slug
SLUG_TO_CANONICAL = {}
for _canonical, _meta in FUNDS.items():
    for _s in _meta["source_slugs"]:
        SLUG_TO_CANONICAL[_s] = _canonical

# normalised name -> canonical slug (fallback for when only a name is known)
NAME_TO_CANONICAL = {}
for _canonical, _meta in FUNDS.items():
    for _a in _meta["aliases"] + [_meta["fund_name"]]:
        NAME_TO_CANONICAL[_a.lower().replace("•", " ").replace("-", " ").strip()] = _canonical


def canonical_for_slug(slug):
    """Canonical fund slug for a source slug, or None."""
    return SLUG_TO_CANONICAL.get((slug or "").strip().lower())


def canonical_for_name(name):
    """Canonical fund slug for a free-text name, or None. Does not fuzzy-merge anything."""
    if not name:
        return None
    key = name.lower().replace("•", " ").replace("-", " ")
    key = " ".join(key.split())
    return NAME_TO_CANONICAL.get(key)
