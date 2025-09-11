import math
import flet as ft
import flet_audio as fa

from enum import Enum
from typing import Callable
from .utilities import format_ms, check_audio
from .file_declarations import SFX, Music
from .storage import Storage


class DEFAULTS(Enum):
    VOLUME = 0.5
    BALANCE = 0.0
    SEEK = 3.0
    SAFE = True


check_audio()

class AudioManager:
    """
    The `AudioManager` handles both SFX and Music playback, and is made using `flet-audio` components.
    When making an instance of this, refer to the Args below:
    
    Args:
        page (Page): The `Page` instance.
        debug (bool): Set to `True` to print debug messages.
        debug_name (str): (Optional) The string used before outputting debug messages.
    """
    def __init__(self, page: ft.Page, debug: bool = True, debug_name: str = "[AudioManager]"):
        self.page = page
        self.music: fa.Audio | None = None
        self.sfx: fa.Audio | None = None
        self.debug: bool = True
        self.on_state_changed: Callable[[fa.AudioStateChangeEvent], None] = None
        self.on_duration_changed: Callable[[fa.AudioDurationChangeEvent], None] = None
        self.on_position_changed: Callable[[fa.AudioPositionChangeEvent], None] = None
        self.on_seek_complete: Callable[[fa.AudioStateChangeEvent], None] = None
        self.on_loaded: Callable[[], None] = None
        self.storage = Storage(page)
        self.name = debug_name
        self.debug = debug

    # ---------- SOUND EFFECTS ----------
    def play_sfx(self, audio: SFX, overlap: bool = True) -> None:
        """
        Plays a sound effect.
        
        Args:
            audio (SFX): Takes an `SFX` Enum, which is what will be played.
            overlap (bool): Set to `True` if SFX played can overlap eachother during playback.
        """
        if self.sfx and not overlap:
            self.sfx.release()
            self.page.overlay.remove(self.sfx)
            if self.debug:
                print(f"{self.name} Overriding SFX")
        
        def on_state_changed(e: fa.AudioStateChangeEvent):
            if self.debug:
                print(f"SFX State: {audio.value.title} -> {e.data}")
            if e.data == "stopped":
                self._cleanup_sfx(e.control)
                
        def on_loaded(_):
            if self.debug:
                print(f"SFX Loaded: {audio.value.title}")
            if self.on_loaded is not None:
                self.on_loaded()
        
        self.sfx = fa.Audio(
            src=audio.value.str_path,
            autoplay=True,
            volume=self.storage.get(DEFAULTS.VOLUME),
            on_loaded=on_loaded,
            on_state_changed=on_state_changed,
        )
        self.page.overlay.append(self.sfx)
        self.page.update()

    def _cleanup_sfx(self, sfx: fa.Audio):
        """Removes an SFX Audio instance."""
        if sfx in self.page.overlay:
            self.page.overlay.remove(sfx)
            self.page.update()
        else:
            print(f"Warning: Tried to remove SFX not in overlay: {sfx.src}")

    # ---------- MUSIC ----------
    def play_music(self, audio: Music, loop: bool = False):
        """
        Plays music, which will play in a different Audio object, separate from the SFX.
        
        Args:
            audio (Music): Takes a `Music` Enum, which is what will be played.
            loop (bool): Set to `True` if music will loop its playback once finished.
        """
        if self.music:
            self.music.release()
            self.page.overlay.remove(self.music)
            if self.debug:
                print(f"{self.name} Overriding Music")
            
        def on_loaded(_):
            if self.debug:
                print(f"{self.name} Music Loaded: {audio.value.title}")
            if self.on_loaded is not None:
                self.on_loaded()
                
        def on_state_changed(e: fa.AudioStateChangeEvent):
            if self.debug:
                loop_text = " (Looping)" if loop else ""
                print(f"{self.name} Music State: {audio.value.title} -> {e.state.name}" + loop_text)
            if (e.data == "completed" and loop):
                print(f"{self.name} Looping music...")
                self.play_music(audio, loop)
            if self.on_state_changed is not None:
                self.on_state_changed(e)

        self.music = fa.Audio(
            src=str(audio.value.str_path),
            data=audio.value, autoplay=True,
            volume=self.storage.get(DEFAULTS.VOLUME),
            on_loaded=on_loaded,
            on_state_changed=on_state_changed,
            on_duration_changed=self.on_duration_changed,
            on_seek_complete=self.on_seek_complete,
            on_position_changed=self.on_position_changed
        )
        self.page.overlay.append(self.music)
        self.page.update()

    def pause_music(self):
        """Pause currently loaded music in `AudioManager` instance."""
        if self.music:
            self.music.pause()

    def resume_music(self):
        """Resume currently loaded music in `AudioManager` instance."""
        if self.music:
            self.music.resume()

    def stop_music(self):
        """Stop currently loaded music in `AudioManager` instance."""
        if self.music:
            self.music.release()
            self.page.overlay.remove(self.music)
            self.music = None
            self.page.update()
            print(f"{self.name} Stopping music")
            
    def stop_all(self):
        """Stops all loaded `Audio` instances in `AudioManager`."""
        self.stop_music()
        self._cleanup_sfx()

    # ---------- GENERAL ----------
    def _perceptual_volume(self, ui_volume: float) -> float:
        """Convert linear UI volume (0.0-1.0) into a perceptual/logarithmic scale."""
        ui_volume = max(0.0001, min(1.0, ui_volume))  # clamp
        return math.pow(ui_volume, 2.0)  # quadratic dropoff (natural feel)

    def set_volume(self, volume: float):
        """Set the user volume (0.0-1.0 UI scale). Internally applies perceptual scaling for natural loudness."""
        volume = max(0.0, min(1.0, volume))  # clamp UI input
        scaled_volume = self._perceptual_volume(volume)

        # Save UI volume (not scaled) so settings.json stays intuitive
        self.storage.set(DEFAULTS.VOLUME, volume)

        if self.music:
            self.music.volume = scaled_volume
            self.music.update()
        if self.sfx:
            self.sfx.volume = scaled_volume
            self.sfx.update()

        if self.debug:
            print(f"[AudioManager | DEBUG] Volume set: UI={volume:.2f}, Scaled={scaled_volume:.4f}")
            
    def set_balance(self, balance: float):
        """Sets balance to either `Music` or `SFX`."""
        if self.music:
            self.music.balance = balance
            self.music.update()
        if self.sfx:
            self.sfx.balance = balance
            self.sfx.update()
            
        if self.debug:
            print(f"{self.name} Balance set: {balance:.2f}")
            
    def seek(self, seek: int):
        """Seeks music for `seek` amount of milliseconds."""
        if self.music:
            self.music.seek(seek)
            if self.debug:
                print(f"{self.name} Seeking music at {seek}ms ({format_ms(seek)}s)")
        else:
            if self.debug:
                print(f"{self.name} No music to seek")
            
    def get_duration(self) -> int | None:
        """Gets the duration of the current song, which can either be `int` or `None`."""
        duration: int | None = None
        
        if self.music:
            duration = self.music.get_duration()
        if self.debug:
            debug_msg = f"{self.name} Current song duration: {duration}" if duration is not None else f"{self.name} No music playing"
            print(debug_msg)
            
        return duration
    
    def get_position(self) -> int | None:
        """Gets the current timestamp or position of the current song playing."""
        position: int | None = None
        
        if self.music:
            position = self.music.get_current_position()
        if self.debug:
            debug_msg = f"{self.name} Current song timestamp: {position}" if position is not None else f"{self.name} No music playing"
            print(debug_msg)
            
        return position
        

