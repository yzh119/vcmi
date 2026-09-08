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

## Layered 2x prototype

`build_layered_town.py` exports all 42 town definitions (100 frames) and three
map variants (3 frames) as a separate graphical mod. Optional `--background`
and `--castle` accept built-in image_gen outputs. The empty background becomes
1600×748; the castle interior is keyed from solid magenta and blended inside
the exact original alpha, retaining original pixels around uncertain edges.
Other assets use bicubic enlargement and mild unsharp masking, not invented
high-resolution detail. Every exported frame is reopened and checked against
its original canvas and nearest-scaled alpha.

```sh
tools/creature-art/.venv/bin/python tools/town-art/build_layered_town.py \
  --data "$HOME/Library/Application Support/vcmi/Data" \
  --out "$HOME/vcmi-art/necropolis-hd/layered-02" \
  --background "$HOME/vcmi-art/necropolis-hd/layer-input-02/background.png" \
  --castle "$HOME/vcmi-art/necropolis-hd/layer-input-02/castle-magenta.png"
```

The generated `mod` directory can be installed under a distinct Mods name.
It supplies only `data2x` and `sprites2x`; enable `video.useHdTextures` and use
2x rendering. Native resources remain the fallback at 1x. Area/border resources,
town configuration, upgrade chains and map templates are not overridden.
Town COLORKEY frames retain all palette colors except transparent index 0;
map frames have separate body/shadow/owner-overlay PNGs.

`CCastleBuildings::recreate` selects the furthest built upgrade in each base
building group. `CBuildingRect::operator<` compares z only, not y. The engine
still controls both behaviors. Copy `layer-review.html` to the output as
`index.html` and serve it over HTTP to inspect independent layers and all
effect frames (frame 0 is drawn as a base, like CShowableAnim::BASE).
The inspector deliberately permits impossible combinations and is not a
game-state emulator or evidence of in-game click/upgrade testing.
