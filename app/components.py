import random
import flet as ft
import flet_audio as fa

from .audio import AudioManager, DEFAULTS
from .utilities import format_ms
from .file_declarations import SFX, Music, Sound
from typing import Callable

# ---------- SLIDERS ----------
def preset_slider(
    divisions: ft.OptionalNumber = 100,
    min: ft.OptionalNumber = 0, max: ft.OptionalNumber = 1,
    width: ft.OptionalNumber = None, height: ft.OptionalNumber = 30,
    value: ft.OptionalNumber = 0, label: str | None = "Slider",
    on_change: ft.OptionalControlEventCallable = None,
    on_change_end: ft.OptionalControlEventCallable = None,
    on_change_start: ft.OptionalControlEventCallable = None,
    tooltip: str = None, disabled: bool = False
) -> ft.Slider:
    """This is a premade slider component for use with audio settings"""
    
    slider = ft.Slider(
        min=min, max=max, divisions=divisions, tooltip=tooltip,
        label=label, value=value, width=width, height=height,
        mouse_cursor=ft.MouseCursor.GRAB, adaptive=True,
        on_change=on_change, on_change_end=on_change_end,
        on_change_start=on_change_start, disabled=disabled,
        expand=True
    )
    return slider

def master_volume_slider(audio: AudioManager, page: ft.Page) -> ft.Slider:
    """This component will control and update the user's saved volume settings"""
    initial_volume = audio._get_settings(DEFAULTS.VOLUME)
    
    def on_volume_change(e: ft.ControlEvent):
        slider: ft.Slider = e.control
        volume = slider.value
        audio.set_volume(volume) # saves UI value and updates music (if playing)

        # update slider label to show percentage
        slider.label = f"Volume: {int(volume * 100)}%"
        slider.update()

        # update any active audio controls in page.overlay (SFX etc.)
        scaled = audio._perceptual_volume(volume)
        for ctrl in list(page.overlay):
        # many overlay items aren't audio controls; be defensive
            if hasattr(ctrl, DEFAULTS.VOLUME.name):
                try:
                    ctrl.volume = scaled
                    ctrl.update()
                except Exception:
                    # ignore objects that look like audio but cannot be updated
                    pass
    
    volume_slider = preset_slider(
        value=initial_volume,
        label=f"Volume: {int(initial_volume * 100)}%",
        on_change=on_volume_change, tooltip="Set Master Volume"
    )
    return volume_slider

def audio_balance_slider(audio: AudioManager) -> ft.Slider:
    """This component will control and update the audio's balance"""
    initial_balance = audio._get_settings(DEFAULTS.BALANCE)
    
    def on_balance_change(e: ft.ControlEvent):
        slider: ft.Slider = e.control
        balance = slider.value
        audio.set_balance(balance) # saves UI value and updates music (if playing)

        slider.label = f"Balance: {balance:.2f}"
        slider.update()
    
    balance_slider = preset_slider(
        value=initial_balance, min=-1,
        label=f"Balance: {initial_balance:.2f}",
        on_change=on_balance_change, tooltip="Set Audio Balance"
    )
    return balance_slider  

def audio_duration_slider(audio: AudioManager, label: ft.Text) -> ft.Slider:
    """This component will show the current music playing, its duration and current timestamp"""
    seeking: bool = False
    
    def on_duration_changed(e: fa.AudioDurationChangeEvent):
        audio_slider.max = e.duration if e.duration is not None else 1
        audio_slider.update()
        
    def on_position_changed(e: fa.AudioPositionChangeEvent):
        if not seeking:
            audio_slider.value = e.position
            audio_slider.update()
            label.value = f"{format_ms(audio_slider.value)}/{format_ms(audio_slider.max)}"
            label.update()
            if audio.debug:
                audio_data: Sound = audio.music.data
                print(f"{audio_data.title} :: {label.value}")
        
    audio.on_duration_changed = on_duration_changed
    audio.on_position_changed = on_position_changed
    
    def on_change(_):
        label.value = f"{format_ms(audio_slider.value)}/{format_ms(audio_slider.max)}"
        label.update()
        
    def on_change_start(_):
        nonlocal seeking
        seeking = True
        
    def on_change_end(_):
        nonlocal seeking
        audio.seek(int(audio_slider.value))
        seeking = False
    
    audio_slider = preset_slider(
        value=0, label=None, disabled=True, on_change=on_change,
        on_change_start=on_change_start, on_change_end=on_change_end,
        divisions=None
    )
    return audio_slider


# ---------- BUTTONS ----------
def random_music_btn(
    audio: AudioManager, loop: bool = True,
    callbacks: list[Callable[[ft.ControlEvent], None]] | None = None,
    alt_music: list[Sound] = None
):
    """
    A button that will play a randomly selected music in the `Music` enum class

    Args:
        audio (AudioManager): `AudioManager` instance
        loop (bool): Whether the music will loop once finished playing
        safe (bool): Enable to exclude playing explicit music (only works if `alt_music` is not `None`)
        callbacks (list): A list of callbacks that takes a `ControlEvent` and retuns `None` if you want to add more function calls

    Returns:
        `ElevatedButton`: A premade button for playing random Music
    """
    def play_random_music(_):
        safe: bool = audio.settings["SAFE"]
        
        if not safe:
            print("Explicit content enabled")
            audio.play_music(audio=random.choice(list(Music)), loop=loop)
        else:
            if alt_music is not None:
                print("Explicit content disabled")
                audio.play_music(audio=random.choice(alt_music), loop=loop)
            else:
                raise ValueError("alt_music cannot be None, and must be a list of Sound")
        
        if callbacks is None:
            return
        for cb in callbacks:
            cb(_)
    
    return ft.ElevatedButton("Play Random Music", on_click=play_random_music)

def random_sfx_btn(
    audio: AudioManager, overlap: bool = True, snackbar: bool = False,
    callbacks: list[Callable[[ft.ControlEvent], None]] | None = None,
    page: ft.Page | None = None, alt_sfx: list[Sound] = None
):
    """
    A button that will play a randomly selected SFX in the `SFX` enum class

    Args:
        audio (AudioManager): `AudioManager` instance
        overlap (bool): Whether the SFX can overlap
        snackbar (bool): Whether to display a snackbar notif on what SFX is being played
        callbacks (list): A list of callbacks that takes a `ControlEvent` and retuns `None` if you want to add more function calls
        page (Page): `Page` instance; only provide if snackbar is `True`
        safe (bool): Enable to exclude playing explicit SFX (only works if `alt_sfx` is not `None`)

    Returns:
        `ElevatedButton`: A premade button for playing random SFX
    """
    def play_random_sfx(_):
        rnd_sfx: SFX = None
        safe: bool = audio.settings["SAFE"]
        
        if not safe:
            print("Explicit content enabled")
            rnd_sfx = random.choice(list(SFX))
            audio.play_sfx(rnd_sfx, overlap=overlap)
        else:
            if alt_sfx is not None:
                print("Explicit content disabled")
                rnd_sfx = random.choice(alt_sfx)
                audio.play_sfx(rnd_sfx, overlap=overlap)
            else:
                raise ValueError("alt_sfx cannot be None, and must be a list of Sound")
        
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