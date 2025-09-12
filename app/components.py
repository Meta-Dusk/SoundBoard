import random
import flet as ft
import flet_audio as fa

from .audio import AudioManager, DEFAULTS
from .utilities import format_ms
from .file_declarations import SFX, Music, Sound
from .storage import Storage
from .popups import simple_popup
from .buttons import preset_sound_btn
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
    tooltip: str = None, disabled: bool = False, expand: bool | int = True
) -> ft.Slider:
    """This is a premade slider component for use with audio settings"""
    
    slider = ft.Slider(
        min=min, max=max, divisions=divisions, tooltip=tooltip,
        label=label, value=value, width=width, height=height,
        mouse_cursor=ft.MouseCursor.GRAB, adaptive=True,
        on_change=on_change, on_change_end=on_change_end,
        on_change_start=on_change_start, disabled=disabled,
        expand=expand
    )
    return slider

# TODO: Migrate slider data to a class
def master_volume_slider(audio: AudioManager, page: ft.Page, storage: Storage) -> ft.Slider:
    """
    This component will control and update the user's saved volume settings.
    
    Args:
        audio (AudioManager): The `AudioManager` instance.
        page (Page): The `Page` instance.
        storage (Storage): The `Storage` instance.
    
    Returns:
        `Slider`: A premade slider that will represent the global volume of all audio.
    """
    initial_volume = storage.get(DEFAULTS.VOLUME)
    
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

def audio_balance_slider(audio: AudioManager, storage: Storage) -> ft.Slider:
    """
    This component will control and update all audio balance found in the `AudioManager`.
    
    Args:
        audio (AudioManager): The `AudioManager` instance.
        storage (Storage): The `Storage` instance.
    
    Returns:
        `Slider`: A premade slider that will represent the balance value of all audio.
    """
    initial_balance = storage.get(DEFAULTS.BALANCE)
    
    def on_balance_change(e: ft.ControlEvent):
        slider: ft.Slider = e.control
        balance = slider.value
        audio.set_balance(balance) # saves UI value and updates music (if playing)
        storage.set(DEFAULTS.BALANCE, round(balance, 2))

        slider.label = f"Balance: {balance:.2f}"
        slider.update()
    
    balance_slider = preset_slider(
        value=initial_balance, min=-1,
        label=f"Balance: {initial_balance:.2f}",
        on_change=on_balance_change, tooltip="Set Audio Balance"
    )
    return balance_slider  

def audio_duration_slider(audio: AudioManager, label: ft.Text) -> ft.Slider:
    """
    This component will show the current music playing, its duration, and current timestamp.
    
    Args:
        audio (AudioManager): The `AudioManager` instance.
        label (Text): The `Text` object of which will serve as the dynamic label.
    
    Returns:
        `Slider`: A premade slider that will represent the playback status of the current music.
    """
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
    audio: AudioManager, safe: bool, loop: bool = True,
    callbacks: list[Callable[[], None]] | None = None,
    alt_music: list[Sound] = None
)-> ft.ElevatedButton:
    """
    A button that will play a randomly selected music in the `Music` Enum class.

    Args:
        audio (AudioManager): The `AudioManager` instance.
        safe (bool): Enable to exclude playing explicit music (only works if `alt_music` is not `None`).
        loop (bool): Whether the music will loop once finished playing.
        callbacks (list): A list of callbacks that retuns `None` if you want to add more function calls.
        alt_sfx (list): A list of alternate `Sound` to choose from when `safe` is `True`.

    Returns:
        `ElevatedButton`: A premade button for playing random Music.
    """
    def play_random_music(_):
        if not safe:
            audio.play_music(audio=random.choice(list(Music)), loop=loop)
        else:
            if alt_music is not None:
                audio.play_music(audio=random.choice(alt_music), loop=loop)
            else:
                raise ValueError("alt_music cannot be None, and must be a list of Sound")
        
        if callbacks is None:
            return
        for cb in callbacks:
            cb(_)
    
    return preset_sound_btn("Play Random Music", on_click=play_random_music, icon=ft.Icons.QUEUE_MUSIC)

