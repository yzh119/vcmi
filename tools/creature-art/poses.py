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
#
# Sign convention trap: leg bones point downward, so local X runs the opposite way
# from the spine's. Positive X on RightLeg/LeftLeg bends the knee correctly (the
# foot travels back and up); negative gives a backward-bending knee. The first
# version had every lower leg negative, and the skeleton read as digitigrade.
BASE = {
    "Hips":          (-8, 0, 0),
    "Spine02":       (10, 0, 0),
    "Spine01":       (8, 0, 0),
    "Spine":         (6, 0, 0),
    "neck":          (-14, 0, 0),
    "Head":          (-10, 0, 0),
    # X is the forward/back swing, Y rolls the arm in toward the chest, Z lowers it
    # from the A-pose. The weapon arm is the Right one by convention; mirror_pose
    # moves it to the other side for a left-handed model.
    #
    # These are measured, not guessed. The blade leaves the wrist along the hand
    # bone's axis, so the stance decides where it points: the values below put the
    # tip 0.58 forward, 0.53 across the midline and 0.37 up from the floor, which
    # is the original's low guard with the sword crossing the shins. The previous
    # stance (-16, 10, -55) left it hanging straight out from the hip, on the far
    # side of the body from the direction the creature faces.
    "RightShoulder": (0, 0, -8),
    "RightArm":      (-10, 25, -40),
    "RightForeArm":  (-20, 0, 0),
    "LeftShoulder":  (0, 0, 8),
    "LeftArm":       (-12, -10, 50),
    "LeftForeArm":   (-26, 0, 0),
    "RightUpLeg":    (16, 0, 0),
    "RightLeg":      (10, 0, 0),
    "RightFoot":     (-6, 0, 0),
    "LeftUpLeg":     (-14, 0, 0),
    "LeftLeg":       (8, 0, 0),
    "LeftFoot":      (4, 0, 0),
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
            (0.0,   {"RightUpLeg": (-28, 0, 0), "RightLeg": (-10, 0, 0), "RightFoot": (8, 0, 0),
                     "LeftUpLeg": (26, 0, 0), "LeftLeg": (34, 0, 0), "LeftFoot": (6, 0, 0),
                     "RightArm": (18, 0, 0), "LeftArm": (-18, 0, 0),
                     "Spine02": (2, 0, 0), "Hips": (0, 0, -5)}),
            (0.25,  {"RightUpLeg": (-6, 0, 0), "RightLeg": (14, 0, 0),
                     "LeftUpLeg": (4, 0, 0), "LeftLeg": (18, 0, 0),
                     "Hips": (-3, 0, 0)}),
            (0.5,   {"RightUpLeg": (26, 0, 0), "RightLeg": (34, 0, 0), "RightFoot": (6, 0, 0),
                     "LeftUpLeg": (-28, 0, 0), "LeftLeg": (-10, 0, 0), "LeftFoot": (8, 0, 0),
                     "RightArm": (-18, 0, 0), "LeftArm": (18, 0, 0),
                     "Spine02": (2, 0, 0), "Hips": (0, 0, 5)}),
            (0.75,  {"RightUpLeg": (4, 0, 0), "RightLeg": (18, 0, 0),
                     "LeftUpLeg": (-6, 0, 0), "LeftLeg": (14, 0, 0),
                     "Hips": (-3, 0, 0)}),
        ),
    },

    # Short lead-in and lead-out the engine plays around MOVING.
    "MOVE_START": {
        "frames": 2, "loop": False,
        "keys": _keys((0.0, {}), (1.0, {"RightUpLeg": (-14, 0, 0), "RightLeg": (-4, 0, 0),
                                        "LeftUpLeg": (12, 0, 0), "LeftLeg": (18, 0, 0),
                                        "Spine02": (4, 0, 0)})),
    },
    "MOVE_END": {
        "frames": 2, "loop": False,
        "keys": _keys((0.0, {"RightUpLeg": (-14, 0, 0), "RightLeg": (-4, 0, 0),
                             "LeftUpLeg": (12, 0, 0), "LeftLeg": (18, 0, 0),
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
    #
    # Second sign trap, after the knees. The blade leaves the wrist along the hand
    # bone's own axis -- it is a continuation of the forearm, not something the
    # wrist aims independently -- and on the upper arm bone negative X carries that
    # line forward and up. The first version struck at +25, which swung the sword
    # behind the creature. Measured tip positions, as (forward, height) from the
    # hips, for the deltas used below: (0.83, 2.42) wound up, (1.19, 1.17) at full
    # extension, (0.66, 0.27) recovered.
    "ATTACK_FRONT": {
        "frames": 8, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.2,  {"RightArm": (-88, 0, 25), "RightForeArm": (-35, 0, 0),
                    "Spine02": (-14, 0, -10), "neck": (4, 0, 0)}),
            (0.45, {"RightArm": (-60, 0, 12), "RightForeArm": (-10, 0, 0),
                    "Spine02": (4, 0, 14), "Hips": (6, 0, 6), "neck": (-6, 0, 0)}),
            (0.7,  {"RightArm": (-34, 0, 14), "RightForeArm": (0, 0, 0),
                    "Spine02": (6, 0, 6), "Hips": (3, 0, 3)}),
            (1.0,  {}),
        ),
    },

    # Upward and downward attacks reuse the swing, aimed by how far the arm is
    # allowed to come down: the strike key leaves the tip at height 1.9, 1.2 and
    # 0.45 for UP, FRONT and DOWN respectively.
    "ATTACK_UP": {
        "frames": 8, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.2,  {"RightArm": (-95, 0, 20), "RightForeArm": (-45, 0, 0), "Spine02": (-16, 0, -8)}),
            (0.45, {"RightArm": (-85, 0, 8), "RightForeArm": (-30, 0, 0),
                    "Spine02": (-4, 0, 12), "Hips": (-4, 0, 5), "neck": (-14, 0, 0)}),
            (0.7,  {"RightArm": (-52, 0, 12), "RightForeArm": (-15, 0, 0), "Spine02": (-2, 0, 5)}),
            (1.0,  {}),
        ),
    },
    "ATTACK_DOWN": {
        "frames": 8, "loop": False,
        "keys": _keys(
            (0.0,  {}),
            (0.2,  {"RightArm": (-84, 0, 30), "RightForeArm": (-40, 0, 0), "Spine02": (-10, 0, -12)}),
            (0.45, {"RightArm": (-60, 0, 16), "RightForeArm": (45, 0, 0),
                    "Spine02": (12, 0, 12), "Hips": (12, 0, 4),
                    "RightUpLeg": (10, 0, 0), "neck": (6, 0, 0)}),
            (0.7,  {"RightArm": (-40, 0, 16), "RightForeArm": (20, 0, 0),
                    "Spine02": (8, 0, 6), "Hips": (6, 0, 2)}),
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
                    "RightLeg": (14, 0, 0), "LeftLeg": (12, 0, 0)}),
            (0.75, {"Spine02": (12, 0, 0), "Spine01": (8, 0, 0), "neck": (10, 0, 0),
                    "RightArm": (-30, 0, 25), "RightForeArm": (-45, 0, 0),
                    "LeftArm": (-25, 0, -25), "LeftForeArm": (-40, 0, 0),
                    "Hips": (10, 0, 0), "RightUpLeg": (12, 0, 0), "LeftUpLeg": (10, 0, 0),
                    "RightLeg": (14, 0, 0), "LeftLeg": (12, 0, 0)}),
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
                    "RightLeg": (70, 0, 0), "LeftLeg": (65, 0, 0),
                    "RightArm": (10, 0, -20), "LeftArm": (10, 0, 20)}),
            (1.0,  {"Spine02": (55, 0, 0), "Spine01": (30, 0, 0), "neck": (-25, 0, 0),
                    "Hips": (78, 0, 0), "RightUpLeg": (60, 0, 0), "LeftUpLeg": (55, 0, 0),
                    "RightLeg": (95, 0, 0), "LeftLeg": (90, 0, 0),
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


# ---------------------------------------------------------------------------
# Per-creature character
# ---------------------------------------------------------------------------
#
# BASE and GROUPS were authored for the skeleton warrior, and sharing them across
# the roster gave the zombie a full running stride where the original shambles.
# The motion is the character: a skeleton strides, a zombie drags its feet, a lich
# barely moves below the waist.
#
# A creature supplies two things, both optional:
#
#   base       overrides merged onto BASE -- its resting stance
#   amplitude  per-group multiplier on the motion, 1.0 being the authored amount
#
# Anything not listed falls back to the shared values, so a new creature costs a
# few lines rather than thirteen groups of keyframes.

CREATURES = {
    "CSKELE": {},          # the groups were authored against it

    "CZOMBI": {
        "base": {
            # Slumped, head lolling, arms hanging heavy and forward rather than
            # carrying anything. No weapon, so the sword stance does not apply.
            "Spine02":       (16, 0, 0),
            "Spine01":       (12, 0, 0),
            "neck":          (-6, 0, 0),
            "Head":          (8, 0, -10),
            "RightShoulder": (0, 0, -4),
            "RightArm":      (-34, 8, -28),
            "RightForeArm":  (-40, 0, 0),
            "LeftShoulder":  (0, 0, 4),
            "LeftArm":       (-30, -8, 26),
            "LeftForeArm":   (-44, 0, 0),
            "RightUpLeg":    (10, 0, 0),
            "RightLeg":      (14, 0, 0),
            "LeftUpLeg":     (-8, 0, 0),
            "LeftLeg":       (10, 0, 0),
        },
        "amplitude": {
            "MOVING": 0.35,        # shamble, not a stride
            "MOVE_START": 0.35,
            "MOVE_END": 0.35,
            "ATTACK_FRONT": 0.65,  # a swipe, not a sword swing
            "ATTACK_UP": 0.65,
            "ATTACK_DOWN": 0.65,
            "MOUSEON": 0.5,
            "HOLDING": 1.3,        # heavier sway while idle
        },
    },
}


def creature_profile(name):
    if not name:
        return {}
    key = name.upper()
    if key.endswith(".DEF"):
        key = key[:-4]
    return CREATURES.get(key, {})


def mirror_pose(pose):
    """Swap the left and right halves of a pose.

    Meshy puts the prop in whichever hand the concept art shows, and the concept
    is not consistent about it -- the skeleton ended up left-handed. Rather than
    author every attack twice, the group deltas are written for a right-handed
    creature and mirrored when the rebind reports a left hand.

    A mirrored rotation flips its name and negates the Y and Z components. That is
    the relationship BASE already encodes between RightArm (-16, 10, -55) and
    LeftArm (-12, -10, 50).
    """
    flipped = {}
    for bone, value in pose.items():
        if bone.startswith("Left"):
            name = "Right" + bone[len("Left"):]
        elif bone.startswith("Right"):
            name = "Left" + bone[len("Right"):]
        else:
            name = bone
        flipped[name] = (value[0], -value[1], -value[2])
    return flipped


def pose_at(group, t, creature=None, mirror=False):
    """The creature's stance plus the group's interpolated delta at time t."""
    profile = creature_profile(creature)
    base_pose = dict(BASE)
    base_pose.update(profile.get("base", {}))
    if mirror:
        base_pose = mirror_pose(base_pose)
    gain = profile.get("amplitude", {}).get(group, 1.0)

    spec = GROUPS[group]
    keys = spec["keys"]
    if spec.get("loop"):
        keys = keys + [(1.0, keys[0][1])]

    if mirror:
        keys = [(time, mirror_pose(delta)) for time, delta in keys]

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
    for bone in set(base_pose) | set(before[1]) | set(after[1]):
        base = base_pose.get(bone, (0.0, 0.0, 0.0))
        start = before[1].get(bone, (0.0, 0.0, 0.0))
        end = after[1].get(bone, (0.0, 0.0, 0.0))
        pose[bone] = tuple(
            base[axis] + gain * (start[axis] + (end[axis] - start[axis]) * blend)
            for axis in range(3)
        )
    return pose
