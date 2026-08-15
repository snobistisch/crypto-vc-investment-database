# Dekkingsrapport

**Peildatum bron:** 2026-08-15
**Rapport gegenereerd:** 2026-08-15

> Volledig binnen de publiek toegankelijke en genoemde bronnen op de peildatum. Niet-aangekondigde rondes, secundaire transacties, liquide marktposities en investeerders die in persberichten onder 'others' vallen, blijven structureel onzichtbaar.

Alle cijfers hieronder zijn gegenereerd uit `data/processed/dataset.json` en
`data/processed/coverage-controls.json`. Er staat bewust geen algemeen
dekkingspercentage in dit rapport: een percentage veronderstelt een bekende
noemer, en de noemer is precies wat niet bekend is.

## Wat de scrape heeft doorzocht

| | |
| --- | ---: |
| Projectpagina's geparsed | 6.410 |
| Pagina's mislukt | 1 |
| Rondes in de bron | 10.395 |
| Investeerdersrelaties in de bron | 48.588 |
| Investeringsregels na filtering op de twintig fondsen | 2.947 |
| Unieke rondes met minstens één geselecteerd fonds | 2.040 |
| Unieke portefeuillebedrijven | 1.505 |

## Rondes en bedrijven per fonds

| Fonds | Rondes | Unieke bedrijven | Waarvan lead | Actief in |
| --- | ---: | ---: | ---: | --- |
| Coinbase Ventures | 497 | 430 | 27 | 2018–2026 |
| Pantera | 249 | 206 | 98 | 2014–2026 |
| Polychain | 261 | 200 | 121 | 2017–2026 |
| a16z crypto | 294 | 194 | 120 | 2011–2026 |
| Dragonfly | 222 | 184 | 84 | 2018–2026 |
| Robot Ventures | 156 | 152 | 12 | 2019–2026 |
| Delphi Ventures | 160 | 141 | 23 | 2021–2026 |
| Framework Ventures | 169 | 135 | 66 | 2019–2026 |
| Multicoin Capital | 160 | 131 | 54 | 2018–2026 |
| Paradigm | 144 | 116 | 77 | 2018–2026 |
| Lemniscap | 113 | 107 | 37 | 2018–2026 |
| Electric Capital | 116 | 96 | 40 | 2018–2026 |
| Maven11 | 104 | 89 | 20 | 2019–2026 |
| Figment Capital | 61 | 55 | 8 | 2021–2026 |
| Founders Fund | 62 | 49 | 27 | 2013–2026 |
| Haun Ventures | 41 | 37 | 19 | 2022–2026 |
| Bain Capital Crypto | 44 | 31 | 24 | 2018–2026 |
| GnosisVC | 33 | 31 | 6 | 2019–2026 |
| cyber•Fund | 30 | 29 | 14 | 2023–2026 |
| Semantic Ventures | 31 | 26 | 5 | 2018–2025 |

## Eigen telling naast de controlebronnen

De kolom *fondspagina bron* is een displaylimiet, geen portefeuilletotaal.
De kolom *CryptoRank* is de eigen telling van CryptoRank uit `__NEXT_DATA__`,
niet de zichtbare lijst van tien regels.

| Fonds | Eigen bedrijven | Fondspagina bron | Officiële pagina | RootData | CryptoRank | Verschil eigen − CryptoRank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Paradigm | 116 | 10 | 95 | — | 121 | -5 |
| cyber•Fund | 29 | 10 | — | — | 31 | -2 |
| Robot Ventures | 152 | 10 | 35 | — | 153 | -1 |
| Framework Ventures | 135 | 10 | — | — | 136 | -1 |
| Electric Capital | 96 | 10 | — | — | 101 | -5 |
| Bain Capital Crypto | 31 | 10 | 20 | — | 45 | -14 |
| Dragonfly | 184 | 10 | — | — | 183 | +1 |
| Maven11 | 89 | 10 | — | — | 101 | -12 |
| Lemniscap | 107 | 10 | — | — | 114 | -7 |
| Haun Ventures | 37 | 9 | 38 | — | 39 | -2 |
| Multicoin Capital | 131 | 10 | — | — | 156 | -25 |
| Figment Capital | 55 | 9 | — | — | 63 | -8 |
| a16z crypto | 194 | 10 | 127 | — | 204 | -10 |
| Founders Fund | 49 | 9 | — | — | 55 | -6 |
| Polychain | 200 | 10 | — | — | 222 | -22 |
| Pantera | 206 | 10 | — | — | 247 | -41 |
| Semantic Ventures | 26 | 10 | — | — | 28 | -2 |
| GnosisVC | 31 | 10 | — | — | 27 | +4 |
| Coinbase Ventures | 430 | 10 | — | — | 507 | -77 |
| Delphi Ventures | 141 | 10 | — | — | 175 | -34 |

## Datakwaliteit per fonds

