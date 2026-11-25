"""Browser audio owns its loops and discards stale effects on tab changes."""
import pygame
from .audio import AudioSystem


class WebAudioSystem(AudioSystem):
    def __init__(self):
        self.suspended = False
        self.scene = "title"
        self.region = None
        super().__init__()
        if self.ready:
            # Base loops use channels 6/7. Reserve 0..7 before any Sound.play().
            pygame.mixer.set_num_channels(24)
            pygame.mixer.set_reserved(8)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        if not self.ready:
            return
        if not self.enabled:
            self._stop()
        else:
            self.sync(self.scene, self.region)

    def _stop(self):
        pygame.mixer.stop()
        self.music_started = False
        self.current_ambience = None

    def set_suspended(self, suspended):
        suspended = bool(suspended)
        if suspended == self.suspended:
            return
        self.suspended = suspended
        if not self.ready:
            return
        if suspended:
            self._stop()
        else:
            self.sync(self.scene, self.region)

    def sync(self, scene, region=None):
        self.scene, self.region = scene, region
        if not self.ready or not self.enabled or self.suspended:
            return
        # Own loop state, not a per-frame get_busy()/restart race in the backend.
        if not self.music_started:
            self.music_channel.play(self.sounds["music_menu"], loops=-1)
            self.music_started = True
        wanted = f"ambience_{region}" if scene == "battle" and region else None
        if wanted not in self.sounds:
            wanted = None
        if wanted != self.current_ambience:
            self.ambience_channel.stop()
            self.current_ambience = wanted
            if wanted:
                self.ambience_channel.play(self.sounds[wanted], loops=-1)

    def play(self, name, *, min_interval_ms=0):
        if not self.suspended:
            super().play(name, min_interval_ms=min_interval_ms)
