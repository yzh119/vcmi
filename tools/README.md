# tools

Developer tooling. Nothing here is installed with the game or loaded by the engine —
`CMakeLists.txt` installs `config/`, `scripts/` and `Mods/`, not this directory.

| | |
|---|---|
| [`creature-art/`](creature-art/) | Produce replacement creature battle animations, and check they will actually work in the engine. |

---

## creature-art in five minutes

Everything below is read-only against your own installed game data. Nothing is
modified, and no original art is redistributed.

### Setup

```bash
cd tools/creature-art
export LOD=~/"Library/Application Support/vcmi/Data/H3sprite.lod"   # macOS
pip install pillow                                                  # optional, see below
```

Pillow is required by `preview.py`, and enables anchor-drift analysis in the
validator. Everything else runs on a stock Python 3.8+.

The archive lives wherever VCMI keeps your imported Heroes III files — on Linux
`$HOME/.local/share/vcmi/Data/`, on Windows `%USERPROFILE%\Documents\My Games\vcmi\Data\`.
See [Installation_Linux](../docs/players/Installation_Linux.md) and
[Installation_Windows](../docs/players/Installation_Windows.md).

### 1. Look at what you are replacing

```bash
python3 preview.py sheet --lod "$LOD" --def CSKELE.DEF --group HOLDING \
    --anchor --numbers --out holding.png
```

A contact sheet of the skeleton's idle loop. The red line is the ground line the
engine anchors to; all eight frames sit exactly on it. Use `anim` instead of `sheet`
for a GIF — bobbing is invisible in stills.

### 2. Get its numbers

```bash
python3 def_extract.py info "$LOD" CSKELE.DEF --anchor
```

Canvas size, animation groups, frame counts, and the ground line per group. This is
the brief your renders have to hit: `CSKELE` is **450x400** with the ground line at
**y = 267**.

### 3. Scaffold a mod

```bash
python3 new_creature_mod.py --mod-dir ~/vcmi-mods/hd-creatures \
    --creature CSKELE --from-def "$LOD" --scales 1,2
```

Writes `mod.json`, the per-scale animation JSON, the empty frame directories, and a
render manifest listing every filename your renderer must produce. `--from-def` takes
the canvas and frame counts from the original, so nothing is typed by hand.

### 4. Produce the art

Not automated yet — this is the part still being built. Whatever produces the frames
(3D render, hand-painted, upscaled) must write them into the directories step 3
created, at that exact canvas and ground line, in three layers:

```
holding_00.png            the creature
holding_00-shadow.png     its ground shadow
holding_00-overlay.png    white silhouette, for the mouse-hover highlight
```

To see the original's three layers separated, so you know what you are matching:

```bash
python3 def_extract.py export "$LOD" CSKELE.DEF --out ref/cskele
python3 preview.py layers --lod "$LOD" --def CSKELE.DEF --group HOLDING --frame 0
```

### 5. Check it

```bash
python3 validate_creature_animation.py ~/vcmi-mods/hd-creatures
```

Catches the mistakes the engine will not report: frames on inconsistent canvases,
scale variants that disagree, missing overlay layers, indexed PNGs, and creatures
that slide inside their canvas. Exits non-zero on any error.

Then look at the result next to the original:

```bash
python3 preview.py compare --lod "$LOD" --def CSKELE.DEF \
    --mod ~/vcmi-mods/hd-creatures --creature CSKELE --group HOLDING --out compare.png
```

Steps 4 and 5 are the loop. Steps 1–3 you do once per creature.

---

## Where to read next

- [`creature-art/README.md`](creature-art/README.md) — the reference: every engine
  layout constraint, with the code that enforces it. Read this before producing art,
  because most of these rules fail silently rather than erroring.
- [`creature-art/docs/asset-generation-survey.md`](creature-art/docs/asset-generation-survey.md)
  — survey of 3D/2D/upscaling services, and the recorded project decisions.

## A note on redistribution

Heroes III assets are proprietary. `def_extract.py` reads *your* installed copy so
you have something exact to match against; the exported frames are reference, not
input to a generator and not redistributable. Original replacement art that happens
to fit H3's layout is yours to publish as a normal mod.
