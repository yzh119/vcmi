"""Reopen baked clips and check actual evaluated motion, including subframes.

blender -b --python-exit-code 1 --python test_skeleton_motion.py -- OUTPUT
"""

import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skeleton_study as study
from test_skeleton_study import controls_for


def main():
    directory = Path(sys.argv[sys.argv.index('--')+1])
    manifest = json.loads((directory/'manifest.json').read_text())
    errors, lengths, bottoms, drifts, replay = [], [], [], [], []
    endpoints = {}
    checked = 0
    for group, clip in manifest['clips'].items():
        bpy.ops.wm.open_mainfile(filepath=str(directory/(group.lower()+'.blend')))
        scene = bpy.context.scene
        arm = bpy.data.objects['SkeletonStudy']
        controls = controls_for(arm)
        socket = bpy.data.objects['WeaponGrip']
        weapons = [bpy.data.objects[n] for n in ['SwordGrip', 'SwordGuard', 'SwordBlade']]
        planted = {}
        states = []
        for half_frame in range(2*(clip['closure_frame']-1)+1):
            frame = 1+half_frame/2
            scene.frame_set(math.floor(frame), subframe=frame % 1)
            row = study.measurements(arm, controls, socket, weapons)
            checked += 1
            lengths.append(row['blade_length'])
            assert row['socket_error'] < 1e-6
            errors.extend(row[c]['target_error'] for c in controls)
            bottoms.extend(row[s+'FootBottom'] for s in ['Left', 'Right'])
            states.append({n: b.matrix.copy() for n, b in arm.pose.bones.items()})
            if half_frame % 2 == 0:
                original = clip['frames'][half_frame//2]
                replay.extend((Vector(row[c]['actual'])-Vector(original[c]['actual'])).length for c in controls)
            if group == 'MOVING':
                t = (frame-1)/(clip['closure_frame']-1)
                travel = Vector(manifest['direction'])*manifest['stride']*t
                for side, offset in [('Right', 0), ('Left', .5)]:
                    phase = (t+offset) % 1
                    # Exclude the half-frame which straddles stance/swing: it is
                    # linearly interpolated between baked 30 fps controls.
                    if phase < manifest['profile']['walk']['stance_fraction']-1/24:
                        key = (side, math.floor(t+offset))
                        world = Vector(row[side+'Leg']['actual'])+travel
                        planted.setdefault(key, world)
                        drifts.append((world-planted[key]).length)
        endpoints[group] = (states[0], states[-1])
        if manifest['profile']['clips'][group]['loop']:
            assert matrix_error(*endpoints[group]) < 2e-4, ('loop seam', group)
        for obj in scene.objects:
            if obj.type == 'MESH' and obj.vertex_groups and obj.name != 'Body':
                assert 'rest_position' in obj.data.attributes, obj.name
        for image in bpy.data.images:
            if image.type == 'IMAGE' and image.source == 'FILE' and image.users:
                assert image.packed_file
    for a, ai, b, bi in [('ATTACK_FRONT', 0, 'HOLDING', 0),
                          ('ATTACK_FRONT', 1, 'HOLDING', 0),
                          ('MOVE_START', 0, 'HOLDING', 0),
                          ('MOVE_START', 1, 'MOVING', 0),
                          ('MOVE_END', 0, 'MOVING', 0),
                          ('MOVE_END', 1, 'HOLDING', 0)]:
        assert matrix_error(endpoints[a][ai], endpoints[b][bi]) < 2e-4, ('transition', a, b)
    assert max(errors) < 2e-4, ('IK', max(errors))
    assert max(replay) < 2e-4, ('saved animation differs from authored motion', max(replay))
    assert min(bottoms) > -2e-4, ('ground penetration', min(bottoms))
    assert max(lengths)-min(lengths) < 1e-5
    assert max(drifts) < 2e-4, ('planted foot drift', max(drifts))
    report = {'evaluated_samples': checked, 'max_ik_error': max(errors),
              'max_replay_error': max(replay), 'min_sole_z': min(bottoms),
              'blade_length_range': max(lengths)-min(lengths), 'max_stance_drift': max(drifts)}
    (directory/'checks.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: saved clips and subframes, loop/transition endpoints, IK, ground, grip, planted feet, textures')
    print(json.dumps(report, indent=2))


def matrix_error(a, b):
    return max(abs(a[n][i][j]-b[n][i][j]) for n in a for i in range(4) for j in range(4))


if __name__ == '__main__':
    main()
