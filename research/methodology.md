# Methode

## De keuze die alles bepaalt: de ronde is de eenheid, niet het fonds

Fondspagina's zijn de voor de hand liggende ingang en de verkeerde. Twee
gemeten eigenschappen maken ze ongeschikt als primaire bron:

1. **Displaylimiet.** De fondspagina van crypto-fundraising.info toont tien
   rondes. Gemeten op `https://crypto-fundraising.info/funds/paradigm/`:
   precies tien unieke projectlinks, terwijl CryptoRank voor hetzelfde fonds
   121 investeringen telt. Pagineringsparameters redirecten terug naar pagina
   één.
2. **Overlevingsbias.** Een fonds dat zijn eigen portfoliopagina onderhoudt,
   heeft geen reden om afgeschreven bedrijven te laten staan. Dezelfde bias
   zit in de openbare CryptoRank-weergave, die tien liquide namen toont.

Beide effecten wijzen dezelfde kant op: wie per fonds scrapet, meet de winnaars
en noemt dat een portefeuille.

De dataset is daarom in één pass over **alle 6.411 projectpagina's** opgebouwd.
Per ronde zijn alle investeerders geparsed; daarna is de index omgekeerd naar
fonds → investeringen. Een fonds komt in deze dataset voor omdat het in een
ronde stond, niet omdat het zichzelf op een lijst zette.

## Twee representaties per pagina, tegen elkaar gelegd

Elke projectpagina bevat dezelfde rondes twee keer, in verschillende vorm. De
parser leest beide en voegt ze samen.

| | JSON-LD `funding[]` | HTML `newrisedblock` |
| --- | --- | --- |
| Rondedatum | exact, `startDate: 2024-04-09` | alleen maand, `Raised Apr 2024` |
| Rondetype | `name`, ook `Unknown` | `roundtype`, ontbreekt vaker |
| Bedrag | `amount.value` | `abbrusd` |
| Waardering | — | `roundvalua` |
| Lead versus deelnemer | — | `Lead Investors` / `Investors` |
| Oorspronkelijke bron | — | `raisedinlink` → persbericht |

De twee lijsten staan in dezelfde volgorde, nieuwste eerst, en worden op index
uitgelijnd. De uitlijning wordt gecontroleerd: de exacte datum uit JSON-LD
wordt alleen overgenomen wanneer maand en jaar overeenkomen met het HTML-label.
Bij afwijking valt de datum terug op de eerste van de maand en wordt
`date_precision` op `month` gezet plus een waarschuwing vastgelegd.

De lead-toewijzing gebeurt op positie: elke investeerderslink krijgt de rol van
de dichtstbijzijnde voorafgaande kop. Dat is robuuster dan het knippen van
geneste `div`-blokken, die in de bron niet consistent gesloten zijn.

## Wat een investering is

Opgenomen: equity-rondes, pre-seed tot en met late stage, strategische
investeringen, aangekondigde token- en SAFT-investeringen, publieke token sales
met aantoonbare deelname, vervolgfinancieringen, en incubaties met aantoonbaar
kapitaal.

Niet opgenomen: grants, accelerator-deelname zonder investering, partnerships,
market-making, ecosystem incentives, tokens die alleen op de markt zijn gekocht,
en adviesrollen. Rondetypen die als grant of airdrop in de bron staan, krijgen
`verification_status = uncertain` met de reden in `notes`; ze worden niet
stilzwijgend verwijderd en niet als bevestigde investering gepresenteerd.

## Bedragen: drie velden die niet hetzelfde zijn

`round_size_usd` is de omvang van de hele ronde. `fund_ticket_usd` is wat het
fonds zelf inlegde. `valuation_usd` is de waardering van de ronde, met
`valuation_type` ernaast.

`fund_ticket_usd` is in deze dataset vrijwel overal leeg, en dat is de juiste
uitkomst: geen van de gebruikte bronnen publiceert wat een individueel fonds
in een ronde stopte. De rondegrootte in dat veld overnemen zou een getal
opleveren dat er goed uitziet en fout is.

`valuation_usd` is nooit ingevuld met een actuele token-FDV. Een waardering uit
2021 en een marktkapitalisatie van vandaag zijn verschillende grootheden.

## Ontbrekende waarden

Een ontbrekende waarde is een lege cel. Niet nul, niet `null`, niet geschat.
De bron gebruikt `0` en `TBD` voor onbekend; de parser zet beide om naar leeg.
Elke regel met een ontbrekend veld staat op het tabblad `Onbekend` met wat er
is geprobeerd.

## Aliassen

Fondsnamen zijn samengevoegd op grond van de bronslug, niet op naamgelijkenis.
Elke samenvoeging staat in `scripts/funds.py` met een reden, en die reden staat
ook op het tabblad `Aliases`. Drie beslissingen zijn het vermelden waard:

- **Bain Capital Ventures is niet samengevoegd met Bain Capital Crypto.** De
  bron voert twee fondsen; het zijn twee fondsen met een eigen mandaat.
- **Figment (stakingoperator) is niet samengevoegd met Figment Capital.**
- **Delphi Ventures, Delphi Digital en Delphi Labs zijn wél samengevoegd.** De
  drie namen worden in fundraisingbronnen door elkaar gebruikt voor dezelfde
  cap-tableregels. `fund_name_in_source` houdt zichtbaar welke naam er stond,
  zodat de samenvoeging terug te draaien is.

## Verificatiestatus

`verified_primary` betekent dat de aggregatorpagina een Details-link naar de
oorspronkelijke aankondiging of het persbericht bevat en dat die link is
vastgelegd. `verified_aggregator_only` betekent dat alleen de aggregatorpagina
de ronde bevestigt. `verified_two_sources` wordt door de scripts niet
toegekend — het script stelt zelf geen tweede onafhankelijke primaire bron
vast, en een status die automatisch wordt uitgedeeld is geen verificatie.

## Dekking meten in plaats van claimen

Per fonds staan vier getallen naast elkaar op het tabblad `Dekking`: de eigen
telling, de fondspagina van de aggregator, de officiële portfoliopagina en de
telling van CryptoRank. Waar een bron niet leesbaar is — client-side gerenderde
portfoliopagina's, RootData zonder sleutel — staat dat er als zodanig, met een
lege cel in plaats van een schatting.

Er staat geen algemeen dekkingspercentage in dit bestand. Een percentage
veronderstelt een bekende noemer, en de noemer is precies wat niet bekend is.

## Volledigheid

> Volledig binnen de publiek toegankelijke en genoemde bronnen op de peildatum.
> Niet-aangekondigde rondes, secundaire transacties, liquide marktposities en
> investeerders die in persberichten onder 'others' vallen, blijven structureel
> onzichtbaar.

Geen beleggingsadvies.
