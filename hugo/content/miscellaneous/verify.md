---
title: 'Verify Templates'
weight: 20
---

If you wanted to manually verify the alignment of the PDF against the cutting template, here's how you'd do it.

## Instructions

Create a PDF using your desired options and the `--output_images` option, which will generate images instead of a PDF.

```sh
python create_pdf.py --output_images
```

The result are images named `page1.png`, `page2.png`, etc. They are 300 PPI so they can be imported easily into Silhouette Studio.

![Created image](/images/verify_image.png)

Open the appropriate cutting template in Silhouette Studio.

![Raw cutting template](/images/verify_template.png)

Select the cutting paths and change the color to something that is easier to see.

![Change cutting path color](/images/verify_color.png)

From your file manager (Finder or File Explorer), drag the image into Silhouette Studio.

![Import image](/images/verify_import.png)

Send the image to the back so the image does not cover the cutting paths.

![Change order](/images/verify_back.png)

Center the image using the `Center to Page` button.

![Center image](/images/verify_center.png)

Manually verify the alignment.

![Close up](/images/verify_close.png)
