"""Check region streaming, all RGBA pixels, order and durations after packing."""
from pathlib import Path
from PIL import Image
import hashlib
import json
import os
import tarfile

root = Path(os.environ['FDM_WEB_WORKSPACE'])
out = root/'web_game/build/web'
meta = json.loads((root/'web_game/assets/web_clips/clips.json').read_text(encoding='utf-8'))
original = json.loads((root/'assets/web_clips/clips.json').read_text(encoding='utf-8'))
assert meta['actors'] == original['actors'], 'Frame order or timings changed'
checked = 0
for page, name in enumerate(meta['pages']):
    image = Image.open(out/'chunks'/name).convert('RGBA')
    for i, (p, x, y, w, h, digest) in enumerate(meta['rects']):
        if p != page:
            continue
        assert (w, h, digest) == tuple(original['rects'][i][3:])
        assert hashlib.sha256(image.crop((x, y, x+w, y+h)).tobytes()).hexdigest() == digest
        checked += 1
assert checked == len(original['rects'])
groups = {r: {meta['rects'][i][0] for actor, states in meta['actors'].items()
              if actor.startswith(r+'_') for clip in states.values() for i in clip['frames']}
          for r in ('city', 'desert', 'beach')}
assert not (groups['city'] & groups['desert'] or groups['city'] & groups['beach'] or groups['desert'] & groups['beach'])
names = json.loads((out/'site-files.json').read_text(encoding='utf-8'))
boot = next(name for name in names if name.startswith('bootstrap-'))
with tarfile.open(out/boot) as archive:
    assert not any('/web_clips/atlas_' in name for name in archive.getnames())
    assert not any('/test-data/' in name or '.web-preview-data/' in name for name in archive.getnames())
report = {'verified_frames': checked, 'actor_timing_unchanged': True,
          'actors': len(meta['actors']), 'region_pages_disjoint': True}
(root/'reports/verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(report)