| Fonds | Regels | Met rondegrootte | Met waardering | Met rondetype | Met primaire bron-URL |
| --- | ---: | ---: | ---: | ---: | ---: |
| Paradigm | 144 | 138 (96%) | 17 (12%) | 109 (76%) | 142 (99%) |
| cyber•Fund | 30 | 29 (97%) | 2 (7%) | 25 (83%) | 30 (100%) |
| Robot Ventures | 156 | 147 (94%) | 6 (4%) | 123 (79%) | 155 (99%) |
| Framework Ventures | 169 | 163 (96%) | 11 (7%) | 127 (75%) | 167 (99%) |
| Electric Capital | 116 | 114 (98%) | 8 (7%) | 89 (77%) | 116 (100%) |
| Bain Capital Crypto | 44 | 43 (98%) | 1 (2%) | 34 (77%) | 43 (98%) |
| Dragonfly | 222 | 203 (91%) | 19 (9%) | 166 (75%) | 220 (99%) |
| Maven11 | 104 | 103 (99%) | 8 (8%) | 83 (80%) | 103 (99%) |
| Lemniscap | 113 | 109 (96%) | 5 (4%) | 98 (87%) | 111 (98%) |
| Haun Ventures | 41 | 36 (88%) | 4 (10%) | 27 (66%) | 38 (93%) |
| Multicoin Capital | 160 | 151 (94%) | 8 (5%) | 125 (78%) | 159 (99%) |
| Figment Capital | 61 | 60 (98%) | 6 (10%) | 52 (85%) | 61 (100%) |
| a16z crypto | 294 | 277 (94%) | 26 (9%) | 204 (69%) | 290 (99%) |
| Founders Fund | 62 | 58 (94%) | 9 (15%) | 46 (74%) | 61 (98%) |
| Polychain | 261 | 249 (95%) | 26 (10%) | 188 (72%) | 260 (100%) |
| Pantera | 249 | 233 (94%) | 20 (8%) | 181 (73%) | 247 (99%) |
| Semantic Ventures | 31 | 31 (100%) | 2 (6%) | 27 (87%) | 31 (100%) |
| GnosisVC | 33 | 31 (94%) | 0 (0%) | 23 (70%) | 33 (100%) |
| Coinbase Ventures | 497 | 459 (92%) | 38 (8%) | 379 (76%) | 493 (99%) |
| Delphi Ventures | 160 | 142 (89%) | 13 (8%) | 113 (71%) | 157 (98%) |

## Verificatie en betrouwbaarheid

| Verificatiestatus | Regels |
| --- | ---: |
| verified_primary | 2.916 |
| verified_aggregator_only | 30 |
| conflict | 1 |

| Betrouwbaarheid | Regels |
| --- | ---: |
| high | 2.916 |
| medium | 30 |
| low | 1 |

`verified_two_sources` komt niet voor. De scripts stellen zelf geen tweede
onafhankelijke primaire bron vast, en een status die automatisch wordt
uitgedeeld is geen verificatie.

## Resterende datagaten

| Ontbrekend veld | Investeringsregels |
| --- | ---: |
| valuation_usd | 765 |
| round_type | 728 |
| round_size_usd | 171 |

Structureel leeg, met reden:

- `fund_ticket_usd` — geen enkele gebruikte bron publiceert wat een individueel
  fonds in een ronde inlegde. De rondegrootte hier overnemen zou een getal
  opleveren dat er goed uitziet en fout is.
- `country`, `sector`, `chain_or_ecosystem` — de projectpagina's van de bron
  voeren geen land-, sector- of ecosysteemtaxonomie. Niet ingevuld op gevoel.
- `acquisition_or_exit`, `acquirer`, `exit_price_usd` — vereisen een aparte
  exitdataset; die valt buiten deze opdracht.
- `secondary_source_url` — vereist handmatige verificatie per regel.

## Kruiscontrole met het eerdere dashboardonderzoek

| | |
| --- | ---: |
| Fonds-rondeparen uit het dashboard (13 aug 2026) | 153 |
| Daarvan teruggevonden in deze dataset | 96 |
| Niet teruggevonden | 57 |

De niet-teruggevonden regels zijn niet stilzwijgend verwijderd en niet als
bevestigd overgenomen. Ze matchen niet op de combinatie fonds, projectnaam en
maand. Plausibele oorzaken, niet per regel uitgezocht: het project is bij de
bron hernoemd, de ronde is sinds 13 augustus 2026 aangepast, of de maand
verschilt tussen aankondiging en registratie. Overname zonder die controle
zou regels aan de dataset toevoegen die de huidige bron niet bevestigt.

## Bronconflicten

Het tabblad `Conflicten` bevat 1 conflictregel. Die is niet gladgestreken: de actuele
bronpagina is in de datavelden aangehouden en de afwijkende waarde uit het
eerdere dashboardonderzoek blijft ernaast staan.

Geen beleggingsadvies.
