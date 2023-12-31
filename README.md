# Advanced Slides Postprocessor -- IDEA DRAFT

This is a post processing utility for the [Advanced Slides](https://github.com/MSzturc/obsidian-advanced-slides) slide export.

[Advanced Slides](https://github.com/MSzturc/obsidian-advanced-slides) allows to create quite nice slides directly from within obsidian. For my workflow there is just one feature missing, which is the integration of `html` figures created with [plotly](https://plotly.com/).

This script will add the `plotly.js` code to the plugins directory and replace images in the `index.html` which is generate by the [Advanced Slides](https://github.com/MSzturc/obsidian-advanced-slides).

## Installation

Via `pip`:

```bash
pip install asp
```

## How to use

Within your `slide.md` simply add an `html` comment line above your image import:

```md
<!-- asp:/path/to/my/figure.html -->

![[my-image.png]]
```

Then export the slides as usual.

Next, use the post processing script to add the plotly library and adjust the `index.html` file:

```bash
python -m asp /path/to/slide/index.html
```

This will also adjust the content in `index.html` to include `plotly.js`, and will replace the positions of the images will calls to render the plotly figures from a `json` payload. This image `json` data is extracted from the file specified in the comment path

## Development status

[ ] tested with a single plot, test with multiple next
