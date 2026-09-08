# Skeleton continuous motion

This extends the [four-pose study](skeleton-study.md) with curved limb shafts,
paired forearm/lower-leg bones and wider anatomical joint ends. Procedural bone
shading uses a rest-position attribute, so the surface noise follows the mesh.
The textured skull/chest/pelvis and source fingerprint remain the same. Hands
retain their fixed finger shapes and explicit right-hand weapon socket.

Thirteen editable clips are generated, totaling 82 original-count body frames
per scale. The attack includes anticipation, a lifted front
foot, wind-up, strike and recovery to holding. The rear foot stays planted.
Weapon orientations interpolate between key quaternions to avoid a hand-basis
flip as the forearm passes the blade direction. Start/end movement clips relocate
one foot at a time. Their endpoints join the authored phase-zero walk; arbitrary
interrupted movement still needs in-game review.

The walking carriage was revised after visual feedback: the blade now remains
57–73 degrees above horizontal throughout the cycle, replacing the previous
-4–32 degree forward-pointing range. The weapon wrist is higher, the free hand
is lowered away from the face, and torso lean is reduced from 42–46 to 34–38
degrees. These angles describe the new design, not a measured fit to all original
frames. Movement start/end share the revised walk endpoint.

The weapon arm now swings with the walk cycle. The profile controls wrist
forward travel/lift and elbow-pole travel together, so the upper arm rotates at
the shoulder while the forearm follows. The wrist moves forward on the first
contact, back halfway through the cycle, then returns. Start/end clips use the
same revised endpoint. Blade elevation remains 57–73 degrees.

Saved-frame checks measure movement relative to the shoulder, excluding apparent
motion from torso sway. The wrist's forward/back range increases from 0.014908
to 0.360025 model units; elbow range is 0.339639. The previous clip fails the new
arm-swing check despite passing IK and blade-elevation checks. These are motion
checks, not a claim of matching the original frame for frame.

## Full clip set

| Groups | Frames per group | Behavior |
|---|---:|---|
| HOLDING, MOVING | 8 | Idle and raised-sword walk loops |
| MOVE_START, MOVE_END | 2 | Enter and leave the phase-zero walk |
| MOUSEON | 11 | Raise sword and free hand, then return |
| HITTED | 6 | Recoil, settle forward, return |
| DEFENCE | 11 | Raise guard, absorb impact, recover |
| DEATH | 6 | Recoil, kneel, fold and settle prone |
| TURN_L, TURN_R | 2 | Whole-body half-turn clips around a facing flip |
| ATTACK_UP, ATTACK_FRONT, ATTACK_DOWN | 8 | Separate high, frontal and low strikes |

`MotionRoot` parents the rig, controls and geometry. Its native keyed rotation
turns the whole character; it does not substitute a spine twist. VCMI plays
TURN_L, flips the rendered facing, then plays TURN_R. The shared frontal pose
bridges the two clips. The preview includes their native frame order with that
flip. Original DEF groups 9/10 are unused duplicate turns and are not exported.

Death keeps the weapon attached and finishes prone, with a held final pose.
During the collapse, a vertical root correction prevents the evaluated geometry
from penetrating the ground. This is authored motion, not a rigid-body simulation
or the original disintegrating bone pile. Other transient actions return to
holding. Directional strikes have independently authored wrist and torso targets.

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
the counts above, at 450x400 and 900x800. Actual game speed still depends on its
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
  --out "$HOME/vcmi-art/skeleton-motion/full-review-02"

blender -b --python-exit-code 1 --python tools/creature-art/test_skeleton_motion.py -- \
  "$HOME/vcmi-art/skeleton-motion/full-review-02"

tools/creature-art/.venv/bin/python tools/creature-art/motion_preview.py \
  "$HOME/vcmi-art/skeleton-motion/full-review-02" \
  --reference tools/creature-art/ref/cskele/body \
  --previous "$HOME/vcmi-art/skeleton-motion/full-review-01"
```

Use a fresh output directory and do not edit sources during a render. `--no-render`
still calibrates the camera, bakes/saves all clips and records measurements, but
skips review and sprite frames. Each `.blend` contains ordinary editable native
Actions, IK controls, packed textures and a closure frame. The manifest retains
the source hash, both profiles, code hashes/snapshots, camera and measurements.

`test_skeleton_motion.py` reopens all thirteen clips and checks 577 frame/subframe
samples for IK reach, saved-versus-authored positions, ground penetration,
weapon rigidity, straight-line stance drift, loop and transition endpoints,
rest-position attributes and embedded textures. Ground tolerance is 0.0002 model
units (about 0.011 base pixels), allowing numerical IK error. Death additionally
checks every mesh at subframes against a 0.002-unit floor tolerance and requires
a low final pose. Tests compare world transforms across the turn bridge and
verify distinct sword-tip heights at directional strikes. A downward-strike
interpolation initially exceeded reach by 0.002186 units; moving the free wrist
closer reduced the full-set maximum IK error to 0.00009017.

`motion_preview.py` checks counts against the extracted original layout, canvas
dimensions and unclipped alpha bounds. It creates GIFs, scrub-able MP4s and
`preview/index.html`, plus an original/new contact sheet at actual 1x scale.
`--previous` additionally creates an original/previous/revised eight-frame walk
comparison at a shared review rate. The contact sheet compares phases; it does not synchronize original game timing.

## Remaining skeleton work

Review all thirteen clips artistically, including silhouette at native size,
the fixed free-hand pose and the mirrored turn bridge. Render shadow/overlay
layers, assemble and validate the full mod, and inspect actual battles.
These exports currently contain the body pass and are not installed as a mod.

The next creature is the zombie (`CZOMBI`). Reuse the inspection, explicit
handedness, controls, motion checks and render pipeline; zombie proportions and
gait need their own authored profile. A second character will inform whether the
Blender tooling warrants a separate repository. No new Meshy call was needed for
this skeleton stage.