def random_sfx_btn(
    audio: AudioManager, page: ft.Page, safe: bool,
    overlap: bool = True, snackbar: bool = False,
    callbacks: list[Callable[[], None]] | None = None,
    alt_sfx: list[Sound] = None
)-> ft.ElevatedButton:
    """
    A button that will play a randomly selected SFX in the `SFX` Enum class.

    Args:
        audio (AudioManager): The `AudioManager` instance.
        page (Page): The `Page` instance; only provide if snackbar is `True`.
        safe (bool): Enable to exclude playing explicit SFX (only works if `alt_sfx` is provided).
        overlap (bool): Whether the SFX can overlap.
        snackbar (bool): Whether to display a snackbar notif on what SFX is being played.
        callbacks (list): A list of callbacks that retuns `None` if you want to add more function calls.
        alt_sfx (list): A list of alternate `Sound` to choose from when `safe` is `True`.

    Returns:
        `ElevatedButton`: A premade button for playing random SFX.
    """
    def play_random_sfx(_):
        rnd_sfx: SFX = None
        
        if not safe:
            rnd_sfx = random.choice(list(SFX))
            audio.play_sfx(rnd_sfx, overlap=overlap)
        else:
            if alt_sfx is not None:
                rnd_sfx = random.choice(alt_sfx)
                audio.play_sfx(rnd_sfx, overlap=overlap)
            else:
                raise ValueError("alt_sfx cannot be None, and must be a list of Sound")
        
        if snackbar and page:
            page.open(simple_popup(f"Playing SFX: {rnd_sfx.value.title}"))
            page.update()
            
        if callbacks is None:
            return
        for cb in callbacks:
            cb(_)
        
    return preset_sound_btn("Play Random SFX", on_click=play_random_sfx, icon=ft.Icons.QUEUE_MUSIC)

def sfx_btn(
    audio: AudioManager, page: ft.Page, sfx: SFX,
    overlap: bool = True, snackbar: bool = False,
    callbacks: list[Callable[[], None]] | None = None,
    disabled: bool = False
)-> ft.ElevatedButton:
    """
    A button that will play the given SFX in the `SFX` Enum class.

    Args:
        audio (AudioManager): The `AudioManager` instance.
        page (Page): The `Page` instance; only provide if snackbar is `True`.
        sfx (SFX): The `SFX` to be played.
        overlap (bool): Whether the SFX can overlap.
        snackbar (bool): Whether to display a snackbar notif on what SFX is being played.
        callbacks (list): A list of callbacks that retuns `None` if you want to add more function calls.

    Returns:
        `ElevatedButton`: A premade button for playing a specific SFX.
    """
    def play_sfx(_):
        print(f"Playing {"overlapping SFX!" if overlap else "NOT overlapping SFX!"}")
        audio.play_sfx(sfx, overlap=overlap)
        
        if snackbar and page:
            page.open(simple_popup(f"Playing SFX: {sfx.value.title}"))
            page.update()
            
        if callbacks is None:
            return
        for cb in callbacks:
            cb(_)
        
    return preset_sound_btn(text=sfx.value.title, on_click=play_sfx, data=sfx, icon=ft.Icons.MUSIC_NOTE, disabled=disabled)

def music_btn(
    audio: AudioManager, music: Music, loop: bool = True,
    callbacks: list[Callable[[], None]] | None = None
)-> ft.ElevatedButton:
    """
    A button that will play the given music in the `Music` Enum class.

    Args:
        audio (AudioManager): The `AudioManager` instance.
        music (Music): The `Music` to be played.
        loop (bool): Whether the music will loop once finished playing.
        callbacks (list): A list of callbacks that retuns `None` if you want to add more function calls.

    Returns:
        `ElevatedButton`: A premade button for playing specific music.
    """
    def play_music(_):
        audio.play_music(music, loop=loop)
        
        if callbacks is None:
            return
        for cb in callbacks:
            cb(_)
    
    return preset_sound_btn(text=music.value.title, on_click=play_music, data=music, icon=ft.Icons.LIBRARY_MUSIC)