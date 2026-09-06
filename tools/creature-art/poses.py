"""Heroes III animation groups, written as keyframed bone rotations.

Meshy's rigging returns a walk and a run. Heroes III wants thirteen groups, so the
rest are authored here rather than retargeted: the original animations are short,
stylised and specific, and a motion library matches none of them.

Everything is expressed against the rig's rest pose, in degrees, per bone, in the
bone's local space. `BASE` is the combat stance every group starts from — the
original skeleton is hunched forward with its sword low, and building that once
keeps each group to the motion that distinguishes it.

Bone names are the ones Meshy's rig uses (Mixamo lineage):

    Hips  Spine02 Spine01 Spine  neck Head
    LeftShoulder LeftArm LeftForeArm LeftHand   (and Right)
    LeftUpLeg LeftLeg LeftFoot LeftToeBase      (and Right)
"""

# The stance shared by every group: weight forward, head ahead of the shoulders,
# sword arm low and across the body, knees bent.
BASE = {
    "Hips":          (-8, 0, 0),
    "Spine02":       (10, 0, 0),
    "Spine01":       (8, 0, 0),
    "Spine":         (6, 0, 0),
    "neck":          (-14, 0, 0),
    "Head":          (-10, 0, 0),
    "RightShoulder": (0, 0, -8),
    "RightArm":      (-20, 10, -55),
    "RightForeArm":  (-35, 0, 0),
    "LeftShoulder":  (0, 0, 8),
    "LeftArm":       (-14, -10, 50),
    "LeftForeArm":   (-30, 0, 0),
    "RightUpLeg":    (14, 0, 0),
    "RightLeg":      (-26, 0, 0),
    "RightFoot":     (12, 0, 0),
    "LeftUpLeg":     (-16, 0, 0),
    "LeftLeg":       (-18, 0, 0),
    "LeftFoot":      (10, 0, 0),
}


def _keys(*pairs):
    """(t, delta) pairs, t normalised 0..1 across the group."""
    return list(pairs)


