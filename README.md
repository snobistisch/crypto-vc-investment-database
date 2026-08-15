# Crypto-VC-investeringsdatabase

Reproduceerbare database van publiek bekende investeringen van twintig
crypto-venture-capitalfondsen. Eén regel per combinatie van fonds en
financieringsronde, elke regel herleidbaar tot een bron-URL.

> **Volledigheid.** Volledig binnen de publiek toegankelijke en genoemde
> bronnen op de peildatum. Niet-aangekondigde rondes, secundaire transacties,
> liquide marktposities en investeerders die in persberichten onder 'others'
> vallen, blijven structureel onzichtbaar.

## Uitvoer

| Bestand | Inhoud |
| --- | --- |
| `outputs/vc-investeringen-volledig.xlsx` | Alle twintig fondsen. Tien tabbladen: README, Fondsen, Investeringen, Rondes, Portefeuillebedrijven, Dekking, Bronnen, Conflicten, Onbekend, Aliases |
| `outputs/vc-investeringen-volledig.csv` | Platte export van het tabblad `Investeringen` |
| `outputs/per-fonds/vc-investeringen-<fonds>.xlsx` | Twintig bestanden, één per fonds, met dezelfde tabbladen en kolommen |

De fondsbestanden zijn dezelfde dataset met een fondsfilter, niet een tweede
opbouw: identieke kolommen, identieke opmaakregels. Twee dingen zijn bewust
niet meegefilterd:

- Het tabblad **Rondes** toont álle investeerders in dezelfde ronde, ook fondsen
  buiten dat bestand. De rest van de cap table is juist het interessante deel.
- Het tabblad **Dekking** houdt de controletotalen van de externe bronnen, zodat
  ook een los fondsbestand laat zien waar het afwijkt.

De validatie controleert dat de twintig fondsbestanden optellen tot het
overzicht en dat geen bestand een regel van een ander fonds bevat.

## De fondsen

Paradigm · cyber•Fund · Robot Ventures · Framework Ventures · Electric Capital ·
Bain Capital Crypto · Dragonfly · Maven11 · Lemniscap · Haun Ventures ·
Multicoin Capital · Figment Capital · a16z crypto · Founders Fund · Polychain ·
Pantera · Semantic Ventures · GnosisVC · Coinbase Ventures · Delphi Ventures

## Waarom de ronde de eenheid is en niet het fonds

De fondspagina van crypto-fundraising.info toont tien rondes. Gemeten op
Paradigm: precies tien projectlinks, terwijl CryptoRank voor hetzelfde fonds
121 investeringen telt. Pagineringsparameters redirecten terug naar pagina één.
Daar komt bij dat fondsen afgeschreven bedrijven van hun eigen portfoliopagina
halen. Wie per fonds scrapet, meet de overlevers.

De dataset is daarom in één pass over alle projectpagina's opgebouwd, waarna de
index is omgekeerd naar fonds → investeringen. Officiële portfoliopagina's en
CryptoRank zijn uitsluitend als controlelijst gebruikt.

Uitgebreid: [`research/methodology.md`](research/methodology.md) en
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
./.venv/bin/python scripts/validate_dataset.py                   # 7
./.venv/bin/python -m pytest tests -q                            # 8
```

1. Leest herbruikbare gegevens uit het bestaande investeringsdashboard en legt
   een manifest met SHA-256 per bronbestand vast.
2. Haalt alle projectpagina's op en parset per ronde de investeerders. Pagina's
   worden gzip-gecachet in `data/raw/`, buiten Git; een herhaalde run haalt
   alleen ontbrekende pagina's op.
3. Haalt controletotalen per fonds op bij de aggregators en de officiële
   portfoliopagina's.
4. Draait de index om naar fonds-rondeparen en bouwt de aliastabel.
5. Bouwt het Excel-bestand en de CSV volledig uit de dataset.
6. Genereert `research/coverage-report.md` uit de dataset — geen ingetypte
   cijfers.
7. Valideert dataset en workbook. Eindigt met foutcode 1 bij een fout.

Stap 2 duurt ongeveer een uur: de bron limiteert op ongeveer anderhalf verzoek
per seconde en antwoordt bij hogere gelijktijdigheid met HTTP 429. De scrape
draait op vier workers met backoff.

## Veldbetekenis

Drie bedragvelden die vaak door elkaar worden gehaald:

- `round_size_usd` — omvang van de hele ronde.
- `fund_ticket_usd` — wat dit fonds zelf inlegde. Vrijwel altijd leeg: geen van
  de gebruikte bronnen publiceert dit. Het is niet ingevuld met de rondegrootte.
- `valuation_usd` — waardering van de ronde, met `valuation_type` ernaast.
  Nooit een actuele token-FDV.

Een ontbrekende waarde is een lege cel. Niet nul, niet `null`, niet geschat.
De bron gebruikt `0` en `TBD` voor onbekend; beide worden omgezet naar leeg.

Toegestane categorieën:

```text
fund_role            lead | co-lead | participant | incubator | unknown
investment_type      equity | token | SAFT | public_sale | strategic | incubated | unknown
verification_status  verified_primary | verified_two_sources | verified_aggregator_only
                     single_source | conflict | uncertain
confidence           high | medium | low
valuation_type       pre_money | post_money | FDV | enterprise_value | unknown
```

`verified_two_sources` komt in de gegenereerde data niet voor. De scripts
stellen zelf geen tweede onafhankelijke primaire bron vast, en een status die
automatisch wordt uitgedeeld is geen verificatie.

## Verhouding tot het investeringsdashboard

`/Users/matthiasalma/Documents/Investeringsdashboard` is uitsluitend als
leesbron gebruikt. Er is daar geen bestand gewijzigd, geen branch gemaakt en
niets gecommit. De 153 eerder gescrapete fonds-rondeparen zijn niet blind
samengevoegd maar als kruiscontrole gebruikt; afwijkingen staan op het tabblad
`Conflicten` en zijn niet gladgestreken.

`data/imported/source-manifest.json` legt bronrepository, Git-commit,
importdatum, SHA-256 per bronbestand en parserwaarschuwingen vast.

## Repositorystructuur

```text
data/imported/    geïmporteerde dashboarddata en het bronmanifest
data/raw/         gzip-cache van opgehaalde pagina's (niet in Git)
data/processed/   ronde-universum, genormaliseerde dataset, controletotalen
scripts/          import, scrape, normalisatie, workbook, validatie
research/         methode, bronaudit, dekkingsrapport
outputs/          xlsx en csv
tests/            parser-, dataset- en workbooktests
```

## Licentie

MIT voor de scripts. De onderliggende feitelijke gegevens komen van derden;
raadpleeg hun gebruiksvoorwaarden voordat u de datasets verder verspreidt. De
HTML-cache wordt bewust niet gecommit.

Geen beleggingsadvies.