'''
Example usage with Flet
Run with:
py -m app.audio
'''
import random

from .containers import default_column
from .styles import base_page


def test(page: ft.Page):
    storage = Storage(page)
    audio = AudioManager(page)
    base_page(page)
    
    paused: bool = False
    
    def on_volume_change(e: ft.ControlEvent):
        slider: ft.Slider = e.control
        v = slider.value
        audio.set_volume(v) # saves UI value and updates music (if playing)

        # update slider label to show percentage
        slider.label = f"Volume: {int(v * 100)}%"
        slider.update()

        # update any active audio controls in page.overlay (SFX etc.)
        scaled = audio._perceptual_volume(v)
        for ctrl in list(page.overlay):
            ctrl: fa.Audio
        # many overlay items aren't audio controls; be defensive
            if hasattr(ctrl, "volume"):
                try:
                    ctrl.volume = scaled
                    ctrl.update()
                except Exception:
                    # ignore objects that look like audio but cannot be updated
                    pass
    
    def on_pause(_):
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
        
    def on_stop(_):
        nonlocal paused
        
        if audio.music:
            if paused:
                paused = False
                pause_btn.text = "Pause Music"
            
            audio.stop_music()
            pause_btn.disabled = True
            paused = False
            pause_btn.update()
    
    def play_random_music(_):
        audio.play_music(audio=random.choice(list(Music)), loop=True)
        pause_btn.disabled = False
        pause_btn.update()
        
    initial_volume = storage.get(DEFAULTS.VOLUME)

    volume_slider = ft.Slider(
        min=0, max=1, divisions=100, value=initial_volume,
        label=f"Volume: {int(initial_volume * 100)}%",
        on_change=on_volume_change,
    )
        
    pause_btn = ft.ElevatedButton("Pause Music", on_click=on_pause, disabled=True)
    stop_btn = ft.ElevatedButton("Stop Music", on_click=on_stop)

    form = [
        ft.Text("Master Volume"),
        volume_slider,
        ft.ElevatedButton("Play FN", on_click=lambda _: audio.play_sfx(SFX.FN)),
        ft.ElevatedButton("Play Aneurysm", on_click=lambda _: audio.play_sfx(SFX.ANEURYSM)),
        ft.ElevatedButton("Play Random Music", on_click=play_random_music),
        pause_btn,
        stop_btn,
    ]
    
    page.add(default_column(form))

if __name__ == "__main__":
    ft.app(target=test)