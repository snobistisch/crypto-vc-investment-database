"""Canonical fund definitions and alias rules.

Single source of truth for the twenty funds in the brief. Every alias was
manually verified against the source's own fund page; `alias_evidence`
records why a name was merged into a canonical fund.

No automatic merging: a name that is not listed here stays a separate fund
and does not enter the dataset.
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
