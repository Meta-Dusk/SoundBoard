import json
import flet as ft
import flet_audio as fa

from pathlib import Path
from enum import Enum


SFX_DIR = Path("assets") / "sfx"
MUSIC_DIR = Path("assets") / "music"
SETTINGS_FILE = Path("app") / "settings.json"


class MusicFile(Enum):
    PATRIOT = MUSIC_DIR / "feofilov_patriot.mp3"

class AudioFile(Enum):
    FN = SFX_DIR / "fn.mp3"
    ANEURYSM = SFX_DIR / "aneurysm.mp3"

class DEFAULTS(Enum):
    AUDIO = 1.0
    BALANCE = 0.0
    SEEK = 3

def check_audio_files():
    for sfx in AudioFile:
        if (sfx.value.exists()):
            print(f"{sfx.name}: {sfx.value}")
        else:
            print(f"AudioFile {sfx.name} does not exist!")
    for music in MusicFile:
        if (music.value.exists()):
            print(f"{music.name}: {music.value}")
        else:
            print(f"MusicFile {music.name} does not exist!")

check_audio_files()

class AudioManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.music: fa.Audio | None = None
        self.settings = self._load_settings()

    # ---------- SETTINGS ----------
    def _load_settings(self) -> dict:
        default_settings = {"volume": 1.0}
        if SETTINGS_FILE.exists():
            try:
                return json.loads(SETTINGS_FILE.read_text())
            except Exception:
                self._save_settings(default_settings)
                return default_settings
        else:
            self._save_settings(default_settings)
            return default_settings

    def _save_settings(self, settings: dict | None = None):
        data = settings if settings is not None else self.settings
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(data, indent=2))

    # ---------- SOUND EFFECTS ----------
    def play_sfx(self, audio_file: AudioFile):
        def on_state_changed(e):
            print(f"SFX State: {audio_file.name} -> {e.data}")
            if e.data == "stopped":
                self._cleanup_sfx(e.control)
        
        sfx = fa.Audio(
            src=str(audio_file.value.resolve()),
            autoplay=True,
            volume=self.settings.get("volume", 1.0),
            on_loaded=lambda _: print(f"SFX Loaded: {audio_file.name}"),
            on_state_changed=on_state_changed,
        )
        # Try page.add instead of overlay for short-lived SFX
        self.page.overlay.append(sfx)
        self.page.update()

    def _cleanup_sfx(self, sfx: fa.Audio):
        if sfx in self.page.overlay:
            self.page.overlay.remove(sfx)
            self.page.update()
        else:
            print(f"Warning: Tried to remove SFX not in overlay: {sfx.src}")

    # ---------- MUSIC ----------
    def play_music(self, music_file: MusicFile):
        if self.music:
            self.music.release()
            self.page.overlay.remove(self.music)

        self.music = fa.Audio(
            src=str(music_file.value.resolve()),
            autoplay=True,
            volume=self.settings.get("volume", 1.0),
            on_loaded=lambda _: print(f"Music Loaded: {music_file.name}"),
            on_state_changed=lambda e: print(f"Music State: {music_file.name} -> {e.data}"),
        )
        self.page.overlay.append(self.music)
        self.page.update()

    def pause_music(self):
        if self.music:
            self.music.pause()

    def resume_music(self):
        if self.music:
            self.music.resume()

    def stop_music(self):
        if self.music:
            self.music.release()
            self.page.overlay.remove(self.music)
            self.music = None
            self.page.update()

    # ---------- GENERAL ----------
    def set_volume(self, volume: float):
        volume = max(0.0, min(1.0, volume))
        self.settings["volume"] = volume
        self._save_settings()
        if self.music:
            self.music.volume = volume
            self.music.update()

# Example usage with Flet
from containers import true_center_container, default_column

def main(page: ft.Page):
    audio = AudioManager(page)

    form = [
        ft.ElevatedButton("Play FN", on_click=lambda e: audio.play_sfx(AudioFile.FN)),
        ft.ElevatedButton("Play Aneurysm", on_click=lambda e: audio.play_sfx(AudioFile.ANEURYSM)),
        ft.ElevatedButton("Play Patriot", on_click=lambda e: audio.play_music(MusicFile.PATRIOT)),
        ft.ElevatedButton("Pause", on_click=lambda e: audio.pause_music()),
        ft.ElevatedButton("Stop", on_click=lambda e: audio.stop_music()),
    ]
    
    page.add(true_center_container(default_column(form)))

if __name__ == "__main__":
    ft.app(target=main)