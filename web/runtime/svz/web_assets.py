"""Load lossless, precompiled frames with the original pivots and timing."""
import json
from pathlib import Path
import pygame
import asyncio, hashlib, gc
from .actor_animation import ActorClip
from .paths import ASSET_ROOT

class WebClips(dict):
    def __init__(self):
        super().__init__()
        self.root = ASSET_ROOT / 'web_clips'
        self.meta = json.loads((self.root / 'clips.json').read_text(encoding='utf-8'))
        self.frames = {}
        self.page_number = None
        self.page = None

    def __bool__(self):
        return bool(self.meta['actors'])

    def __contains__(self, actor):
        return actor in self.meta['actors']

    def get(self, actor, default=None):
        return self[actor] if actor in self else default

    def frame(self, index):
        if index not in self.frames:
            page, x, y, w, h, digest = self.meta['rects'][index]
            if self.page_number != page:
                self.page = pygame.image.load(str(self.root / self.meta['pages'][page])).convert_alpha()
                self.page_number = page
            self.frames[index] = self.page.subsurface((x,y,w,h)).copy()
        return self.frames[index]

    def __missing__(self, actor):
        source = self.meta['actors'][actor]
        result = {}
        for state, spec in source.items():
            if state.startswith('between:'):
                continue
            clip = ActorClip(tuple(self.frame(i) for i in spec['frames']),
                             tuple(spec['durations']), spec['loop'], spec['name'])
            if 'between:'+state in source:
                clip.inbetweens.update({i:self.frame(frame) for i,frame in
                                       enumerate(source['between:'+state]['frames'])})
            result[state] = clip
        self[actor] = result
        self.page = self.page_number = None
        return result

    async def prepare_region(self, region, bridge):
        """Download and decode before simulation, yielding between actors."""
        import platform
        actors=[a for a in self.meta['actors'] if a.startswith(region+'_')]
        if all(dict.__contains__(self,a) for a in actors):
            return False
        bridge.busy(True)
        try:
            bridge.keepAssets(json.dumps([s['url'] for s in self.meta.get('downloads',{}).values()]))
            indexes={i for a in actors for s in self.meta['actors'][a].values() for i in s['frames']}
            pages=sorted({self.meta['rects'][i][0] for i in indexes})
            for n,page in enumerate(pages):
                name=self.meta['pages'][page];path=self.root/name
                if not path.exists():
                    spec=self.meta['downloads'][name]
                    bridge.statusJSON(json.dumps('Baixando animações de '+region+f' ({n+1}/{len(pages)})',ensure_ascii=True),n/len(pages)*70)
                    async with platform.fopen(spec['url'],'rb') as source:
                        raw=source.read()
                    if len(raw)!=spec['bytes'] or hashlib.sha256(raw).hexdigest()!=spec['sha256']:
                        bridge.invalidate(spec['url'])
                        raise ValueError('Arquivo de animação incompleto. Recarregue para tentar novamente.')
                    path.write_bytes(raw)
                    del raw
                await asyncio.sleep(0)
            for a in list(self.keys()):
                if a not in actors:del self[a]
            self.frames.clear()
            for n,page in enumerate(pages):
                bridge.statusJSON(json.dumps('Decodificando animações '+f'{n+1}/{len(pages)}',ensure_ascii=True),70+20*n/len(pages))
                surface=pygame.image.load(str(self.root/self.meta['pages'][page])).convert_alpha()
                for i in indexes:
                    p,x,y,w,h,_=self.meta['rects'][i]
                    if p==page:self.frames[i]=surface.subsurface((x,y,w,h)).copy()
                del surface
                await asyncio.sleep(0)
            for n,actor in enumerate(actors):
                bridge.statusJSON(json.dumps('Preparando animações '+f'{n+1}/{len(actors)}',ensure_ascii=True),70+30*n/len(actors))
                self[actor]
                await asyncio.sleep(0)
            self.frames.clear()
            keep={self.meta['pages'][p] for p in pages}
            for name in self.meta['pages']:
                path=self.root/name
                if name not in keep and path.exists():path.unlink()
            gc.collect()
        finally:
            bridge.busy(False)
        return True

