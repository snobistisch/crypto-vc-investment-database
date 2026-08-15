"""Canonieke fondsdefinities en aliasregels.

Eén bron van waarheid voor de twintig fondsen uit de opdracht. Iedere alias is
handmatig vastgesteld tegen de fondspagina van de bron; `alias_evidence` legt
vast waarom een naam met een canoniek fonds is samengevoegd.

Niet automatisch samenvoegen: een naam die hier niet staat, blijft een apart
fonds en komt niet in de dataset terecht.
"""

# canonical_slug -> definitie
FUNDS = {
    "paradigm": {
        "fund_name": "Paradigm",
        "source_slugs": ["paradigm"],
        "aliases": ["Paradigm", "Paradigm Capital"],
        "official_portfolio_url": "https://www.paradigm.xyz/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/paradigm/portfolio",
        "alias_evidence": "Eén fondspagina op crypto-fundraising.info; geen tweede Paradigm-slug gevonden.",
    },
    "cyber-fund": {
        "fund_name": "cyber•Fund",
        "source_slugs": ["cyber-fund"],
        "aliases": ["cyber•Fund", "cyber Fund", "cyberFund", "Cyber Fund"],
        "official_portfolio_url": "https://cyber.fund/",
        "cryptorank_url": "https://cryptorank.io/funds/cyber-fund/portfolio",
        "alias_evidence": "Bron schrijft 'cyber•Fund'; slug cyber-fund. Punt is opmaak, geen naamsverschil.",
    },
    "robot-ventures": {
        "fund_name": "Robot Ventures",
        "source_slugs": ["robot-ventures"],
        "aliases": ["Robot Ventures", "Robot VC"],
        "official_portfolio_url": "https://robvc.com/",
        "cryptorank_url": "https://cryptorank.io/funds/robot-ventures/portfolio",
        "alias_evidence": "Eén fondspagina; geen tweede slug.",
    },
    "framework-ventures": {
        "fund_name": "Framework Ventures",
        "source_slugs": ["framework"],
        "aliases": ["Framework Ventures", "Framework"],
        "official_portfolio_url": "https://framework.ventures/",
        "cryptorank_url": "https://cryptorank.io/funds/framework-ventures/portfolio",
        "alias_evidence": "Bronslug is `framework`, brontitel 'Framework Ventures'. Eén fondspagina.",
    },
    "electric-capital": {
        "fund_name": "Electric Capital",
        "source_slugs": ["electric-capital"],
        "aliases": ["Electric Capital"],
        "official_portfolio_url": "https://www.electriccapital.com/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/electric-capital/portfolio",
        "alias_evidence": "Eén fondspagina; geen tweede slug.",
    },
    "bain-capital-crypto": {
        "fund_name": "Bain Capital Crypto",
        "source_slugs": ["bain-capital-crypto"],
        "aliases": ["Bain Capital Crypto", "Bain Capital Ventures"],
        "official_portfolio_url": "https://baincapitalcrypto.com/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/bain-capital-crypto/portfolio",
        "alias_evidence": (
            "De bron voert bain-capital-crypto en bain-capital-ventures als twee fondsen. "
            "Alleen bain-capital-crypto is opgenomen: Bain Capital Ventures is een apart "
            "fonds met een eigen mandaat en staat niet in de opdracht."
        ),
    },
    "dragonfly": {
        "fund_name": "Dragonfly",
        "source_slugs": ["dragonfly-capital"],
        "aliases": ["Dragonfly", "Dragonfly Capital", "Dragonfly Capital Partners"],
        "official_portfolio_url": "https://www.dragonfly.xyz/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/dragon-fly-capital/portfolio",
        "alias_evidence": "Fonds heeft 'Capital' uit de naam laten vallen; bronslug is nog dragonfly-capital.",
    },
    "maven11": {
        "fund_name": "Maven11",
        "source_slugs": ["maven-11-capital"],
        "aliases": ["Maven11", "Maven 11", "Maven 11 Capital"],
        "official_portfolio_url": "https://www.maven11.com/",
        "cryptorank_url": "https://cryptorank.io/funds/maven11/portfolio",
        "alias_evidence": "Spatie- en achtervoegselvarianten van dezelfde Nederlandse firma.",
    },
    "lemniscap": {
        "fund_name": "Lemniscap",
        "source_slugs": ["lemniscap"],
        "aliases": ["Lemniscap", "Lemniscap Ventures"],
        "official_portfolio_url": "https://lemniscap.com/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/lemniscap/portfolio",
        "alias_evidence": "Eén fondspagina; geen tweede slug.",
    },
    "haun-ventures": {
        "fund_name": "Haun Ventures",
        "source_slugs": ["haun-ventures"],
        "aliases": ["Haun Ventures", "HAUN Ventures", "Haun"],
        "official_portfolio_url": "https://www.haun.co/portfolio",
        "cryptorank_url": "https://cryptorank.io/funds/haun-ventures/portfolio",
        "alias_evidence": "Bron schrijft 'HAUN Ventures'; kapitalisatie is opmaak.",
    },
    "multicoin-capital": {
        "fund_name": "Multicoin Capital",
        "source_slugs": ["multicoin-capital"],
        "aliases": ["Multicoin Capital", "Multicoin"],
        "official_portfolio_url": "https://multicoin.capital/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/multicoin-capital/portfolio",
        "alias_evidence": "Eén fondspagina; geen tweede slug.",
    },
    "figment-capital": {
        "fund_name": "Figment Capital",
        "source_slugs": ["figment-capital"],
        "aliases": ["Figment Capital", "Figment"],
        "official_portfolio_url": "https://www.figmentcapital.io/",
        "cryptorank_url": "https://cryptorank.io/funds/figment-capital/portfolio",
        "alias_evidence": (
            "Figment Capital is de investeringstak; 'Figment' zonder achtervoegsel is de "
            "stakingoperator en wordt niet automatisch samengevoegd."
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
            "De bron voert één slug a16z-crypto met titel 'Andreessen Horowitz (a16z crypto)'. "
            "Er bestaat geen aparte andreessen-horowitz-slug voor investeringen; de a16z Games- "
            "en accelerator-slugs zijn andere programma's en niet meegenomen."
        ),
    },
    "founders-fund": {
        "fund_name": "Founders Fund",
        "source_slugs": ["founders-fund"],
        "aliases": ["Founders Fund", "Founders fund"],
        "official_portfolio_url": "https://foundersfund.com/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/founders-fund/portfolio",
        "alias_evidence": "Eén fondspagina; kapitalisatie wisselt in de bron.",
    },
    "polychain": {
        "fund_name": "Polychain",
        "source_slugs": ["polychain-capital"],
        "aliases": ["Polychain", "Polychain Capital"],
        "official_portfolio_url": "https://polychain.capital/",
        "cryptorank_url": "https://cryptorank.io/funds/polychain-capital/portfolio",
        "alias_evidence": "Bronslug bevat 'capital'; het fonds presenteert zich als Polychain.",
    },
    "pantera": {
        "fund_name": "Pantera",
        "source_slugs": ["pantera-capital"],
        "aliases": ["Pantera", "Pantera Capital"],
        "official_portfolio_url": "https://panteracapital.com/portfolio/",
        "cryptorank_url": "https://cryptorank.io/funds/pantera-capital/portfolio",
        "alias_evidence": "Bronslug bevat 'capital'; zelfde firma.",
    },
    "semantic-ventures": {
        "fund_name": "Semantic Ventures",
        "source_slugs": ["semantic-ventures"],
        "aliases": ["Semantic Ventures", "Semantic"],
        "official_portfolio_url": "https://www.semantic.vc/",
        "cryptorank_url": "https://cryptorank.io/funds/semantic-ventures/portfolio",
        "alias_evidence": "Eén fondspagina; geen tweede slug.",
    },
    "gnosis-vc": {
        "fund_name": "GnosisVC",
        "source_slugs": ["gnosis"],
        "aliases": ["GnosisVC", "Gnosis VC", "Gnosis", "GnosisDAO"],
        "official_portfolio_url": "https://www.gnosis.io/",
        "cryptorank_url": "https://cryptorank.io/funds/gnosis/portfolio",
        "alias_evidence": (
            "De bron kent één slug `gnosis` met titel 'Gnosis'. GnosisVC uit de opdracht is de "
            "investeringsarm van datzelfde ecosysteem. Safe (ex Gnosis Safe) is een afgesplitst "
            "project en niet meegenomen."
        ),
    },
    "coinbase-ventures": {
        "fund_name": "Coinbase Ventures",
        "source_slugs": ["coinbase-ventures"],
        "aliases": ["Coinbase Ventures", "Coinbase"],
        "official_portfolio_url": "https://www.coinbase.com/ventures",
        "cryptorank_url": "https://cryptorank.io/funds/coinbase-ventures/portfolio",
        "alias_evidence": (
            "'Coinbase' als beursentiteit is geen investeerder; alleen de slug "
            "coinbase-ventures wordt meegenomen."
        ),
    },
    "delphi-ventures": {
        "fund_name": "Delphi Ventures",
        "source_slugs": ["delphi-ventures", "delphi-digital", "delphi-labs"],
        "aliases": ["Delphi Ventures", "Delphi Digital", "Delphi Labs", "Delphi"],
        "official_portfolio_url": "https://delphiventures.io/",
        "cryptorank_url": "https://cryptorank.io/funds/delphi-ventures/portfolio",
        "alias_evidence": (
            "Delphi Digital is de researchtak, Delphi Ventures de investeringstak, Delphi Labs "
            "de bouwtak. In fundraisingbronnen worden de namen door elkaar gebruikt voor "
            "dezelfde cap-tableregels; bronnaam blijft zichtbaar."
        ),
    },
}

# bron-slug -> canonieke slug
SLUG_TO_CANONICAL = {}
for _canonical, _meta in FUNDS.items():
    for _s in _meta["source_slugs"]:
        SLUG_TO_CANONICAL[_s] = _canonical

# genormaliseerde naam -> canonieke slug (fallback wanneer alleen een naam bekend is)
NAME_TO_CANONICAL = {}
for _canonical, _meta in FUNDS.items():
    for _a in _meta["aliases"] + [_meta["fund_name"]]:
        NAME_TO_CANONICAL[_a.lower().replace("•", " ").replace("-", " ").strip()] = _canonical


def canonical_for_slug(slug):
    """Canonieke fondsslug voor een bronslug, of None."""
    return SLUG_TO_CANONICAL.get((slug or "").strip().lower())


def canonical_for_name(name):
    """Canonieke fondsslug voor een vrije naam, of None. Voegt niets fuzzy samen."""
    if not name:
        return None
    key = name.lower().replace("•", " ").replace("-", " ")
    key = " ".join(key.split())
    return NAME_TO_CANONICAL.get(key)
