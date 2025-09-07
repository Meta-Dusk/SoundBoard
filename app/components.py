import random
import flet as ft

from .audio import AudioManager, Music, SFX


def master_volume_slider(audio: AudioManager, page: ft.Page):
    initial_volume = audio.settings.get("volume", 1.0)
    
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
    
    return ft.Slider(
        min=0,
        max=1,
        divisions=100,
        value=initial_volume,
        label=f"Volume: {int(initial_volume * 100)}%",
        on_change=on_volume_change,
    )
    
def random_music_btn(audio: AudioManager, loop: bool = True):
    def play_random_music(_):
        audio.play_music(audio=random.choice(list(Music)), loop=loop)
    
    return ft.ElevatedButton("Play Random Music", on_click=play_random_music)

def random_sfx_btn(audio: AudioManager, overlap: bool = True):
    def play_random_sfx(e):
        audio.play_sfx(random.choice(list(SFX)), overlap=overlap)
        
    return ft.ElevatedButton("Play Random SFX", on_click=play_random_sfx)