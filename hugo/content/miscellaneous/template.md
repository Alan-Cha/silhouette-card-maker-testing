---
title: 'Create Templates'
---

This project already supports many [cutting templates]({{% ref "../_index.md#supported-sizes" %}}) but if you'd like to create your own, here's what you need to do.

### Create cutting template

Open Silhouette Studio and create a cutting template.

![Cutting template](/images/cutting_template_domino.png)

Use the **Transform tools** to ensure that the cards are aligned and evenly distributed.

![Transform tools](/images/transform_tools.png)

Save the template in `cutting_templates/`.

### Create square PDF

Modify the cutting template so that the corners of the cards are square.

![Square cards](/images/square_cards.png)

Fill the cards with black color.

![Black cards](/images/black_cards.png)

Disable print bleed. 

![Print bleed](/images/print_bleed.png)

Print the template to PDF.

![Print preview](/images/print_preview.png)

### Update `layouts.json`

[`assets/layouts.json`](https://github.com/Alan-Cha/silhouette-card-maker/blob/main/assets/layouts.json) contains the position of each cutting shape.

Import the square PDF into a photo editing software. The photo editing software should convert the PDF into a photo format. The photo must be 300 PPI.

![Photo editor](/images/photo_editor.png)

Determine the coordinates of the top left corner and the size of each card.

![Card_size](/images/card_size.png)

Create a new entry in `layouts.json`.

```diff
{
    "paper_layouts": {
        "letter": {
            "width": 3300,
            "height": 2550,
            "card_layouts": {
+               "domino": {
+                   "width": 524,
+                   "height": 1049,
+                   "x_pos": [
+                       245,
+                       817,
+                       1388,
+                       1959,
+                       2531
+                   ],
+                   "y_pos": [
+                       205,
+                       1296
+                   ],
+                   "template": "letter-domino-v1"
+               }
            }
        }
    }
}
```

### Update `utilities.py`

[`utilities.py`](https://github.com/Alan-Cha/silhouette-card-maker/blob/main/utilities.py) contains two enums which capture every card and paper size. Update these appropriately.

```diff
class CardSize(str, Enum):
    STANDARD = "standard"
    JAPANESE = "japanese"
    POKER = "poker"
    POKER_HALF = "poker_half"
    BRIDGE = "bridge"
+   DOMINO = "domino"    

class PaperSize(str, Enum):
    LETTER = "letter"
    TABLOID = "tabloid"
    A4 = "a4"
    A3 = "a3"
    ARCHB = "archb"
```

### Update Assets

If you're adding a new paper size, you also need to add new base images to [`assets/`](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/assets).

For example, for `letter` paper size, there are the following files:
* [`letter_blank.jpg`](https://github.com/Alan-Cha/silhouette-card-maker/blob/main/assets/letter_blank.jpg)
* [`letter_registration.jpg`](https://github.com/Alan-Cha/silhouette-card-maker/blob/main/assets/letter_registration.jpg)
* [`letter_registration.pdf`](https://github.com/Alan-Cha/silhouette-card-maker/blob/main/assets/letter_registration.pdf)

### Run `create_pdf.py`

Now you're ready to test out your new card and paper size!

```sh
python create_pdf.py --card_size domino
```

### Pull Request

A pull request is how external contributors can suggest changes.

Make a pull request to share your cutting template with the rest of the world!