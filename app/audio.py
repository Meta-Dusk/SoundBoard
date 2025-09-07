import json
import math
import flet as ft
import flet_audio as fa

from pathlib import Path
from enum import Enum
from dataclasses import dataclass


SFX_DIR = Path("assets") / "sfx"
MUSIC_DIR = Path("assets") / "music"
SETTINGS_FILE = Path("app") / "settings.json"

@dataclass
class Sound:
    str_path: str
    title: str
    description: str = "No description"

# 🎵 Music
class Music(Enum):
    PATRIOT = Sound((MUSIC_DIR / "patriot.mp3").resolve(), "Feofilov - Patriot", "prod. DJ PIČKA x DJ PEDOPHILE feat. DJ CIGAN")
    NECKHURTS = Sound((MUSIC_DIR / "neckhurts.mp3").resolve(), "Neckhurts (Tiktok remix bass boosted)", "Perfect club music")
    PATAPIM = Sound((MUSIC_DIR / "patapim.mp3").resolve(), "Brr Brr Patapim Alarm😴⏰", "A perfect alarm to wake up to")

# 🔊 Sound Effects
class SFX(Enum):
    FN = Sound((SFX_DIR / "fn.wav").resolve(), "Puck Higgens", "ifykyk")
    ANEURYSM = Sound((SFX_DIR / "aneurysm.wav").resolve(), "Brain Aneurysm", "Yep")
    AMONGUS = Sound((SFX_DIR / "amongus.wav").resolve(), "Amongus", "It's just a dude shouting amongus")
    CATLAUGH = Sound((SFX_DIR / "catlaugh.wav").resolve(), "Cat Laugh (Loud)", "A cat laughing at you at your expense")
    GOOFYHORN = Sound((SFX_DIR / "goofyhorn.wav").resolve(), "Goofy Car Horn", "Goofy ahh horn... Use responsibly")
    HOLYMOLY = Sound((SFX_DIR / "holymoly.wav").resolve(), "Holy Moly 😮", "Woah")
    KUYASHI = Sound((SFX_DIR / "kuyashi.wav").resolve(), "くやし 😡", "It means frustration")
    YATTA = Sound((SFX_DIR / "yatta.wav").resolve(), "やった 😆", "It means yippe")
    NESQUICK = Sound((SFX_DIR / "nesquick.wav").resolve(), "Nesquick", "ifykyk (1)")

class DEFAULTS(Enum):
    AUDIO = 1.0
    BALANCE = 0.0
    SEEK = 3

def check_audio():
    sfx_count = 0
    music_count = 0

    print("Checking registered SFX...\n")
    for sfx in SFX:
        if Path(sfx.value.str_path).exists():
            print(f"{sfx.name}: {sfx.value.str_path}")
            sfx_count += 1
        else:
            print(f"SFX {sfx.name} does not exist at {sfx.value.str_path}!")
    print(f"Found {sfx_count}/{len(SFX)} SFX\n")

    print("Checking registered Music...\n")
    for music in Music:
        if Path(music.value.str_path).exists():
            print(f"{music.name}: {music.value.str_path}")
            music_count += 1
        else:
            print(f"Music {music.name} does not exist at {music.value.str_path}!")
    print(f"Found {music_count}/{len(Music)} Music\n")

    if sfx_count == len(SFX) and music_count == len(Music):
        print("✅ All sound files are fully registered!\n")
    else:
        print("⚠️ Some files are missing.\n")

check_audio()

class AudioManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.music: fa.Audio | None = None
        self.sfx: fa.Audio | None = None
        self.settings = self._load_settings()
        self.debug: bool = True

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
    def play_sfx(self, audio: SFX, overlap: bool = True):
        if self.sfx and not overlap:
            self.sfx.release()
            self.page.overlay.remove(self.sfx)
            print("[AudioManager] Overriding SFX")
        
        def on_state_changed(e):
            if (self.debug):
                print(f"SFX State: {audio.value.title} -> {e.data}")
            if e.data == "stopped":
                self._cleanup_sfx(e.control)
                
        def on_loaded(e):
            if (self.debug):
                print(f"SFX Loaded: {audio.value.title}")
        
        self.sfx = fa.Audio(
            src=str(audio.value.str_path),
            autoplay=True,
            volume=self.settings.get("volume", 1.0),
            on_loaded=on_loaded,
            on_state_changed=on_state_changed,
        )
        self.page.overlay.append(self.sfx)
        self.page.update()

    def _cleanup_sfx(self, sfx: fa.Audio):
        if sfx in self.page.overlay:
            self.page.overlay.remove(sfx)
            self.page.update()
        else:
            print(f"Warning: Tried to remove SFX not in overlay: {sfx.src}")

    # ---------- MUSIC ----------
    def play_music(self, audio: Music, loop: bool = False):
        if self.music:
            self.music.release()
            self.page.overlay.remove(self.music)
            print("[AudioManager] Overriding Music")
            
        def on_loaded(e):
            if (self.debug):
                print(f"[AudioManager] Music Loaded: {audio.value.title}")
                
        def on_state_changed(e):
            if (self.debug):
                loop_text = " (Looping)" if loop else ""
                print(f"[AudioManager] Music State: {audio.value.title} -> {e.data}" + loop_text)
            if (e.data == "completed" and loop):
                print("[AudioManager] Looping music...")
                self.play_music(audio, loop)

        self.music = fa.Audio(
            src=str(audio.value.str_path),
            autoplay=True,
            volume=self.settings.get("volume", DEFAULTS.AUDIO.value),
            on_loaded=on_loaded,
            on_state_changed=on_state_changed,
        )
        self.page.overlay.append(self.music)
        self.page.update()
        # self.music.play()

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
            
    def stop_all(self):
        self.stop_music()
        self._cleanup_sfx()

    # ---------- GENERAL ----------
    def _perceptual_volume(self, ui_volume: float) -> float:
        """
        Convert linear UI volume (0.0-1.0) into a perceptual/logarithmic scale.
        """
        ui_volume = max(0.0001, min(1.0, ui_volume))  # clamp
        return math.pow(ui_volume, 2.0)  # quadratic dropoff (natural feel)

    def set_volume(self, volume: float):
        """
        Set the user volume (0.0-1.0 UI scale).
        Internally applies perceptual scaling for natural loudness.
        """
        volume = max(0.0, min(1.0, volume))  # clamp UI input
        scaled_volume = self._perceptual_volume(volume)

        # Save UI volume (not scaled) so settings.json stays intuitive
        self.settings["volume"] = volume
        self._save_settings()

        if self.music:
            self.music.volume = scaled_volume
            self.music.update()

        if self.debug:
            print(f"[DEBUG] Volume set: UI={volume:.2f}, Scaled={scaled_volume:.4f}")

'''
Example usage with Flet
Run with:
py -m app.audio
'''
import random

from .containers import true_center_container, default_column
from .styles import base_page


def test(page: ft.Page):
    audio = AudioManager(page)
    base_page(page)
    
    def on_volume_change(e: ft.ControlEvent):
        v = e.control.value
        audio.set_volume(v) # saves UI value and updates music (if playing)

        # update slider label to show percentage
        e.control.label = f"Volume: {int(v * 100)}%"
        e.control.update()

        # update any active audio controls in page.overlay (SFX etc.)
        scaled = audio._perceptual_volume(v)
        for ctrl in list(page.overlay):
        # many overlay items aren't audio controls; be defensive
            if hasattr(ctrl, "volume"):
                try:
                    ctrl.volume = scaled
                    ctrl.update()
                except Exception:
                    # ignore objects that look like audio but cannot be updated
                    pass

    initial_volume = audio.settings.get("volume", 1.0)

    volume_slider = ft.Slider(
        min=0,
        max=1,
        divisions=100,
        value=initial_volume,
        label=f"Volume: {int(initial_volume * 100)}%",
        on_change=on_volume_change,
    )
    
    paused: bool = False
    
    def on_pause(e):
        nonlocal paused
        
        if paused:
            audio.resume_music()
            paused = False
            pause_btn.text = "Pause Music"
        else:
            audio.pause_music()
            paused = True
            pause_btn.text = "Resume Music"
        pause_btn.update()
        
    def on_stop(e):
        nonlocal paused
        
        if audio.music:
            if paused:
                paused = False
                pause_btn.text = "Pause Music"
            
            audio.stop_music()
            pause_btn.disabled = True
            paused = False
            pause_btn.update()
    
    def play_random_music(e):
        audio.play_music(audio=random.choice(list(Music)), loop=True)
        pause_btn.disabled = False
        pause_btn.update()
        
    pause_btn = ft.ElevatedButton("Pause Music", on_click=on_pause, disabled=True)
    stop_btn = ft.ElevatedButton("Stop Music", on_click=on_stop)

    form = [
        ft.Text("Master Volume"),
        volume_slider,
        ft.ElevatedButton("Play FN", on_click=lambda e: audio.play_sfx(SFX.FN)),
        ft.ElevatedButton("Play Aneurysm", on_click=lambda e: audio.play_sfx(SFX.ANEURYSM)),
        ft.ElevatedButton("Play Random Music", on_click=play_random_music),
        pause_btn,
        stop_btn,
    ]
    
    page.add(true_center_container(default_column(form)))

if __name__ == "__main__":
    ft.app(target=test)