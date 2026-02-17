---
title: 'Troubleshooting'
weight: 1000
---

## Do I need to laminate my cards?

No. Lamination provides a lot of advantages like durability, water resistance, shuffleability, and card feel, but it's not necessary. However, if you're planning on using a cutting machine to help with another workflow that doesn't require lamination, you don't need to do so.

## Are laminated cards similar to mass produced cards?

It depends on the weight of your card stock and the thickness of your lamination, but from personal experience with 110 lb card stock and 3 mil lamination, I think it's very similar to mass produced cards.

If I had to say anything, I would say this combination is only marginally thicker than mass produced card but if you plan on using card sleeves and playing with a mix of both, I would say it's almost indistinguishable.

## Can I make double-sided cards?

Yes, the `create_pdf.py` script has many other features including laying out double-sided cards. To see the full documentation, please see [here]({{% ref "../docs/create.md#double-sided-cards" %}}).

Long story short, put the fronts in the `game/front/` folder and the backs in the `game/double_sided/` folder. The filenames (and file extensions) must match for each pair. Then, simply run `create_pdf.py` as usual.

## Do you have printer recommendations?

See the [Equipment]({{% ref "supplies.md#equipment" %}}) section.

## Why are my card delaminating?

Are you using a laser printer? The laser toner sticks to the lamination, which prevents the lamination from sticking to the paper. Laser printing can work with this process, but you'll have to be gentler with the cards while cutting and while playing.

Try laminating a second time or laminating at a higher setting before cutting. Because card stock is thicker than printer paper, you need to use more heat to get proper lamination. Additionally, this will help to clear up any cloudiness in your lamination, making your cards look better in the end.

## Why are my cards wavy?

Set your laminator to a lower setting. It's adding too much heat, causing the lamination to contract more than needed.

Alternatively, immediately put the laminated sheets under a heavy book to let them cool down flat.

## Why is the registration failing?

Ensure that there is nothing blocking the registration sensor.

Ensure that the sheets are generated with the right template and printed with 100% scale.

Ensure the sheet is placed correctly on the mat and the mat is placed correctly in the machine. The sheet placement should match the cutting template.

Playing around with the lighting. If the room is too bright or too dark, the machine may have issues. Try shining a light at the sensor to provide more lighting. Try closing the cover as well.

Registration can fail when the machine scans something other than the registration marks. To prevent this, use Post-It notes to cover up the cards closest to the L registration marks. In my experience, you only need to do this for the L registration mark that gets scanned after the square. You can peel off the Post-It note after registration. You can use masking tape or a piece of paper with tape as well.

![No Post-It](/images/registration_fix.jpg)
![With Post-It](/images/registration_fix2.jpg)

If none of the previous tips worked, the issue may be your choice of paper, lamination, or printing.

## Why is the registration failing on foil paper?

The reflectivity of the foil paper can affect the registration process.

There are a few solutions you can try.

The first solution is to apply matte clear tape over the registration marks. This can diffuse the reflections while allowing the registration marks to be scannable.

The second solution to apply opaque tape where the registration marks would be and printing on the paper after it's been taped. This allows the registration marks and the nearby area to be nonreflective.

## Why didn't my machine cut all the way through?

Did you configure your cutting settings? The cutting templates do not contain cutting settings. You must add your settings manually. To learn more, see [here]({{% ref "guide.md#cutting-settings" %}}). 

If you configured you cutting settings, then try adjusting your settings by adding more force or more passes. If you are still having issues, try using a new blade and/or mat.

## Why is my machine cutting in the wrong place?

Make sure you're using the right cutting template. Each sheet should be labeled with the cutting template it's associated with, for example "letter-bridge-v1".

## Why did my cards come out diagonally?

Make sure your machine's pinch rollers are set to the right position. The pinch rollers should grip both sides of the mat.

Registration can fail or be adversely affected when the machine scans something other than the registration marks. As described in [Why is the registration failing?](#why-is-the-registration-failing), employ the Post-It trick.

## Why is the mat slipping during cutting?

Your machine uses two pinch rollers to grip the mat. Check if that is the case. If not, adjust their positions so they do.

## Why are my cards offset?

If either the fronts or the backs are offset, then there's most likely an issue with your printer alignment. Refer to your printer's instruction manual and try to recalibrate it. If there's no way to change the printer's settings, try using [offset.py]({{% ref "../docs/offset.md" %}}) to compensate for the offset.

If both the fronts and backs are offset, then there may be an issue with registraion. Ensure that you are printing with the right scale and cutting with the right cutting template, and ensure that there's nothing that can interfere with the registration process.

## Why are my cards the wrong size?

Some printers secretly add an offset to your prints, even if they are set to 100% scale or actual size. You may need to do some manual calibration in order to have your cards print and be cut out at the right size.

## Why does the PDF have a lower image resolution? Why are there image artifacts?

The default quality is lossy. You can maximize the resolution by using `--quality 100` option. See [here]({{% ref "../docs/create.md" %}}) for more information.