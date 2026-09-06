#!/usr/bin/env python3
"""Generate creature concept art with the Black Forest Labs FLUX API.

The concept step feeds the mesh step, so what matters is not a pretty picture but
a clean, evenly lit character on a plain background that image-to-3D can read.
Baked shadows, rim light and motion blur all fight the render stage later.

    export BFL_API_KEY=...
    gen_concept.py --prompt-file docs/prompt-cskele.txt --out concept/cskele

Writes <out>-front.png and <out>-side.png plus a .json recording the exact prompt,
seed and cost of each, so a result can be reproduced or bisected later.

Cost is reported per call; flux-2-pro is 3 credits (~$0.03) at 1MP.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

API = "https://api.bfl.ai/v1"
DEFAULT_MODEL = "flux-2-pro"

# Appended to every view so the output stays usable by image-to-3D.
# The backdrop matters as much as the character. Image models default to a subtle
# gradient or an implied floor, and a gradient cannot be keyed out cleanly -- it
# leaves a haze across the whole frame that swallows the silhouette. Demand a single
# flat colour, and one that the subject cannot contain.
MESH_SAFE = (
    "Isolated on a solid uniform chroma green background, one single flat colour "
    "filling the entire frame, absolutely no gradient, no vignette, no floor, "
    "no horizon, no cast shadow, no contact shadow. "
    "Flat even studio lighting, no rim light, no motion blur, no depth of field. "
    "Full body in frame, no cropping, single character, no text."
)

VIEWS = {
    "front": "three-quarter front view",
    "side": "side view, same pose and proportions",
}


def post(path, payload, key):
    request = urllib.request.Request(
        "%s/%s" % (API, path),
        data=json.dumps(payload).encode(),
        headers={"x-key": key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def poll(url, key, timeout=300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        request = urllib.request.Request(url, headers={"x-key": key})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
        status = body.get("status")
        if status == "Ready":
            return body["result"]["sample"]
        if status in ("Error", "Failed", "Content Moderated", "Request Moderated"):
            raise SystemExit("generation failed: %s" % json.dumps(body)[:400])
        time.sleep(2)
    raise SystemExit("timed out waiting for the image")


def generate(prompt, out_path, key, model, width, height, seed):
    payload = {"prompt": prompt, "width": width, "height": height}
    if seed is not None:
        payload["seed"] = seed

    submitted = post(model, payload, key)
    cost = submitted.get("cost")
    url = poll(submitted["polling_url"], key)

    with urllib.request.urlopen(url, timeout=120) as response:
        out_path.write_bytes(response.read())

    return {
        "file": out_path.name,
        "prompt": prompt,
        "model": model,
        "width": width,
        "height": height,
        "seed": seed,
        "cost_credits": cost,
        "request_id": submitted.get("id"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="the character description, without view or lighting")
    source.add_argument("--prompt-file", type=Path, help="read the description from a file")
    parser.add_argument("--out", type=Path, required=True, help="output prefix, e.g. concept/cskele")
    parser.add_argument("--views", default="front,side",
                        help="comma-separated subset of: %s" % ", ".join(VIEWS))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1440)
    parser.add_argument("--seed", type=int, help="fixed seed, so the two views match better")
    parser.add_argument("--dry-run", action="store_true", help="print the prompts, call nothing")
    args = parser.parse_args(argv)

    key = os.environ.get("BFL_API_KEY")
    if not key and not args.dry_run:
        parser.error("BFL_API_KEY is not set")

    base = (args.prompt_file.read_text().strip() if args.prompt_file else args.prompt)
    views = [v.strip() for v in args.views.split(",") if v.strip()]
    for view in views:
        if view not in VIEWS:
            parser.error("unknown view %r; known: %s" % (view, ", ".join(VIEWS)))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    records, total = [], 0.0

    for view in views:
        prompt = "%s %s. %s" % (base, VIEWS[view], MESH_SAFE)
        target = args.out.with_name("%s-%s.png" % (args.out.name, view))
        if args.dry_run:
            print("[%s] -> %s\n  %s\n" % (view, target, prompt))
            continue
        print("generating %s ..." % view, flush=True)
        record = generate(prompt, target, key, args.model, args.width, args.height, args.seed)
        records.append(record)
        total += record["cost_credits"] or 0
        print("  %s  (%s credits)" % (target, record["cost_credits"]))

    if args.dry_run:
        return 0

    meta = args.out.with_name("%s.json" % args.out.name)
    meta.write_text(json.dumps({"base_prompt": base, "images": records}, indent=2) + "\n")
    print("\n%d image(s), %.0f credits (~$%.2f)" % (len(records), total, total * 0.01))
    print("prompts and seeds recorded in %s" % meta)
    print("\nnext: check it reads at in-game size")
    print("  preview.py readability %s-front.png --height 79 \\" % args.out)
    print('      --lod "$LOD" --against CSKELE.DEF --out check.png')
    return 0


if __name__ == "__main__":
    sys.exit(main())
