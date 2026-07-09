# Elestrals Plugin

This plugin reads a decklist, fetches the card image from [Elestrals](https://collect.elestrals.com/cards), and puts the card images into the proper `game/` directories.

This plugin supports the `edk` format. To learn more, see [here](#formats).

## Basic Instructions

Navigate to the [root directory](../..) as plugins are not meant to be run in the [plugin directory](.).

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-usage) for more information.

Put your decklist into a text file in [game/decklist](../game/decklist/). In this example, the filename is `deck.txt` and the decklist format is EDK (`edk`).

Run the script.

```sh
python plugins/elestrals/application/fetch.py game/decklist/deck.txt edk
```

Now you can create the PDF using [`create_pdf.py`](../../README.md#create_pdfpy).

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {edk}

Options:
  --help  Show this message and exit.
```

## Formats

### `edk`

EDK format uses the EDK output from [BuildElestrals](https://buildelestrals.com/), [ClashNet](https://thelawtcg.github.io/ClashNet/), and [TopElestrals](https://www.topelestrals.com/).

```
{
  "name": "Cbach66 - Premier Webcam Tournament (Hosted by Elestrals) - 05-02-2026",
  "mainDeck": [
    {
      "card": "cd-1674"
    },
    {
      "card": "cd-298"
    },
    {
      "card": "cd-1713"
    },
    {
      "card": "cd-1713"
    },
    {
      "card": "cd-1713"
    },
    {
      "card": "cd-295"
    },
    {
      "card": "cd-295"
    },
    {
      "card": "cd-221"
    },
    {
      "card": "cd-221"
    },
    {
      "card": "cd-715"
    },
    {
      "card": "cd-259"
    },
    {
      "card": "cd-259"
    },
    {
      "card": "cd-348"
    },
    {
      "card": "cd-348"
    },
    {
      "card": "cd-1787"
    },
    {
      "card": "cd-1787"
    },
    {
      "card": "cd-1787"
    },
    {
      "card": "cd-284"
    },
    {
      "card": "cd-284"
    },
    {
      "card": "cd-340"
    },
    {
      "card": "cd-340"
    },
    {
      "card": "cd-340"
    },
    {
      "card": "cd-560"
    },
    {
      "card": "cd-560"
    },
    {
      "card": "cd-277"
    },
    {
      "card": "cd-277"
    },
    {
      "card": "cd-277"
    },
    {
      "card": "cd-1788"
    },
    {
      "card": "cd-476"
    },
    {
      "card": "cd-476"
    },
    {
      "card": "cd-440"
    },
    {
      "card": "cd-322"
    },
    {
      "card": "cd-322"
    },
    {
      "card": "cd-322"
    },
    {
      "card": "cd-1804"
    },
    {
      "card": "cd-1804"
    },
    {
      "card": "cd-1804"
    },
    {
      "card": "cd-1784"
    },
    {
      "card": "cd-1784"
    },
    {
      "card": "cd-841"
    }
  ],
  "spiritDeck": [
    {
      "card": "cd-241"
    },
    {
      "card": "cd-241"
    },
    {
      "card": "cd-241"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    },
    {
      "card": "cd-228"
    }
  ],
  "sideDeck": [
    {
      "card": "cd-1694"
    },
    {
      "card": "cd-1694"
    },
    {
      "card": "cd-288"
    },
    {
      "card": "cd-298"
    },
    {
      "card": "cd-560"
    },
    {
      "card": "cd-303"
    },
    {
      "card": "cd-303"
    },
    {
      "card": "cd-591"
    },
    {
      "card": "cd-482"
    },
    {
      "card": "cd-482"
    },
    {
      "card": "cd-482"
    },
    {
      "card": "cd-841"
    },
    {
      "card": "cd-361"
    },
    {
      "card": "cd-361"
    },
    {
      "card": "cd-361"
    }
  ]
}
```