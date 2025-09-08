import random
import flet as ft

from .audio import AudioManager, Music, SFX, DEFAULTS
from typing import Callable, Tuple

# ---------- SLIDERS ----------
def preset_slider(
    page: ft.Page, divisions: ft.OptionalNumber = 100,
    min: ft.OptionalNumber = 0, max: ft.OptionalNumber = 1,
    width: ft.OptionalNumber = None, height: ft.OptionalNumber = 30,
    automatically_resize: Tuple[bool, int] = (True, -20),
    value: ft.OptionalNumber = 0, label: str | None = "Slider"
):
    def on_resized(_):
        if automatically_resize[0]:
            slider.width = width if width is not None else page.window.width + automatically_resize[1]
            slider.update()
    
    page.on_resized = on_resized
    
    slider = ft.Slider(
        min=min, max=max, divisions=divisions,
        label=label, value=value, width=width, height=height,
        mouse_cursor=ft.MouseCursor.GRAB
    )
    return slider

def master_volume_slider(
    audio: AudioManager, page: ft.Page,
    width: ft.OptionalNumber = None, height: ft.OptionalNumber = 30
):
    """
    This component will control and update the user's saved volume settings
    
    Args:
        audio (AudioManager): `AudioManager` instance
        page (Page): `Page` instance
        width (int | float | None): Width of the slider; if None, it will resize based on the window's width
        height (int | float | None): Height of the slider
        
    Returns:
        `Slider`: A premade master volume slider
    """
    initial_volume = audio.settings.get("volume", 1.0)
    
    def on_resized(_):
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
            if hasattr(ctrl, DEFAULTS.VOLUME.name):
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

def audio_balance_slider(
    audio: AudioManager, page: ft.Page,
    width: ft.OptionalNumber = None, height: ft.OptionalNumber = 30
):
    """
    This component will control and update the audio's balance
    
    Args:
        audio (AudioManager): `AudioManager` instance
        page (Page): `Page` instance
        width (int | float | None): Width of the slider; if None, it will resize based on the window's width
        height (int | float | None): Height of the slider
        
    Returns:
        `Slider`: A premade audio balance slider
    """
    initial_volume = audio.settings.get("volume", 1.0)
    
    def on_resized(_):
        # print(f"Window width is: {page.window.width}")
        balance_slider.width = width if width is not None else page.window.width - 20
        balance_slider.update()
    
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
    
    balance_slider = ft.Slider(
        min=0, max=1, divisions=100,
        width=width, height=height,
        value=initial_volume, adaptive=True,
        label=f"Volume: {int(initial_volume * 100)}%",
        on_change=on_volume_change,
        mouse_cursor=ft.MouseCursor.GRAB
    )
    return balance_slider  


# ---------- BUTTONS ----------
def random_music_btn(
    audio: AudioManager, loop: bool = True,
    callbacks: list[Callable[[ft.ControlEvent], None]] | None = None
):
    """
    A Button that will play a randomly selected Music in the Music Enum class

    Args:
        audio (AudioManager): `AudioManager` instance
        loop (bool): Whether the Music will loop once finished playing
        callbacks (list): A list of callbacks that takes a `ControlEvent` and retuns `None` if you want to add more function calls

    Returns:
        `ElevatedButton`: A premade button for playing random Music
    """
    def play_random_music(_):
        audio.play_music(audio=random.choice(list(Music)), loop=loop)
        
        if callbacks is None:
            return
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