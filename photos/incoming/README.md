# Drop folder for photographs that have to be fetched by hand

Some tools cannot be sourced automatically — the vendor blocks scripted access
(lowes.com answers HTTP 403 to curl and to any non-browser fetch), or the only
image available is shot at an angle. Save those here and they get built like
any other tool.

**Images in this folder are not committed.** `.gitignore` keeps everything here
except these two Markdown files out of git, which matters because these are
vendor product photographs: tracing one to derive geometry is fine, but
committing it would republish it. Same rule as the automated intake path —
only the traced outline reaches the repository.

## Naming

Save each file as the catalogue number, exactly as it appears in `MANIFEST.md`:

    photos/incoming/J213-9NE.jpg
    photos/incoming/D213-9NE.jpg

Any of `.jpg`, `.jpeg`, `.png`, `.webp` is fine — the pipeline reads the bytes,
not the extension. Nothing else in the name.

## What the photograph has to be

**Straight down, tool flat.** This is the one that actually matters. A
three-quarter "hero" shot traces perfectly and produces the wrong shape,
because the silhouette becomes the projection of a tilted tool. Two tells:

- you can see the *side* faces of the handles, not just the top
- one handle looks nearer the camera, or foreshortened, next to the other

If either is true, keep looking. **No image is better than an angled one** — an
angled one fails silently, and the overlay will look fine.

Also reject:

- badge, watermark or text graphics sitting on the image (Klein's own product
  shots carry a "Made in USA" badge, which traces as a second object)
- anything cropped at the frame edge
- hands, packaging, props, busy backgrounds

Prefer:

- plain white or uniform background
- a margin of clear background all the way round — tight crops are the single
  most common failure here, see below
- 1000 px or more on the short edge; 600 px is the hard floor

## Tight crops

Vendor images are often framed with only a pixel or two of background. The
segmenter needs background to work against, and without it the trace escapes
along the frame edge. In the first Klein batch this made 11053 come out
125.4 mm wide instead of 62.2 mm — it would have shipped as a 4x5 bin.

It is fixable: padding the canvas with the backdrop colour before tracing
recovered 11053, 63020, D248-8 and D203-6. Scale comes from `--length`, so
padding cannot move a dimension. If a photograph here is tightly cropped, say
so and it gets padded before tracing rather than rejected.

## Lengths

`MANIFEST.md` carries the overall length Klein publishes for each catalogue
number. Those are **nominal figures, not measurements taken off a tool.** The
whole model scales from that one number, so a bin that grips or rattles
*uniformly* means the published figure is wrong — not the outline, and not the
clearance. Do not absorb it into the clearance; see CLAUDE.md.

If you have the tool in hand, measure it and use that instead.
