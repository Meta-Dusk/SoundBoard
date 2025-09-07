import random
import flet as ft

from .audio import AudioManager, Music, SFX
from typing import Callable


def master_volume_slider(
    audio: AudioManager, page: ft.Page,
    width: ft.OptionalNumber = None, height: ft.OptionalNumber = None
):
    initial_volume = audio.settings.get("volume", 1.0)
    # width = width if width is not None else page.window.width - 20
    height = height if height is not None else 30
    
    def on_resized(_):
        # print(f"Window width is: {page.window.width}")
        volume_slider.width = width if width is not None else page.window.width - 20
        volume_slider.update()
    
    page.on_resized = on_resized
    
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
    
    volume_slider = ft.Slider(
        min=0, max=1, divisions=100,
        width=width, height=height,
        value=initial_volume, adaptive=True,
        label=f"Volume: {int(initial_volume * 100)}%",
        on_change=on_volume_change,
        mouse_cursor=ft.MouseCursor.GRAB
    )
    return volume_slider

def random_music_btn(
    audio: AudioManager, loop: bool = True,
    callbacks: list[Callable[[ft.ControlEvent], None]] | None = None
):
    def play_random_music(_):
        audio.play_music(audio=random.choice(list(Music)), loop=loop)
        for cb in callbacks:
            cb(_)
    
    return ft.ElevatedButton("Play Random Music", on_click=play_random_music)

def random_sfx_btn(
    audio: AudioManager, overlap: bool = True, snackbar: bool = False,
    callbacks: list[Callable[[ft.ControlEvent], None]] | None = None,
    page: ft.Page | None = None
):
    """
    A Button that will play a randomly selected SFX in the SFX Enum class

    Args:
        audio (AudioManager): `AudioManager` instance
        overlap (bool): Whether the SFX can overlap
        snackbar (bool): Whether to display a snackbar notif on what SFX is being played
        callbacks (list): A list of callbacks that takes a `ControlEvent` and retuns `None` if you want to add more function calls
        page (Page): `Page` instance; only provide if snackbar is `True`

    Returns:
        `ElevatedButton`: A premade button for playing random SFX
    """
    def play_random_sfx(_):
        rnd_sfx = random.choice(list(SFX))
        audio.play_sfx(rnd_sfx, overlap=overlap)
        if snackbar and page:
            print("Show snackbar pls")
            snackbar_text = ft.Text(f"Playing SFX: {rnd_sfx.value.title}")
            page.open(ft.SnackBar(snackbar_text, duration=1000))
            page.update()
        if callbacks is None:
            return
        for cb in callbacks:
            cb(_)
        
    return ft.ElevatedButton("Play Random SFX", on_click=play_random_sfx)