# Skeleton and walking-dead battle installation

The reviewed bodies are now assembled as `necropolis-creature-animations`, a
separate local graphical mod. Source animations are unchanged:

- CSKELE: `~/vcmi-art/skeleton-motion/full-review-03`, 13 groups, 82 frames per scale.
- CZOMBI: `~/vcmi-art/zombie-study/full-review-01`, 13 groups, 80 frames per scale.

Both 1x and 2x are included (324 body PNGs). These are the unupgraded skeleton
and walking dead. CWSKEL and CZOMLO upgrades, portraits and adventure-map graphics
are not replaced. In-game testing should use unupgraded stacks in battle.

The engine derives sheared shadows (`generateShadow: 2`) for every group and
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
