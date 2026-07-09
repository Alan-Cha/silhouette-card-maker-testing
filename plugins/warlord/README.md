# Warlord: Sage of the Storm Plugin

This plugin reads a decklist, automatically fetches card art from [WarlordCCGDB](https://warlordccgdb.com/) and puts them in the proper `game/` directories.

This plugin supports many decklist formats such as `text` and `untap`. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is Untap (`untap`).

Run the script.

```sh
python plugins/warlord/application/fetch.py game/decklist/deck.txt untap
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {text|untap}

Options:
  --help  Show this message and exit.
```

## Formats

### `text`

The Text export from [WarlordDB](https://www.warlorddb.com/)

```
Starting Army
3 TFK Brigand
1 Mair Haven
2 Crownland Strategist

Characters
3 Alaya
3 Birdsong Druid
1 Crownland Strategist
1 Oracle of Kavara
3 Graham Heyward
3 Huggins
1 Master Dresden
1 Blitzer
2 Thunic Yeti
1 Brightwing

Items
2 Merrick Regalia
1 Teufeltiger's Shroud
1 Storm Shard
2 Ardian Greathawk
3 Fatestring Bow
3 Shrapnelball

Actions
2 Pin Down
2 Swivel
3 Assassin's Strike
3 Meet at the Inn!
3 Crypt Wine
```

### `untap`

The Untap export from [WarlordCCGDB](https://warlordccgdb.com/)

```
1x Wa'San Wolf-Spirit
1x Draljaca Tar
2x Joleg
1x 'Mad' Pat Carrik
3x Catapult Crew
3x Kraig'dem
3x Makusog Steelhorn
2x Bloodsteed
2x Burning Scroll
1x Cloak of Brilliance
2x Darkflame Bolts
1x Kaballite Regalia
2x Nehil
3x Noble Sacrifice
3x Sutek Slimefang
3x Balian
3x Walk on Wind
2x Jubilant Hatchling
1x Greenflower Warden
1x Dissolve
1x Flamefall
2x Grave Exchange
1x Dreadfang
3x Magic Missiles
3x Flamelance
```