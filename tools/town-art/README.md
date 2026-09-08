# Necropolis town-art study

Extract original town layers and adventure-map town variants before changing
resolution. The town background is TBNCBACK.PCX, 800×374. The faction config
contains 42 structure definitions, including upgrade stages and overlays.
The reference exporter composes 23 selected fully upgraded layers at their
configured positions. It is a reference layout, not a game-state screenshot.

The three map templates use AVCNECR0 (village), AVCNECX0 (fort/citadel/castle) and
AVCNECZ0 (capitol). Each original has a 192×192 canvas and one frame. Raw decoding
preserves the original canvas/margins and indexed shadow alpha. Generated assets
live outside the source repository.

```sh
tools/creature-art/.venv/bin/python tools/town-art/export_necropolis_reference.py \
  --data "$HOME/Library/Application Support/vcmi/Data" \
  --out "$HOME/vcmi-art/necropolis-hd/reference-01"
```

The first HD comparison uses built-in `image_gen`, with the extracted full-town
reference and fortified map castle as edit targets. Prompts are retained with
the generated outputs under `~/vcmi-art/necropolis-hd/review-01`. This pass is a
visual study, not an installed replacement pack. The town output is a flattened
1832×858 panorama; it cannot represent arbitrary unbuilt/upgraded town states.
The first castle output was RGB with a painted checkerboard, which is not alpha
transparency and must not be installed as a game sprite.

Integration needs separate background, building and effect assets, preserving
`config/factions/necropolis.json` positions, z-order, upgrade relationships and
area/border masks. Map images must preserve canvas, anchor, footprint and owner
color handling. `clientsdl2/render/RenderHandler.cpp::loadScaledImage` supports
DATA2X/3X/4X and SPRITES2X/3X/4X, gated by `video.useHdTextures`.
High-resolution files must match the scale of their logical canvas; a larger
PNG alone does not satisfy that contract. Keep preview images separate from
installable assets until registration, alpha and state-dependent layers pass.
