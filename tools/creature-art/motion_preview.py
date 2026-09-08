#!/usr/bin/env python3
"""Build fixed-scale sheets, playable videos and a local motion review page.

Requires Pillow and ffmpeg. All crops share the holding camera's pixel origin.
"""

import argparse
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw


BACKGROUND = (28, 29, 33)
GROUPS = ['holding', 'moving', 'attack_front', 'move_start', 'move_end']


def tile(path, center, scale=2):
    with Image.open(path) as im:
        raw = im.convert('RGBA').crop((round(center-90*scale), 125*scale,
                                       round(center+90*scale), 278*scale))
    return raw


def center(path):
    with Image.open(path) as im:
        box = im.getbbox()
        return (box[0]+box[2])/2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--reference', type=Path, required=True)
    args = parser.parse_args()
    p = args.directory
    manifest = json.loads((p/'manifest.json').read_text())
    reference = json.loads((args.reference.parent/'layout.json').read_text())
    counts = {g['name']: len(g['frames']) for g in reference['groups']}
    for group in GROUPS:
        expected = counts[group.upper()]
        assert manifest['profile']['clips'][group.upper()]['sprite_frames'] == expected
        for scale in [1, 2]:
            files = sorted((p/('sprites%dx' % scale)).glob(group+'_*.png'))
            assert len(files) == expected, (group, scale, len(files))
            for file in files:
                with Image.open(file) as im:
                    assert im.size == (450*scale, 400*scale), file
                    box = im.getbbox()
                    assert box and box[0] > 0 and box[1] > 0 and box[2] < im.width and box[3] < im.height, file
    output = p/'preview'
    output.mkdir(exist_ok=True)
    new_center = center(p/'sprites2x/holding_00.png')
    ref_center = center(args.reference/'holding_00.png')
    html = ['<!doctype html><html lang="en"><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>Skeleton motion review</title>',
            '<style>body{background:#1c1d21;color:#ddd;font:16px system-ui;max-width:1000px;margin:32px auto;padding:16px}video{width:360px;max-width:100%}img{max-width:100%}section{display:inline-block;vertical-align:top;margin:12px}p{line-height:1.6}</style>',
            '<h1>Skeleton motion review</h1><p>Editable five-clip study. Videos show the 30 fps bake at 2× game scale. '
            'Pause or scrub to inspect. Body pass only; no in-game acceptance yet. '
            'Attack includes recovery to holding. Movement is shown in place.</p>']
    for group in GROUPS:
        frames = []
        for source in sorted((p/'review'/group).glob('*.png')):
            raw = tile(source, new_center)
            image = Image.new('RGB', raw.size, BACKGROUND)
            image.paste(raw, (0, 0), raw)
            frames.append(image)
        fps = manifest['profile']['fps']
        # GIF durations use centiseconds; alternate 30/40 ms to retain 30 fps.
        durations = [10*(round((i+1)*100/fps)-round(i*100/fps)) for i in range(len(frames))]
        frames[0].save(output/(group+'.gif'), save_all=True, append_images=frames[1:],
                       duration=durations, loop=0, disposal=2)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps),
                        '-i', str(p/'review'/group/'%03d.png'), '-filter_complex',
                        ('[0:v]crop=360:306:%d:250[fg];'
                         'color=c=0x1c1d21:s=360x306:r=%d[bg];'
                         '[bg][fg]overlay=shortest=1,format=yuv420p') % (round(new_center-180), fps),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18',
                        '-movflags', '+faststart', str(output/(group+'.mp4'))], check=True)
        html.append('<section><h2>%s</h2><video controls loop muted playsinline preload="metadata" poster="%s.gif" src="%s.mp4"></video></section>' % (group, group, group))
    # Original-count frames, aligned by phase; not a claim of matched engine timing.
    width, height = 180, 175
    sheet = Image.new('RGB', (8*width, 6*height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for group_index, group in enumerate(GROUPS[:3]):
        for version, source, offset in [('Original', args.reference, ref_center),
                                         ('Study', p/'sprites1x', new_center/2)]:
            row = group_index*2+(version == 'Study')
            for i in range(8):
                raw = tile(source/(group+'_%02d.png' % i), offset, 1)
                x, y = i*width, row*height
                sheet.paste(raw, (x, y+22), raw)
                draw.text((x+4, y+4), '%s %s %d' % (version, group, i), fill='white')
    sheet.save(output/'native-frames.png')
    sheet.resize((sheet.width*2, sheet.height*2), Image.Resampling.NEAREST).save(output/'frames-2x.png')
    html.append('<h2>Original-count frames at 1×</h2><p>Shared scale and crop per row; original attack frames are phase references. No individual frame fitting.</p><img src="native-frames.png" alt="Original and new eight-frame sequences"></html>')
    (output/'index.html').write_text('\n'.join(html)+'\n')
    print(output/'index.html')


if __name__ == '__main__':
    main()
