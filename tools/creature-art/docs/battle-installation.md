# Skeleton and walking-dead battle installation

The reviewed bodies are now assembled as `necropolis-creature-animations`, a
separate local graphical mod. Source animations are unchanged:

- CSKELE: `~/vcmi-art/skeleton-motion/full-review-03`, 13 groups, 82 frames per scale.
- CZOMBI: `~/vcmi-art/zombie-study/full-review-01`, 13 groups, 80 frames per scale.

Both 1x and 2x are included (324 body PNGs). These are the unupgraded skeleton
and walking dead. CWSKEL and CZOMLO upgrades, portraits and adventure-map graphics
are not replaced. In-game testing should use unupgraded stacks in battle.

The initial 0.1.0 package asked the engine to derive sheared shadows (`generateShadow: 2`) for every group and
hover outlines (`generateOverlay: 1`) for holding/mouseon. This uses the new body
alpha rather than stale original shadow shapes. It is the engine's simplified
projection, not a Blender shadow-catcher pass. Both SDL backends support these
sequence fields; see `new_creature_mod.py` and `SharedImageLocator`.

Reproduce the animation JSONs with the existing scaffold tool:

```sh
python3 tools/creature-art/new_creature_mod.py \
  --mod-dir "$HOME/vcmi-art/creature-game-01/mod" --creature CSKELE \
  --from-def "$HOME/Library/Application Support/vcmi/Data/H3sprite.lod" \
  --generate-shadow 2 --generate-overlay
python3 tools/creature-art/new_creature_mod.py \
  --mod-dir "$HOME/vcmi-art/creature-game-01/mod" --creature CZOMBI \
  --from-def "$HOME/Library/Application Support/vcmi/Data/H3sprite.lod" \
  --generate-shadow 2 --generate-overlay
```

Copy each source's `sprites1x/*.png` to `content/Sprites/creatures/cskele/` or
`czombi/`, and `sprites2x/*.png` to the corresponding `content/Sprites2x` directory.
Keep every filename unchanged. Verify copied bytes against the source before
running:

```sh
tools/creature-art/.venv/bin/python tools/creature-art/validate_creature_animation.py \
  "$HOME/vcmi-art/creature-game-01/mod" \
  --lod "$HOME/Library/Application Support/vcmi/Data/H3sprite.lod" --json
```

The installed package passes with zero errors, zero warnings and 42 informational
motion findings. Frame counts and 450×400 / 900×800 canvases match the original
DEFs. Original unused duplicate groups 9/10 are omitted by the scaffold tool.
`~/vcmi-art/creature-game-01/provenance.json` records all copied body hashes and
the source manifest hashes; `validation.json` contains the complete findings.

The mod was copied into the user VCMI Mods directory, added to the active preset,
and a fresh client reported `Loading mod: OK (necropolis-creature-animations)`.
This is native loading verification, not proof of all battle animation timing,
contact, shadow or selection behavior. Existing online previews remain body-only.

## Skeleton canvas registration (0.2.0, mod only)

The user reported the creature information portrait was right-aligned, then
clarified this was a creature showcase issue. CCreaturePic crops single-hex creatures at x=150 in a
100-pixel window, so a new silhouette centered at x=224.5 appeared at x=74.5.

The user explicitly requested a mod-only solution. All provisional engine/schema
changes were reverted. `offset_animation.py` instead shifts all 164 skeleton PNGs
left 25 logical pixels (50 at 2x), retaining fixed canvases, frame counts and every
visible pixel. No creature configuration override is needed. The unchanged preview
crop now places the silhouette at x=49.5. This also changes the body position within
the battle canvas: the holding-frame bottom-band mean X goes from 219.2 to 194.2,
compared with 196.5 in the original. It is not a preview-only transformation.

```sh
tools/creature-art/.venv/bin/python tools/creature-art/offset_animation.py \
  --source-mod "$HOME/vcmi-art/creature-game-01/mod" \
  --out "$HOME/vcmi-art/creature-game-02/mod" --creature CSKELE --offset-x -25
```

The tool checks translated content byte-for-byte and alpha histograms, rejecting
any visible clipping. Revalidation still has zero errors/warnings. Zombie frames
and animation JSONs are byte-identical. Engine-generated effects follow the shifted
body alpha. Package 0.2.0 records this registration; restart VCMI to clear old cached
images. Authoring exports and their existing online animation galleries remain
unchanged; `creature-game-02` holds the corrected installation and provenance.

## Precomputed effects (0.3.0, mod only)

The user observed stuttering on first display that went away after caching.
`bake_effects.cpp` calls the existing SDL3 `drawShadow` and `drawOutline` functions
in a standalone offline executable. It produces 324 shadows and 72 idle/hover
outlines alongside the 324 unchanged registered body PNGs. Full canvases and all
frame counts remain intact. The animation JSONs no longer request runtime effect
generation. The standard loader finds `-shadow.png` and `-overlay.png` and can
trim their transparent padding internally, preserving the logical canvas.

Build the helper against the already-built SDL3 object and facade (macOS example):

