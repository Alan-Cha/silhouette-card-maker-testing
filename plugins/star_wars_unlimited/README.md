# Star Wars Unlimited Plugin

This plugin reads a decklist from [swudb](https://swudb.com/) and puts the card images into the proper `game/` directories.

This plugin currently supports the ``JSON``, ``Melee``, and ``Picklist`` formats.

## Instructions

Navigate to the [root directory](../..), as the plugins are not meant to be run in the [plugin directory](.).

Open a terminal on your device in the root directory.

> [!NOTE]
> On Windows, this would be the ``PowerShell`` application, unless you use another terminal of your choice.
>
> On MacOS or Linux, this would be the ``Terminal`` application, unless you use another terminal of your choice.

Create and start your Python virtual environment in the terminal.

> [!NOTE]
> Use the following command to create your Python virtual environment.
> ```bash
> python -m venv venv
> ```
>
> On Windows, use the following command to start your Python virtual environment.
> ```bash
> .\venv\Scripts\Activate.ps1
> ```
>
> On MacOS or Linux, use the following command to start your Python virtual environment.
> ```bash
> . venv/bin/activate
> ```

> [!WARNING]
> If this fails on Windows due to authorization policy issues, then run the following command to get around it.
> ```bash
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```

Then install the Python dependencies in the Python virtual environment using the following command.
```bash
pip install -r requirements.txt  
```

Put your decklist into a text file within the [decklist directory/folder](../../game/decklist).

Now, you are ready to run the program to generate the images for the deck using one of the following commands.
> If your deck is in the ``JSON`` format, then use the following command.
> ```bash
> python plugins/star_wars_unlimited/fetch.py game/decklist/deck.txt json
> ```
> If your deck is in the ``Melee`` format, then use the following command.
> ```bash
> python plugins/star_wars_unlimited/fetch.py game/decklist/deck.txt melee
> ```
> If your deck is in the ``Picklist` format, then use the following command.
> ```bash
> python plugins/star_wars_unlimited/fetch.py game/decklist/deck.txt picklist
> ```

And finally, you can generate the [PDF files](../../README.md#create_pdfpy) for the deck to print so that you can play at the table!

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {json|melee|picklist}

Options:
  --help  Show this message and exit.
```

## Format

### `json`

The format for ``JSON``.

```
{
  "metadata": {
    "name": "Wichita PQ - 4th",
    "author": "aces"
  },
  "leader": {
    "id": "SOR_017",
    "count": 1
  },
  "base": {
    "id": "TWI_029",
    "count": 1
  },
  "deck": [
    {
      "id": "SOR_203",
      "count": 3
    },
    {
      "id": "SHD_202",
      "count": 3
    },
    {
      "id": "SOR_211",
      "count": 2
    },
    {
      "id": "SOR_200",
      "count": 3
    },
    {
      "id": "TWI_226",
      "count": 3
    },
    {
      "id": "SOR_201",
      "count": 3
    },
    {
      "id": "SHD_231",
      "count": 3
    },
    {
      "id": "TWI_198",
      "count": 2
    },
    {
      "id": "SHD_203",
      "count": 2
    },
    {
      "id": "SHD_174",
      "count": 3
    },
    {
      "id": "SHD_204",
      "count": 2
    },
    {
      "id": "SOR_202",
      "count": 2
    },
    {
      "id": "SHD_197",
      "count": 3
    },
    {
      "id": "SHD_213",
      "count": 3
    },
    {
      "id": "SOR_193",
      "count": 3
    },
    {
      "id": "SHD_200",
      "count": 3
    },
    {
      "id": "SHD_248",
      "count": 3
    },
    {
      "id": "TWI_196",
      "count": 2
    },
    {
      "id": "SOR_198",
      "count": 2
    }
  ],
  "sideboard": [
    {
      "id": "SOR_195",
      "count": 2
    },
    {
      "id": "SHD_055",
      "count": 1
    },
    {
      "id": "SHD_219",
      "count": 2
    },
    {
      "id": "SHD_207",
      "count": 2
    },
    {
      "id": "SOR_199",
      "count": 3
    }
  ]
}
```

### `melee`

The format for ``Melee``.

```
Leaders
1 | Han Solo | Audacious Smuggler

Base
1 | Level 1313

Deck
3 | Hotshot DL-44 Blaster
3 | L3-37 | Droid Revolutionary
3 | Spark of Rebellion
3 | Surprise Strike
3 | Bodhi Rook | Imperial Defector
3 | DJ | Blatant Thief
3 | Liberated Slaves
3 | Millennium Falcon | Piece of Junk
3 | Tech | Source of Insight
3 | Waylay
2 | Gamorrean Guards
3 | Qi'ra | Playing Her Part
3 | Cunning
2 | Cantina Bouncer
2 | Plo Koon | Koh-to-yah!
2 | Zorii Bliss | Valiant Smuggler
2 | Millennium Falcon | Lando's Pride
2 | Enfys Nest | Champion of Justice
2 | Han Solo | Reluctant Hero

Sideboard
1 | Moisture Farmer
2 | A New Adventure
3 | Bamboozle
2 | Auzituck Liberator Gunship
2 | Enfys Nest | Marauder
```

### `picklist`

The format for ``Picklist``.

```
[ ]          Han Solo | Audacious Smuggler
             SOR 017, SOR 283, SOR 267

[ ]          Level 1313
             TWI 029, TWI 518

[ ] [ ] [ ]  Millennium Falcon | Piece of Junk
             SOR 193, SOR 455

[ ] [ ]      Auzituck Liberator Gunship
             SOR 195, SOR 457

[ ] [ ]      Han Solo | Reluctant Hero
             SOR 198, SOR 460, P25 43

[ ] [ ] [ ]  Bamboozle
             SOR 199, SOR 461

[ ] [ ] [ ]  Spark of Rebellion
             SOR 200, SOR 462

[ ] [ ] [ ]  Bodhi Rook | Imperial Defector
             SOR 201, SOR 463

[ ] [ ]      Cantina Bouncer
             SOR 202, SOR 464

[ ] [ ] [ ]  Cunning
             SOR 203, SOR 465

[ ] [ ]      Gamorrean Guards
             SOR 211, SOR 473

[ ]          Moisture Farmer
             SHD 055, SHD 330

[ ] [ ] [ ]  Hotshot DL-44 Blaster
             SHD 174, SHD 443

[ ] [ ] [ ]  L3-37 | Droid Revolutionary
             SHD 197, SHD 465

[ ] [ ] [ ]  Liberated Slaves
             SHD 200, SHD 468

[ ] [ ] [ ]  Qi'ra | Playing Her Part
             SHD 202, SHD 470

[ ] [ ]      Zorii Bliss | Valiant Smuggler
             SHD 203, SHD 471

[ ] [ ]      Millennium Falcon | Lando's Pride
             SHD 204, SHD 472, SHDOP 16

[ ] [ ]      A New Adventure
             SHD 207, SHD 475

[ ] [ ] [ ]  DJ | Blatant Thief
             SHD 213, SHD 481

[ ] [ ]      Enfys Nest | Marauder
             SHD 219, SHD 487, SHDOP 15

[ ] [ ] [ ]  Surprise Strike
             SOR 220, SOR 482, SHD 231, SHD 498

[ ] [ ] [ ]  Tech | Source of Insight
             SHD 248, SHD 510

[ ] [ ]      Plo Koon | Koh-to-yah!
             TWI 196, TWI 461

[ ] [ ]      Enfys Nest | Champion of Justice
             TWI 198, TWI 463

[ ] [ ] [ ]  Waylay
             SOR 222, SOR 484, SOROP 03, TWI 226
```