"""Serialize the existing sprite pipeline without changing pixels or timings."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import sys
from pathlib import Path
import json
import hashlib
ROOT = Path(os.environ["FDM_WEB_WORKSPACE"]).resolve()
sys.path.insert(0, str(ROOT / 'src'))
import pygame
from svz.production_animations import build_production_clips

def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    output = ROOT / 'assets' / 'web_clips'
    output.mkdir(exist_ok=True)
    clips = build_production_clips()
    pages, rects, fingerprints = [], [], {}
    page = pygame.Surface((2048, 2048), pygame.SRCALPHA)
    page.fill((0, 0, 0, 0))
    x = y = row_height = 0
    def save_page():
        name = f'atlas_{len(pages):03d}.png'
        pygame.image.save(page, output / name)
        pages.append(name)
    from svz.actor_animation import ActorClip
    from svz.animation import AnimationClip
    for states in clips.values():
        for state, clip in list(states.items()):
            if state in {"move", "idle"} and isinstance(clip, ActorClip):
                states["between:"+state] = AnimationClip(tuple(clip.intermediate(i) for i in range(len(clip.frames))), clip.frame_durations, clip.loop, clip.name)
    actors = {}
    for actor, states in clips.items():
        actors[actor] = {}
        for state, clip in states.items():
            indexes = []
            for frame in clip.frames:
                w, h = frame.get_size()
                raw = pygame.image.tobytes(frame, 'RGBA')
                digest = (w, h, hashlib.sha256(raw).hexdigest())
                if digest not in fingerprints:
                    if w > 2048 or h > 2048:
                        raise ValueError(f'Frame too large: {actor}/{state}')
                    if x + w > 2048:
                        x, y, row_height = 0, y + row_height + 2, 0
                    if y + h > 2048:
                        save_page()
                        page.fill((0, 0, 0, 0))
                        x = y = row_height = 0
                    # Copy RGBA directly: normal alpha blending would change pixels.
                    page.blit(frame, (x, y), special_flags=pygame.BLEND_RGBA_ADD)
                    fingerprints[digest] = len(rects)
                    rects.append([len(pages), x, y, w, h, digest[2]])
                    x += w + 2
                    row_height = max(row_height, h)
                indexes.append(fingerprints[digest])
            actors[actor][state] = dict(frames=indexes, durations=clip.frame_durations,
                                         loop=clip.loop, name=clip.name)
    save_page()
    metadata = dict(pages=pages, rects=rects, actors=actors)
    (output / 'clips.json').write_text(json.dumps(metadata, ensure_ascii=False), encoding='utf-8')
    print(f'{len(actors)} actors, {len(rects)} unique frames, {len(pages)} lossless atlases')
    pygame.quit()

if __name__ == '__main__':
    main()
