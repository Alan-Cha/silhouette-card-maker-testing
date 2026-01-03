# Digimon Plugin

This plugin reads a decklist, fetches the card images, and puts the card images into the proper `game/` directories.

This plugin supports many decklist formats such as, `tts`, `digimonmeta`, and `untap`. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Tabletop Simulator (`tts`).

Run the script.

```sh
python plugins/digimon/fetch.py game/decklist/deck.txt tts
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {tts|digimoncardio|digimoncarddev|digimonc
                ardapp|digimonmeta|untap}

Options:
  --help  Show this message and exit.
```

## Formats

### `tts`

The format for ``Tabletop Simulator``.

```
["Exported from https://digimoncard.dev","BT15-006","BT15-006","BT15-006","BT15-006","BT2-070","BT2-070","BT2-070","BT15-069","BT15-069","BT15-069","BT15-069","P-123","BT16-082","BT16-082","BT16-082","BT16-082","BT19-062","BT18-026","BT18-053","BT7-013","BT8-067","EX9-011","EX9-012","EX9-043","BT11-055","BT18-052","BT19-052","EX7-044","ST17-07","EX9-030","BT15-064","EX9-064","BT12-072","EX1-073","EX1-073","EX1-073","EX1-073","EX3-013","EX9-073","EX9-073","BT11-092","BT11-092","BT11-092","BT11-092","EX9-068","EX9-068","BT9-102","BT9-102","BT9-102","BT9-102","BT15-096","BT15-096","BT15-096","BT15-096"]
```

### `digimoncardio`

[digimoncard.io](digimoncard.io) format.

```
// Digimon Deck List 
4 BlitzGreymon EX9-013
2 Blue Scramble LM-028
4 Gabumon BT15-020
2 Gabumon EX9-014
4 Gabumon (X Antibody) BT9-020
4 Garurumon BT15-024
2 Garurumon P-007
2 Garurumon (X Antibody) BT9-024
1 Garurumon (X Antibody) EX5-018
2 Matt Ishida BT15-083
2 Mental Training P-104
1 MetalGarurumon BT15-101
4 MetalGarurumon EX1-021
4 Omnimon Alter-S EX9-021
4 Tai Kamiya & Matt Ishida EX9-066
4 WereGarurumon: Sagittarius Mode EX9-019
4 Wisteria Memory Boost! LM-034
// Egg Deck 
1 Bukamon BT14-002
4 Wanyamon BT11-002
```

### `digimoncarddev`

[digimoncard.dev](digimoncard.dev) format.

```
// Digimon DeckList

1 DemiMeramon             BT15-006 
2 Myotismon ACE           BT15-076 
2 Mist Barrier            BT15-098 
2 Venom Infusion          BT15-099 
1 Cupimon                 BT16-006 
4 Arukenimon              BT16-072 
4 Mummymon                BT16-073 
4 MaloMyotismon           BT16-081 
4 Ukkomon                 BT16-082 
4 Arukenimon & Mummymon   BT16-089 
3 Impmon                  BT19-067 
1 DemiMeramon              BT3-006 
1 Gazimon                  BT3-077 
1 Psychemon                BT8-071 
3 Yukio Oikawa             BT8-093 
2 Mist Memory Boost!       BT8-108 
4 Myotismon               EX10-048 
2 Mummymon                EX10-051 
2 VenomMyotismon          EX10-054 
2 Yukio Oikawa            EX10-065 
1 Ukkomon                    P-123 
3 Myotismon (X Antibody)     P-145 
```

### `digimoncardapp`

[digimoncard.app](digimoncard.app) format.

```
// Digimon DeckList

BT11-005 Koromon 4
EX10-006 Agumon 4
BT8-058 Agumon 4
BT11-062 Agumon (X Antibody) 4
EX10-007 Greymon 4
ST15-08 Greymon 4
BT11-064 Greymon (X Antibody) 1
EX10-008 MetalGreymon 4
BT11-069 MetalGreymon (X Antibody) 3
EX10-010 BlackWarGreymon 2
BT8-070 BlackWarGreymon 2
BT11-074 BlackWarGreymon (X Antibody) 2
BT22-083 Yuuko Kamishiro 3
BT11-093 Yuuya Kuga 3
P-107 Defense Training 4
BT11-107 Hades Force 2
BT9-109 X Antibody 4
```

### `digimonmeta`

[DigimonMeta](https://digimonmeta.com/) format.

```
4 (BT22-002)
4 (ST19-03)
4 (EX7-024)
2 (EX9-024)
2 (BT22-029)
4 (P-165)
2 (EX7-025)
3 (EX9-027)
1 (BT20-084)
1 (ST19-11)
4 (EX9-032)
2 (BT22-036)
2 (EX7-030)
4 (EX9-033)
2 (BT22-042)
3 (P-136)
1 (EX7-063)
2 (EX9-067)
1 (BT22-088)
3 (P-105)
1 (EX7-074)
2 (BT22-098)
```

### `untap`

Untap format.

```
1 MetalTyrannomon                      (DCG) (BT11-055)
4 Analogman                            (DCG) (BT11-092)
1 Chaosdramon (X Antibody)             (DCG) (BT12-072)
4 DemiMeramon                          (DCG) (BT15-006)
1 Megadramon                           (DCG) (BT15-064)
4 Candlemon                            (DCG) (BT15-069)
4 Supreme Connection!                  (DCG) (BT15-096)
4 Ukkomon                              (DCG) (BT16-082)
1 Daipenmon                            (DCG) (BT18-026)
1 CannonBeemon                         (DCG) (BT18-052)
1 JetSilphymon                         (DCG) (BT18-053)
1 Vespamon                             (DCG) (BT19-052)
1 Cyberdramon                          (DCG) (BT19-062)
3 Tapirmon                              (DCG) (BT2-070)
1 MetalGreymon                          (DCG) (BT7-013)
1 MetalGreymon                          (DCG) (BT8-067)
4 Attack of the Heavy Mobile Digimon!   (DCG) (BT9-102)
4 Machinedramon                         (DCG) (EX1-073)
1 Chaosdramon                           (DCG) (EX3-013)
1 Gigadramon                            (DCG) (EX7-044)
1 MetalGreymon                          (DCG) (EX9-011)
1 MetalGreymon: Alterous Mode           (DCG) (EX9-012)
1 Andromon                              (DCG) (EX9-030)
1 MetalTyrannomon                       (DCG) (EX9-043)
1 Megadramon                            (DCG) (EX9-064)
2 Analogman                             (DCG) (EX9-068)
2 Machinedramon                         (DCG) (EX9-073)
1 Ukkomon                                 (DCG) (P-123)
1 Rapidmon                              (DCG) (ST17-07)
```