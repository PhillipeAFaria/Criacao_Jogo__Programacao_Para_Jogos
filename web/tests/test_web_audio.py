import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

path = Path(__file__).resolve().parents[1]/"runtime/svz/web_audio.py"
spec = importlib.util.spec_from_file_location("svz.web_audio", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WebAudioTests(unittest.TestCase):
    def setUp(self):
        self.audio = module.WebAudioSystem.__new__(module.WebAudioSystem)
        self.audio.ready = self.audio.enabled = True
        self.audio.suspended = self.audio.music_started = False
        self.audio.scene, self.audio.region = "title", None
        self.audio.current_ambience = None
        self.audio.music_channel, self.audio.ambience_channel = Mock(), Mock()
        self.audio.sounds = {k: Mock() for k in ("music_menu", "ambience_city", "ambience_beach", "shot")}
        self.audio.last_played = {}

    def test_repeated_frames_do_not_restart_loops(self):
        for _ in range(100):
            self.audio.sync("battle", "city")
        self.audio.music_channel.play.assert_called_once()
        self.audio.ambience_channel.play.assert_called_once()
        self.audio.music_channel.get_busy.assert_not_called()

    @patch.object(module.pygame.mixer, "stop")
    def test_hidden_discards_effects_and_return_restores_once(self, stop):
        self.audio.sync("battle", "city")
        self.audio.set_suspended(True)
        self.audio.set_suspended(True)
        self.audio.play("shot")
        self.audio.sync("battle", "city")
        stop.assert_called_once()
        self.audio.sounds["shot"].play.assert_not_called()
        self.audio.set_suspended(False)
        self.audio.set_suspended(False)
        self.assertEqual(self.audio.music_channel.play.call_count, 2)
        self.assertEqual(self.audio.ambience_channel.play.call_count, 2)

    @patch.object(module.pygame.mixer, "stop")
    def test_muted_stays_muted_across_visibility(self, stop):
        self.audio.set_enabled(False)
        self.audio.set_suspended(True)
        self.audio.set_suspended(False)
        self.audio.music_channel.play.assert_not_called()
        self.audio.set_enabled(True)
        self.audio.set_enabled(True)
        self.audio.music_channel.play.assert_called_once()

    def test_scene_change_stops_old_ambience_before_start(self):
        self.audio.sync("battle", "city")
        self.audio.sync("battle", "beach")
        self.audio.sync("title")
        self.assertEqual(self.audio.ambience_channel.stop.call_count, 3)
        self.assertEqual(self.audio.ambience_channel.play.call_count, 2)
        self.audio.music_channel.play.assert_called_once()

    def test_effects_cannot_occupy_music_and_ambience_channels(self):
        import os
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame = module.pygame
        pygame.mixer.init()
        def library(audio):
            audio.sounds = {key: pygame.mixer.Sound(buffer=bytes(44100*4))
                            for key in ("music_menu", "ambience_city", "shot")}
            audio.base_volumes = {}
        try:
            with patch.object(module.WebAudioSystem, "_load_library", library):
                audio = module.WebAudioSystem()
            self.assertTrue(audio.ready, audio.error)
            audio.sync("battle", "city")
            for _ in range(40):
                audio.play("shot")
            self.assertEqual(pygame.mixer.Channel(6).get_sound(), audio.sounds["music_menu"])
            self.assertEqual(pygame.mixer.Channel(7).get_sound(), audio.sounds["ambience_city"])
            audio.set_suspended(True)
            self.assertFalse(pygame.mixer.get_busy())
            audio.set_suspended(False)
            self.assertEqual(sum(pygame.mixer.Channel(i).get_busy() for i in range(24)), 2)
        finally:
            pygame.mixer.quit()
