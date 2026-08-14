---
title: 'KeyForge'
weight: 65
---

This plugin reads a decklist, fetches the card images from the [Archon Arcana](https://www.archonarcana.com) wiki, and puts the card images into the proper `game/` directories.

This plugin supports decklist URLs from [Master Vault](https://www.keyforgegame.com) and [Decks of KeyForge](https://decksofkeyforge.com), as well as a plain list of cards. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the root directory as plugins are not meant to be run in the plugins directory.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here]({{% ref "../docs/create/#basic-usage" %}}) for more information.

Put your decklist into a text file in `game/decklist`. In this example, the filename is `deck.txt` and the decklist format is Master Vault (`master_vault_url`).

Run the script.

```sh
python plugins/keyforge/fetch.py game/decklist/deck.txt master_vault_url
```

Card images are always downloaded from Archon Arcana because it hosts higher-resolution art than Master Vault. Any cards that could not be found are reported together at the end.

> [!NOTE]
> Card enhancements (the æmber, capture, damage, and draw pips added to specific cards in a deck) are not currently handled, so enhanced cards are printed with their standard, unenhanced art.

Now you can create the PDF using [`create_pdf.py`]({{% ref "../docs/create" %}}). KeyForge uses the `standard` card size, which is the default.

```sh
python create_pdf.py
```

> [!TIP]
> KeyForge cards share a common card back, which you provide in `game/back/`. Blank card backs are available in the [keyteki repository](https://github.com/keyteki/keyteki/tree/master/client/assets/img/idbacks/idback_blanks).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {archon_arcana|master_vault_url|decks_of_keyforge_url}

Options:
  --help  Show this message and exit.
```

## Formats

### `master_vault_url`

Master Vault deck URL format.

```
https://www.keyforgegame.com/deck-details/4b86855f-71e5-4f54-a20d-2a58ec973f9c
```

You can also use a Master Vault URL directly in the command line.

```sh
python plugins/keyforge/fetch.py https://www.keyforgegame.com/deck-details/4b86855f-71e5-4f54-a20d-2a58ec973f9c master_vault_url
```

### `decks_of_keyforge_url`

Decks of KeyForge deck URL format.

```
https://decksofkeyforge.com/decks/4b86855f-71e5-4f54-a20d-2a58ec973f9c
```

You can also use a Decks of KeyForge URL directly in the command line.

```sh
python plugins/keyforge/fetch.py https://decksofkeyforge.com/decks/4b86855f-71e5-4f54-a20d-2a58ec973f9c decks_of_keyforge_url
```

### `archon_arcana`

A plain list of cards, one per line. Each card can be referenced as an Archon Arcana URL or a card name. Names are matched case-insensitively, and spaces and underscores are interchangeable, so all of the following refer to the same card:

```
https://www.archonarcana.com/wiki/Gracchan_Reform
Gracchan_Reform
Gracchan Reform
gracchan reform
```

Special characters can be written in plain ASCII: `AEmber Imp`, `Nature's Call`, and `Shae "Cloudkicker"` resolve to their `Æmber`, curly-apostrophe, and curly-quote spellings on Archon Arcana. Accents can be omitted too (for example, `Gezdrutyo the Arcane`), and if there is no exact match, the closest Archon Arcana search result is used as a last resort.
