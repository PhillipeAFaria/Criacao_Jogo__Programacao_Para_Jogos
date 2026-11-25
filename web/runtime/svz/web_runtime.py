"""Async browser adapter; campaign and combat remain in Game/Battle."""
import asyncio
import json
import time
import pygame
from . import app
from .web_audio import WebAudioSystem

# Browser-only dependency; shared Windows implementation remains unchanged.
app.AudioSystem = WebAudioSystem
Game = app.Game
from .paths import data_dir
from .web_storage import BrowserStorage

class WebGame(Game):
    pending_web_action = None

    def enter_selection(self, region):
        self.pending_web_action = ('start',region)

    def resume_battle(self):
        region = self.battle.region if self.battle else (self.pending_snapshot or {}).get('battle',{}).get('region','city')
        self.pending_web_action = ('resume',region)
        return True

    async def settle_assets(self):
        region=None
        if self.pending_web_action:region=self.pending_web_action[1]
        elif self.scene=='developer':region=self.developer_lab.region
        elif self.scene=='characters':region=self.character_region
        elif self.scene=='story':region=('city','desert','beach')[self.story_page]
        elif self.scene=='battle':region=self.battle.region
        if region:
            self.assets.prepare_production_animations()
            if await self.assets.production_clips.prepare_region(region,self.bridge):
                self.assets.scale_cache.clear();self.assets.trim_cache.clear()
                self.stepper.remainder=0.0
            pending=self.pending_web_action
            self.pending_web_action=None
            if pending:
                if pending[0]=='start':super().enter_selection(region)
                else:super().resume_battle()

    async def browser_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:self.request_quit()
            elif event.type in (pygame.WINDOWFOCUSLOST,pygame.WINDOWMINIMIZED):
                if self.scene=='battle' and self.battle:
                    self.battle.paused=True;self.checkpoint()
            elif event.type==pygame.KEYDOWN:self.handle_key(event.key,getattr(event,'mod',0))
            elif event.type==pygame.MOUSEMOTION:
                self.navigation.visible=False;self.hover_card=None
            await self.settle_assets()

    def toggle_fullscreen(self):
        self.bridge.fullscreen()
        return True

    def click_profile(self, pos):
        if self.profile_name_rect().collidepoint(pos):
            self.bridge.editNameJSON(json.dumps(self.profile_name_draft,ensure_ascii=True))
            return
        super().click_profile(pos)

    def checkpoint(self):
        ok = super().checkpoint()
        if hasattr(self, 'storage'):
            ok = self.storage.flush() and ok
        return ok

    async def commands(self):
        for command in json.loads(self.bridge.drain()):
            name = command.get('action')
            if name == 'name':
                self.profile_name_draft = str(command.get('value',''))[:20]
                self.save_profile()
            elif name == 'click':
                self.handle_click((int(command['x']),int(command['y'])))
            elif name == 'lab' and self.scene == 'title':
                self.handle_key(pygame.K_F12)
            elif name == 'lab_action' and self.scene == 'developer':
                self.developer_lab.action(str(command.get('value','')))
            elif name == 'menu':
                self.handle_key(pygame.K_ESCAPE)
            elif name == 'pause':
                self.handle_key(pygame.K_SPACE if self.scene == 'developer' else pygame.K_p)
            elif name == 'wave' and self.scene == 'battle' and self.battle:
                self.battle.start_next_wave()
            elif name == 'card' and self.scene == 'battle' and self.battle:
                index = int(command.get('value',-1))
                rects = self.battle.card_rects()
                if 0 <= index < len(rects):
                    self.handle_click(rects[index].center)
            elif name == 'remove':
                self.handle_key(pygame.K_r)
            elif name == 'info':
                self.show_card_info = not self.show_card_info
            elif name == 'sound':
                self.audio.set_enabled(not self.audio.enabled)
                self.save_settings()
            elif name == 'save':
                self.checkpoint()
                self.storage.flush()
            elif name == 'hidden':
                if self.battle:
                    self.battle.paused = True
                if self.scene == 'developer':
                    self.developer_lab.paused = True
                self.checkpoint()
                self.audio.set_suspended(True)
            elif name == 'visible':
                self.audio.set_suspended(bool(self.bridge.isHidden()))
            elif name in ('medkit','ammo'):
                self.handle_key(pygame.K_h if name == 'medkit' else pygame.K_t)
            await self.settle_assets()

async def run(bridge):
    storage = BrowserStorage(data_dir(),bridge)
    storage.restore()
    bridge.statusJSON(json.dumps('Preparando o jogo…',ensure_ascii=True),0)
    await asyncio.sleep(0)
    # Configure before Game calls pygame.init(); the browser needs more buffering.
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
    game = WebGame()
    game.bridge, game.storage = bridge, storage
    game.control_mode = 'mouse'
    previous = time.perf_counter()
    reported = flushed = previous
    while True:
        now = time.perf_counter()
        hidden = bool(bridge.isHidden())
        game.audio.set_suspended(hidden)
        await game.commands()
        await game.browser_events()
        # Download/decoding time is not simulated as elapsed combat time.
        current=time.perf_counter()
        if current-now>.15:previous=current;now=current
        if not game.running:
            game.checkpoint()
            game.running = True
            game.scene = 'title'
        if not hidden:
            game.stepper.advance(min(.1,now-previous),game.simulation_step)
            game.draw()
            game.present_frame()
        previous = now
        if now-flushed > 1:
            storage.flush()
            flushed = now
        if now-reported > .2:
            lab = game.developer_lab if game.scene == 'developer' else None
            active = lab.battle if lab else game.battle
            bridge.state(json.dumps({'scene':game.scene,'loaded':game.assets.loaded,
                'total':game.assets.total,'error':game.assets.error or storage.error,
                'audio':game.audio.ready,'sound':game.audio.enabled,
                'player':game.player_name,'saved':bool(storage.last),
                'wave':game.battle.wave if game.battle else 0,
                'cards': [name for key,name in game.battle.selected] if game.scene == 'battle' and game.battle else [],
                'lab': {'region':lab.region,'team':lab.team,'index':lab.index,
                        'entries':lab.entries(),'paused':lab.paused} if lab else None,
                'combat': {'paused':active.paused if not lab else lab.paused,
                           'soldiers':[{'hp':u.hp,'row':u.row} for u in active.defenders],
                           'enemies':[{'hp':u.hp,'x':u.x,'row':u.row} for u in active.enemies]} if active else None}))
            reported = now
        await asyncio.sleep(0)