```sh
c++ -std=c++20 -O2 -I/opt/homebrew/include \
  tools/creature-art/bake_effects.cpp \
  build/clientsdl3/CMakeFiles/vcmisdl3.dir/render/SDL_Extensions.cpp.o \
  -L/opt/homebrew/lib -lSDL3 -lSDL3_image -ltbb \
  -Lbuild/bin -lvcmi -Wl,-dead_strip -Wl,-rpath,"$PWD/build/bin" \
  -o /tmp/bake_effects
/tmp/bake_effects bake "$HOME/vcmi-art/creature-game-03/mod"
/tmp/bake_effects verify "$HOME/vcmi-art/creature-game-03/mod"
```

Copy the registered 0.2.0 package to a new output before baking. The helper expects
this pipeline's body filenames without hyphens, and holding_/mouseon_ names for
outline groups. After baking succeeds, remove `generateShadow` and
`generateOverlay` from all four animation JSONs, then validate the final mod.
Do not remove these fields before effect generation finishes. `verify` regenerates
and compares every saved effect pixel. `generated` and `prebaked` benchmark body
loading with either computed or loaded effects; neither mode writes assets.

The engine sources and binaries retain their normal implementation. Restart VCMI
to load the updated assets instead of the active process's cache. This removes
runtime effect computation; PNG decoding, scaling and GPU upload still occur.

On this machine, one fresh-process sweep of all 324 body frames and 396 effects
at both scales took 203,810 ms when generating effects, versus 513.249 ms loading
precomputed PNGs (a second fresh-process load took 491.436 ms). The sweep eagerly
visits the complete package; the game loads frames as needed. OS disk cache was
not flushed. These numbers exclude game startup, GPU upload and engine trimming,
so they are not an end-to-end cold-start speedup. The report is stored at
`~/vcmi-art/creature-game-03/benchmark.json`.

All 396 saved effects passed pixel-for-pixel comparison with regenerated native
surfaces. All 720 PNGs have nonempty alpha and original full canvas sizes. All four
animation JSONs differ from 0.2.0 only by removal of generation flags. The final
validator reports zero errors/warnings and 42 informational motion findings.
Installation 0.3.0 is byte-verified, with 0.2.0 backed up; the running game was not
restarted. `effects-manifest.json` and `effect-verification.json` record this audit.

## Creature showcase backgrounds (0.5.0)

Necropolis uses `CRBKGNEC` (100x130) and `TPCASNEC` (100x120) behind its creature
showcases. `package_backdrop.py` adds eight PNG resources in Data/Data2x/Data3x/
Data4x, preserving those logical sizes. A built-in image_gen edit of the original
background supplies detailed masonry, mountains and cracked ground. The smaller
variant crops the bottom ten logical pixels from the shared master, retaining
the horizon. This preserves the reference composition approximately; it is new
painted detail, not recovery of missing original pixels.

```sh
tools/creature-art/.venv/bin/python tools/creature-art/package_backdrop.py \
  --source-mod "$HOME/vcmi-art/creature-game-03/mod" \
  --master "$HOME/vcmi-art/creature-backdrop-02/generated.png" \
  --out "$HOME/vcmi-art/creature-backdrop-02/mod" --version 0.5.0
```

The 728 existing source files are checked byte-for-byte before updating mod.json.
No animation, shadow, outline or registration changes. All eight background PNGs
pass size and pixel round-trip checks; the creature validator still reports zero
errors/warnings and 42 informational findings. Offline showcase composites use the
actual crop and saved shadow layers, and are not native screenshots. Package 0.5.0
is installed with the initial backdrop package 0.4.0 backed up. Restart the running game to refresh its cache.
No engine or faction configuration changes. Both backgrounds apply to all
Necropolis creatures, including original upgraded units; other factions are untouched.

Master, exact prompt, comparison and provenance: `~/vcmi-art/creature-backdrop-02`.

A second built-in image edit sharpens masonry and ground detail following user
feedback. Both generated masters are 1100x1430; the improvement is in painted
edge/detail definition, not a larger returned image. The requested 2000x2600 size
was not honored by the tool. Review the actual 200x260 comparison before attributing
quality to the prompt dimensions. All eight backgrounds use the refined master.

### Small-panel readability (0.6.0)

The user clarified that the remaining sharpness gap was in the offline creature
composite, not an observation of game resource loading. No runtime loading defect
has been established. A third built-in image edit reduces gravel/soil mottling,
clarifies larger rock planes and separates ground cracks. Review uses the same
200x260 background dimensions and identical creature/shadow crops on both sides.
Separate 440-pixel-wide two-column skeleton and walking-dead figures replace the
wide five-column figure for this comparison; these remain offline composites.

Build with the same command using `creature-backdrop-03` and `--version 0.6.0`.
All eight 1x-4x backgrounds are replaced. The master remains 1100x1430. Existing
animation PNGs and JSONs are byte-identical to installed 0.5.0, and final validation
has zero errors/warnings. Package 0.6.0 is installed with 0.5.0 backed up under
`~/vcmi-art/creature-backdrop-03/installed-05-backup`. Source, prompt, two comparison
figures, provenance and validation are in `creature-backdrop-03`.