# Each group: how many frames the original uses, whether it loops, and the
# deltas added to BASE at each normalised time.
GROUPS = {
    # Walk cycle. The original's ground line moves about 5 px across this group,
    # so the feet are allowed to leave it -- unlike the idle, which the validator
    # holds to two.
    "MOVING": {
        "frames": 8, "loop": True,
        "keys": _keys(
            (0.0,   {"RightUpLeg": (-28, 0, 0), "RightLeg": (10, 0, 0), "RightFoot": (8, 0, 0),
                     "LeftUpLeg": (26, 0, 0), "LeftLeg": (-34, 0, 0), "LeftFoot": (6, 0, 0),
                     "RightArm": (18, 0, 0), "LeftArm": (-18, 0, 0),
                     "Spine02": (2, 0, 0), "Hips": (0, 0, -5)}),
            (0.25,  {"RightUpLeg": (-6, 0, 0), "RightLeg": (-14, 0, 0),
                     "LeftUpLeg": (4, 0, 0), "LeftLeg": (-18, 0, 0),
                     "Hips": (-3, 0, 0)}),
            (0.5,   {"RightUpLeg": (26, 0, 0), "RightLeg": (-34, 0, 0), "RightFoot": (6, 0, 0),
                     "LeftUpLeg": (-28, 0, 0), "LeftLeg": (10, 0, 0), "LeftFoot": (8, 0, 0),
                     "RightArm": (-18, 0, 0), "LeftArm": (18, 0, 0),
                     "Spine02": (2, 0, 0), "Hips": (0, 0, 5)}),
            (0.75,  {"RightUpLeg": (4, 0, 0), "RightLeg": (-18, 0, 0),
                     "LeftUpLeg": (-6, 0, 0), "LeftLeg": (-14, 0, 0),
                     "Hips": (-3, 0, 0)}),
        ),
    },

    # Short lead-in and lead-out the engine plays around MOVING.
    "MOVE_START": {
        "frames": 2, "loop": False,
        "keys": _keys((0.0, {}), (1.0, {"RightUpLeg": (-14, 0, 0), "RightLeg": (4, 0, 0),
                                        "LeftUpLeg": (12, 0, 0), "LeftLeg": (-18, 0, 0),
                                        "Spine02": (4, 0, 0)})),
    },
    "MOVE_END": {
        "frames": 2, "loop": False,
        "keys": _keys((0.0, {"RightUpLeg": (-14, 0, 0), "RightLeg": (4, 0, 0),
                             "LeftUpLeg": (12, 0, 0), "LeftLeg": (-18, 0, 0),
                             "Spine02": (4, 0, 0)}), (1.0, {})),
    },

    # Idle. The feet must not move: the original holds its ground line to the
    # pixel across all eight frames, and the validator checks exactly that.
    "HOLDING": {
        "frames": 8, "loop": True,
        "keys": _keys(
            (0.0,  {}),
            (0.25, {"Spine01": (-2, 0, 0), "neck": (2, 0, 0), "RightArm": (2, 0, 0)}),
            (0.5,  {"Spine01": (-3, 0, 0), "neck": (3, 0, 0), "RightArm": (3, 0, 1)}),
            (0.75, {"Spine01": (-2, 0, 0), "neck": (2, 0, 0), "RightArm": (2, 0, 0)}),
        ),
    },

    # Hover highlight. Raises the sword, which is what the original does; the feet
    # stay planted, so only the upper body moves.
    "MOUSEON": {
        "frames": 11, "loop": True,
        "keys": _keys(
            (0.0,  {}),
            (0.35, {"RightArm": (-25, 0, 20), "RightForeArm": (-20, 0, 0), "Spine01": (-4, 0, 0)}),
            (0.6,  {"RightArm": (-40, 0, 35), "RightForeArm": (-30, 0, 0), "Spine01": (-6, 0, 0)}),
            (0.85, {"RightArm": (-25, 0, 20), "RightForeArm": (-20, 0, 0), "Spine01": (-4, 0, 0)}),
        ),
    },

    # Forward attack: wind up, strike through, recover.
    "ATTACK_FRONT": {
        "frames": 8, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.2,  {"RightArm": (-55, 0, 30), "RightForeArm": (-45, 0, 0),
                    "Spine02": (-8, 0, -10), "neck": (4, 0, 0)}),
            (0.45, {"RightArm": (25, 0, -20), "RightForeArm": (10, 0, 0),
                    "Spine02": (12, 0, 14), "Hips": (6, 0, 6), "neck": (-6, 0, 0)}),
            (0.7,  {"RightArm": (10, 0, -8), "RightForeArm": (-5, 0, 0),
                    "Spine02": (6, 0, 6), "Hips": (3, 0, 3)}),
            (1.0,  {}),
        ),
    },

    # Upward and downward attacks reuse the swing, tilted at the shoulder and spine.
    "ATTACK_UP": {
        "frames": 8, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.2,  {"RightArm": (-70, 0, 25), "RightForeArm": (-50, 0, 0), "Spine02": (-12, 0, -8)}),
            (0.45, {"RightArm": (-15, 0, -15), "RightForeArm": (-5, 0, 0),
                    "Spine02": (-4, 0, 12), "Hips": (-4, 0, 5), "neck": (-14, 0, 0)}),
            (0.7,  {"RightArm": (-8, 0, -6), "Spine02": (-2, 0, 5)}),
            (1.0,  {}),
        ),
    },
    "ATTACK_DOWN": {
        "frames": 8, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.2,  {"RightArm": (-45, 0, 35), "RightForeArm": (-40, 0, 0), "Spine02": (-6, 0, -12)}),
            (0.45, {"RightArm": (45, 0, -25), "RightForeArm": (18, 0, 0),
                    "Spine02": (22, 0, 12), "Hips": (12, 0, 4),
                    "RightUpLeg": (10, 0, 0), "neck": (6, 0, 0)}),
            (0.7,  {"RightArm": (20, 0, -10), "Spine02": (12, 0, 6), "Hips": (6, 0, 2)}),
            (1.0,  {}),
        ),
    },

    # Taking a hit: knocked back, then recovering.
    "HITTED": {
        "frames": 6, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.3,  {"Spine02": (-22, 0, 0), "Spine01": (-12, 0, 0), "neck": (18, 0, 0),
                    "Head": (12, 0, 0), "RightArm": (-15, 0, 10), "LeftArm": (-15, 0, -10),
                    "Hips": (-8, 0, 0)}),
            (0.6,  {"Spine02": (-10, 0, 0), "neck": (8, 0, 0), "Hips": (-4, 0, 0)}),
            (1.0,  {}),
        ),
    },

    # Defending: crouched behind the guard.
    "DEFENCE": {
        "frames": 11, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.25, {"Spine02": (12, 0, 0), "Spine01": (8, 0, 0), "neck": (10, 0, 0),
                    "RightArm": (-30, 0, 25), "RightForeArm": (-45, 0, 0),
                    "LeftArm": (-25, 0, -25), "LeftForeArm": (-40, 0, 0),
                    "Hips": (10, 0, 0), "RightUpLeg": (12, 0, 0), "LeftUpLeg": (10, 0, 0),
                    "RightLeg": (-14, 0, 0), "LeftLeg": (-12, 0, 0)}),
            (0.75, {"Spine02": (12, 0, 0), "Spine01": (8, 0, 0), "neck": (10, 0, 0),
                    "RightArm": (-30, 0, 25), "RightForeArm": (-45, 0, 0),
                    "LeftArm": (-25, 0, -25), "LeftForeArm": (-40, 0, 0),
                    "Hips": (10, 0, 0), "RightUpLeg": (12, 0, 0), "LeftUpLeg": (10, 0, 0),
                    "RightLeg": (-14, 0, 0), "LeftLeg": (-12, 0, 0)}),
            (1.0,  {}),
        ),
    },

    # Collapsing. The one group where the ground line is meant to move.
    "DEATH": {
        "frames": 6, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.25, {"Spine02": (-18, 0, 0), "neck": (16, 0, 0), "Hips": (-10, 0, 0),
                    "RightArm": (-20, 0, 15), "LeftArm": (-20, 0, -15)}),
            (0.6,  {"Spine02": (25, 0, 0), "Spine01": (18, 0, 0), "neck": (-10, 0, 0),
                    "Hips": (35, 0, 0), "RightUpLeg": (40, 0, 0), "LeftUpLeg": (35, 0, 0),
                    "RightLeg": (-70, 0, 0), "LeftLeg": (-65, 0, 0),
                    "RightArm": (10, 0, -20), "LeftArm": (10, 0, 20)}),
            (1.0,  {"Spine02": (55, 0, 0), "Spine01": (30, 0, 0), "neck": (-25, 0, 0),
                    "Hips": (78, 0, 0), "RightUpLeg": (60, 0, 0), "LeftUpLeg": (55, 0, 0),
                    "RightLeg": (-95, 0, 0), "LeftLeg": (-90, 0, 0),
                    "RightArm": (25, 0, -35), "LeftArm": (25, 0, 35)}),
        ),
    },

    # Turning. Two frames in the original; a half-turn of the hips reads enough at
    # this size, and the engine mirrors for the other facing anyway.
    "TURN_L": {
        "frames": 2, "loop": False,
        "keys": _keys((0.0, {}), (1.0, {"Hips": (0, 0, 40), "Spine02": (0, 0, 15), "neck": (0, 0, -20)})),
    },
    "TURN_R": {
        "frames": 2, "loop": False,
        "keys": _keys((0.0, {"Hips": (0, 0, 40), "Spine02": (0, 0, 15), "neck": (0, 0, -20)}), (1.0, {})),
    },
}


def pose_at(group, t):
    """BASE plus the group's interpolated delta at normalised time t."""
    spec = GROUPS[group]
    keys = spec["keys"]
    if spec.get("loop"):
        keys = keys + [(1.0, keys[0][1])]

    before, after = keys[0], keys[-1]
    for index in range(len(keys) - 1):
        if keys[index][0] <= t <= keys[index + 1][0]:
            before, after = keys[index], keys[index + 1]
            break

    span = after[0] - before[0]
    blend = 0.0 if span <= 0 else (t - before[0]) / span
    # Smoothstep: the original animations ease rather than move linearly.
    blend = blend * blend * (3.0 - 2.0 * blend)

    pose = {}
    for bone in set(BASE) | set(before[1]) | set(after[1]):
        base = BASE.get(bone, (0.0, 0.0, 0.0))
        start = before[1].get(bone, (0.0, 0.0, 0.0))
        end = after[1].get(bone, (0.0, 0.0, 0.0))
        pose[bone] = tuple(
            base[axis] + start[axis] + (end[axis] - start[axis]) * blend
            for axis in range(3)
        )
    return pose
