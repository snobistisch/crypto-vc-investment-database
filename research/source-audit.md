# Bronaudit

Wat is getest, wat werkte, en wat niet. Statuscodes zijn uitkomsten van
feitelijke requests op de peildatum, geen aannames.

## Gestructureerde API's

| Bron | Endpoint | Uitkomst |
| --- | --- | --- |
| crypto-fundraising.info | `/wp-json/wp/v2/projects` | **200**, `x-wp-total: 6411`, 65 pagina's — open en enumereerbaar |
| crypto-fundraising.info | `/wp-json/wp/v2/funds` | **200**, doorzoekbaar op naam; gebruikt om bronslugs te verifiëren |
| crypto-fundraising.info | ACF-relatievelden via REST | `acf` komt leeg terug; de relatie staat wél in de gerenderde HTML |
| CryptoRank | `__NEXT_DATA__` op de fondspagina | **200**, bevat `investments` — de eigen telling van CryptoRank |
| RootData | publieke portefeuillepagina | geen telling af te leiden zonder sleutel of JavaScript |
| DefiLlama Raises | `api.llama.fi/raises` | betaald sinds 2026 (vastgesteld in het eerdere dashboardonderzoek) |
| Crunchbase, CB Insights, PitchBook | — | sleutel of enterprise-contract vereist |

## robots.txt en rate-limiting

`https://crypto-fundraising.info/robots.txt` bevat `User-agent: *` met
`Disallow:` — geen enkel pad uitgesloten, en een sitemap-verwijzing.

De site limiteert wel op snelheid. Bij negen gelijktijdige verbindingen kwamen
**HTTP 429**-antwoorden terug; de doorvoer bleef daarbij rond anderhalf verzoek
per seconde steken. De scrape draait daarom op vier workers met een pauze per
verzoek en zes pogingen met exponentiële backoff. Een pagina die na zes
pogingen niet binnenkomt, wordt als mislukt geregistreerd en niet als leeg
verwerkt.

Elke pagina wordt gzip-gecachet in `data/raw/`, buiten Git. Een herhaalde run
doet daardoor geen enkel overbodig verzoek en haalt alleen de ontbrekende
pagina's op.

## De fondspagina als controlelijst

Gemeten op `https://crypto-fundraising.info/funds/paradigm/`: tien unieke
projectlinks. CryptoRank telt voor hetzelfde fonds 121 investeringen. Het
verschil is geen datafout maar een displaylimiet, en het is de reden dat deze
dataset niet per fonds is opgebouwd.

Dezelfde beperking geldt voor de openbare CryptoRank-portefeuillelijst, die
tien regels toont. Het veld `investments` in `__NEXT_DATA__` is wél een totaal
en is als controlegetal gebruikt — niet als bron van individuele rondes.

## Officiële portfoliopagina's

Van de twintig fondsen levert een minderheid een portefeuillelijst in statische
HTML. De rest rendert client-side; daar staat een lege cel met de reden. Waar
een lijst wel leesbaar is, is het aantal unieke uitgaande domeinen geteld als
benadering van het aantal portefeuillenamen. Dat is een benadering en staat als
zodanig in de kolomtoelichting.

Een portfoliopagina van een fonds is hoe dan ook een controlelijst en geen
primaire bron: fondsen halen afgeschreven bedrijven weg.

## Hergebruik uit het investeringsdashboard

Uit `SOURCE_REPOSITORY` zijn 153 fonds-rondeparen overgenomen (Haun Ventures en
Paradigm, gescrapet op 13 augustus 2026) plus vijf tokenmetingen en de
CryptoRank-slicetellingen per fonds. Die 153 regels zijn niet blind
samengevoegd maar als **kruiscontrole** gebruikt: waar de leadstatus of de
rondegrootte afwijkt van de actuele bronpagina, staat het verschil op het
tabblad `Conflicten` en is het niet gladgestreken.

`data/imported/source-manifest.json` legt de bronrepository, het Git-commit,
de importdatum, een SHA-256 per bronbestand en de parserwaarschuwingen vast.

De bronrepository is uitsluitend gelezen. Er is daar geen bestand gewijzigd,
geen branch gemaakt en niets gecommit.

## Bekende beperkingen van de bron

1. Persberichten noemen lead en "others"; de "others" vallen weg en verschijnen
   in geen enkele database.
2. Niet-aangekondigde pre-seedrondes bestaan niet in openbare bronnen.
3. Secundaire aankopen en SAFT-overnames maken een fonds nergens zichtbaar als
   investeerder.
4. Een deel van de rondes heeft geen rondetype in de bron; die cel blijft leeg.
5. Waar de bron alleen maand en jaar geeft, staat de datum op de eerste van de
   maand met `date_precision = month`.

Geen beleggingsadvies.
