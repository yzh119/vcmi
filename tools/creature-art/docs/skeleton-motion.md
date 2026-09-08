# Skeleton continuous motion

This extends the [four-pose study](skeleton-study.md) with curved limb shafts,
paired forearm/lower-leg bones and wider anatomical joint ends. Procedural bone
shading uses a rest-position attribute, so the surface noise follows the mesh.
The textured skull/chest/pelvis and source fingerprint remain the same. Hands
retain their fixed finger shapes and explicit right-hand weapon socket.

Five editable clips are generated: `HOLDING`, `MOVING`, `ATTACK_FRONT`,
`MOVE_START`, and `MOVE_END`. The attack includes anticipation, a lifted front
foot, wind-up, strike and recovery to holding. The rear foot stays planted.
Weapon orientations interpolate between key quaternions to avoid a hand-basis
flip as the forearm passes the blade direction. Start/end movement clips relocate
one foot at a time. Their endpoints join the authored phase-zero walk; arbitrary
interrupted movement still needs in-game review.

## Timing and foot contact

`client/battle/CreatureAnimation.cpp` sets melee attack playback to
`10 * speedFactor` frames/second. `attackAnimationTime` does not set melee timing.
Movement uses `10 * speedFactor / walkAnimationTime` frames/second and translates
at `2 * speedFactor / walkAnimationTime` hexes/second. An eight-frame movement
cycle therefore covers 1.6 hexes, or 70.4 pixels on a horizontal 44-pixel hex step.

The walk profile converts that displacement through the fixed orthographic
camera. During stance an ankle moves backward by exactly the corresponding
forward root displacement. Checks add the hypothetical root motion back and
measure the world ankle's drift. This checks straight horizontal movement;
diagonal paths, direction flips and interrupted cycles require engine review.

Dense review uses 30 fps, with key spans of 2 s holding, 0.8 s walk/attack and
0.2 s start/end. Nonloop videos retain the endpoint for one additional frame.
It is **not** substituted for the original sprite counts. Body exports retain
8/8/8/2/2 frames, at 450x400 and 900x800. Actual game speed still depends on its
animation settings. Loop exports omit the duplicate closure frame. Nonloop
exports include both endpoints.

Python `keyframe_insert` produced Bezier keys even with the UI preference set to
linear in Blender 5.2.1. Explicitly setting every Action key to linear reduced
measured stance drift at subframes from 0.008757 to 0.000061 model units
(about 0.47 to 0.0033 base pixels). Always test the saved Action at subframes.

## Reproduce

```sh
blender -b --python-exit-code 1 --python tools/creature-art/skeleton_motion.py -- \
  --model "$HOME/vcmi-art/skeleton-study/source/skeleton.glb" \
  --out "$HOME/vcmi-art/skeleton-motion/review-03"

blender -b --python-exit-code 1 --python tools/creature-art/test_skeleton_motion.py -- \
  "$HOME/vcmi-art/skeleton-motion/review-03"

tools/creature-art/.venv/bin/python tools/creature-art/motion_preview.py \
  "$HOME/vcmi-art/skeleton-motion/review-03" \
  --reference tools/creature-art/ref/cskele/body
```

Use a fresh output directory and do not edit sources during a render. `--no-render`
still calibrates the camera, bakes/saves all clips and records measurements, but
skips review and sprite frames. Each `.blend` contains ordinary editable native
Actions, IK controls, packed textures and a closure frame. The manifest retains
the source hash, both profiles, code hashes/snapshots, camera and measurements.

`test_skeleton_motion.py` reopens all five clips and checks 245 frame/subframe
samples for IK reach, saved-versus-authored positions, ground penetration,
weapon rigidity, straight-line stance drift, loop and transition endpoints,
rest-position attributes and embedded textures. Ground tolerance is 0.0002 model
units (about 0.011 base pixels), allowing numerical IK error.

`motion_preview.py` checks counts against the extracted original layout, canvas
dimensions and unclipped alpha bounds. It creates GIFs, scrub-able MP4s and
`preview/index.html`, plus an original/new contact sheet at actual 1x scale.
The contact sheet compares phases; it does not synchronize original game timing.

## Remaining skeleton work

Review the five clips artistically, including silhouette at native size and the
fixed free-hand pose. Complete `MOUSEON`, `HITTED`, `DEFENCE`, `DEATH`, `TURN_L`,
`TURN_R`, `ATTACK_UP` and `ATTACK_DOWN`, then render body/shadow/overlay
layers, assemble and validate the full mod, and inspect actual battles.
This body-only study is not installed as an incomplete replacement set.

The next creature is the zombie (`CZOMBI`). Reuse the inspection, explicit
handedness, controls, motion checks and render pipeline; zombie proportions and
gait need their own authored profile. A second character will inform whether the
Blender tooling warrants a separate repository. No new Meshy call was needed for
this skeleton stage.
