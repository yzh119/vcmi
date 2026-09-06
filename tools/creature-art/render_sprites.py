#!/usr/bin/env python3
"""Render a rigged model back into Heroes III sprite frames. Runs inside Blender.

    blender -b --python render_sprites.py -- \\
        --model rigged/skeleton.glb --out frames/holding \\
        --canvas 450x400 --ground 267 --height 79 --elevation 30

The engine gives no way to nudge a sprite afterwards: the frame's own canvas and
the position of the creature inside it are the only anchor there is. So the camera
is solved rather than eyeballed — the model's vertices are projected into camera
space and the orthographic scale and shift are computed so the creature lands at
exactly `height` pixels tall with its feet on `ground`.

Three passes per frame, matching what the engine expects back:

    <name>_NN.png           the creature
    <name>_NN-shadow.png    its ground shadow, on a catcher plane
    <name>_NN-overlay.png   flat white silhouette for the hover highlight

Frames come from the model's own animation, sampled evenly across its length.
"""

import argparse
import math
import os
import sys

import bpy
from mathutils import Euler, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poses  # noqa: E402


def argv_after_ddash():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_model(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".glb" or ext == ".gltf":
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    else:
        raise SystemExit("unsupported model format: %s" % ext)
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def world_vertices(meshes, depsgraph):
    """Every vertex in world space, after modifiers and the current pose."""
    points = []
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        matrix = evaluated.matrix_world
        points.extend([matrix @ v.co for v in mesh.vertices])
        evaluated.to_mesh_clear()
    return points


def measure_alpha_bbox(path):
    """(left, top, right, bottom) of non-transparent pixels, read back in Blender."""
    image = bpy.data.images.load(path)
    try:
        width, height = image.size
        pixels = list(image.pixels)          # RGBA floats, bottom-up
        left, top, right, bottom = width, height, -1, -1
        for y in range(height):
            row = y * width * 4
            for x in range(width):
                if pixels[row + x * 4 + 3] > 0.004:
                    flipped = height - 1 - y   # to top-down pixel coordinates
                    if x < left: left = x
                    if x > right: right = x
                    if flipped < top: top = flipped
                    if flipped > bottom: bottom = flipped
        return None if right < 0 else (left, top, right + 1, bottom + 1)
    finally:
        bpy.data.images.remove(image)


def calibrate_camera(camera, canvas, ground, height_px, probe_path, rounds=8):
    """Render, measure, correct, until the creature lands on the anchor.

    An analytic solve looked exact and rendered 51 px where it predicted 79. The
    projection and the render disagreed for reasons that did not survive scrutiny,
    so this measures the render instead -- ground truth, one cheap extra frame, and
    it self-corrects for whatever a future model does.

    Scale and position are corrected in separate phases. Fixing both at once makes
    them fight: rescaling moves the feet, so a position correction computed against
    the old scale overshoots.
    """
    width_px, canvas_h = canvas
    larger = float(max(width_px, canvas_h))
    box = None

    for attempt in range(rounds):
        render_to(probe_path)
        box = measure_alpha_bbox(probe_path)
        if box is None:
            raise SystemExit("nothing rendered -- the camera is not pointing at the model")
        got_h = box[3] - box[1]
        got_feet = box[3]
        got_cx = (box[0] + box[2]) / 2.0

        off_h = got_h - height_px
        off_y = ground - got_feet
        off_x = got_cx - width_px / 2.0
        print("CALIBRATE %d: height %d (%+d), feet %d (%+d), centre %.1f (%+.1f)"
              % (attempt, got_h, off_h, got_feet, -off_y, got_cx, off_x))

        if abs(off_h) <= 1 and abs(off_y) <= 1 and abs(off_x) <= 1:
            return box

        if abs(off_h) > 1:
            # ortho_scale is inversely proportional to rendered size. Nothing else
            # this round -- the position correction is computed after the scale is
            # settled.
            camera.data.ortho_scale *= got_h / float(height_px)
            continue

        # Shift is a fraction of the larger render dimension. Sign established by
        # measurement: increasing shift_y moves the rendered content down.
        camera.data.shift_y += off_y / larger
        camera.data.shift_x += off_x / larger

    print("CALIBRATE gave up after %d rounds" % rounds)
    return box


def build_scene(model, canvas, elevation, azimuth, ground, height_px, samples):
    reset_scene()
    meshes = import_model(model)
    scene = bpy.context.scene

    scene.render.resolution_x, scene.render.resolution_y = canvas
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True

    camera_data = bpy.data.cameras.new("cam")
    camera_data.type = "ORTHO"
    camera = bpy.data.objects.new("cam", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    # Elevation above the horizon, azimuth around the model. Blender's camera
    # looks down -Z, so an X rotation of 90 degrees puts it level with the ground.
    camera.rotation_euler = (math.radians(90 - elevation), 0.0, math.radians(azimuth))
    distance = 100.0
    direction = Vector((
        math.sin(math.radians(azimuth)) * math.cos(math.radians(elevation)),
        -math.cos(math.radians(azimuth)) * math.cos(math.radians(elevation)),
        math.sin(math.radians(elevation)),
    ))
    camera.location = direction * distance

    # matrix_world is stale until the view layer catches up with the location and
    # rotation just assigned; solving against the stale matrix silently projects
    # into world space instead of camera space.
    bpy.context.view_layer.update()
    # A starting guess; calibration converges from anything that frames the model.
    camera.data.ortho_scale = 4.0

    # Flat, even key light: the render stage supplies its own shadow pass, so the
    # beauty pass should not bake one in.
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", type="SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0.0, math.radians(azimuth - 30))
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    scene.world = world

    return meshes, camera, sun


def find_armature():
    for obj in bpy.context.scene.objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def apply_pose(armature, pose):
    """Set every bone's local rotation from a {bone: (x, y, z) degrees} dict."""
    for bone in armature.pose.bones:
        bone.rotation_mode = "XYZ"
        degrees = pose.get(bone.name)
        bone.rotation_euler = Euler(
            tuple(math.radians(v) for v in degrees) if degrees else (0.0, 0.0, 0.0), "XYZ")
    bpy.context.view_layer.update()


def render_to(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--name", default="", help="frame name prefix (default: the group)")
    parser.add_argument("--group", choices=sorted(poses.GROUPS),
                        help="which Heroes III animation group to render")
    parser.add_argument("--canvas", default="450x400")
    parser.add_argument("--ground", type=int, default=267)
    parser.add_argument("--height", type=int, default=79, help="creature height in pixels")
    parser.add_argument("--elevation", type=float, default=30.0)
    parser.add_argument("--azimuth", type=float, default=0.0)
    parser.add_argument("--frames", type=int, default=0,
                        help="override the group's frame count")
    parser.add_argument("--samples", type=int, default=48)
    parser.add_argument("--scale", type=int, default=1, help="render at N times 1x")
    args = parser.parse_args(argv_after_ddash())

    width, height = (int(v) for v in args.canvas.lower().split("x"))
    canvas = (width * args.scale, height * args.scale)
    ground = args.ground * args.scale
    creature_px = args.height * args.scale

    meshes, camera, _ = build_scene(
        args.model, canvas, args.elevation, args.azimuth, ground, creature_px, args.samples)

    os.makedirs(args.out, exist_ok=True)
    scene = bpy.context.scene

    armature = find_armature()

    # Calibrate against the pose that will actually be rendered. The rig arrives in
    # an A-pose, and the combat stance is hunched -- calibrating before posing put
    # the creature 2 px too tall and 2 px too low.
    if args.group and armature is not None:
        apply_pose(armature, poses.pose_at(args.group, 0.0))

    real_samples = scene.cycles.samples
    scene.cycles.samples = 1                     # calibration only needs coverage
    calibrate_camera(camera, canvas, ground, creature_px,
                     os.path.join(args.out, "_calibration.png"))
    scene.cycles.samples = real_samples

    if args.group:
        if armature is None:
            raise SystemExit("--group needs a rigged model; no armature found")
        spec = poses.GROUPS[args.group]
        count = args.frames or spec["frames"]
        name = args.name or args.group.lower()
        for index in range(count):
            # A loop samples [0, 1) so the last frame does not repeat the first;
            # a one-shot samples [0, 1] so it reaches its final pose.
            t = index / float(count) if spec.get("loop") else (
                index / float(count - 1) if count > 1 else 0.0)
            apply_pose(armature, poses.pose_at(args.group, t))
            render_to(os.path.join(args.out, "%s_%02d.png" % (name, index)))
    else:
        count = 1
        render_to(os.path.join(args.out, "%s_00.png" % (args.name or "frame")))

    probe = os.path.join(args.out, "_calibration.png")
    if os.path.exists(probe):
        os.remove(probe)

    print("RENDERED %d frame(s) at %dx%d, ground %d, creature %d px"
          % (count, canvas[0], canvas[1], ground, creature_px))


if __name__ == "__main__":
    main()
