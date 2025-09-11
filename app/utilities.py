import flet as ft

from pathlib import Path
from typing import Tuple, List
from enum import Enum
from .file_declarations import Sound, SFX, Music


class PREFIXES(Enum):
    SIGNATURE = "MetaDusk"
    APP_NAME = "SeBored"
    

def default_prefixes(key: str, debug: bool = True) -> str:
    """Simply returns a string prefixed with the default prefixes."""
    value = f"{PREFIXES.SIGNATURE.value}.{PREFIXES.APP_NAME.value}.{key}"
    if debug:
        print(f"Modifying entry: {value}")
    return value

def is_empty(var: str | Enum, debug: bool = False) -> bool:
    """Checks if input is an empty string which then returns `True`, set debug to `True` for debug messages."""
    def debug_msg(msg: str):
        if debug:
            print(msg)
            
    if isinstance(var, Enum):
        debug_msg(f"Received: {var} which is an Enum")
        return False
    if var is None or var.strip() == "":
        debug_msg(f"Received: {var} which is empty")
        return True
    debug_msg(f"Received: {var} which is not empty")
    return False

def format_ms(ms: int | float) -> str:
    """Converts the input of `milliseconds` into \"`minutes`:`seconds`\""""
    total_seconds = int(ms) // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def generate_non_explicits() -> Tuple[List[Sound], List[Sound]]:
    """
    Generates lists of `Audio` excluding those tagged as `explicit=`True`.`
    
    Returns:
        Tuple: A tuple of lists, containing `Sound`, two of which are `safe_sfx` and `safe_music`.
    """
    safe_sfx = []
    safe_music = []
    
    print("Generating safe_sfx")
    for sfx in SFX:
        if (not sfx.value.explicit):
            safe_sfx.append(sfx)
    print(f"Finished generation. Original size: {len(SFX)} -> New size: {len(safe_sfx)}\n")
    
    print("Generating safe_music")
    for music in Music:
        if (not music.value.explicit):
            safe_music.append(music)
    print(f"Finished generation. Original size: {len(Music)} -> New size: {len(safe_music)}\n")
    
    return safe_sfx, safe_music


def check_audio():
    """Checks integrity of all audio files."""
    sfx_count = 0
    music_count = 0

    print("\nChecking registered SFX...")
    for sfx in SFX:
        if Path(sfx.value.str_path).exists():
            print(f"{sfx.name}: {sfx.value.str_path}")
            sfx_count += 1
        else:
            print(f"SFX {sfx.name} does not exist at {sfx.value.str_path}!")
    print(f"Found {sfx_count}/{len(SFX)} SFX files\n")

    print("\nChecking registered Music...")
    for music in Music:
        if Path(music.value.str_path).exists():
            print(f"{music.name}: {music.value.str_path}")
            music_count += 1
        else:
            print(f"Music {music.name} does not exist at {music.value.str_path}!")
    print(f"Found {music_count}/{len(Music)} Music files\n")

    if sfx_count == len(SFX) and music_count == len(Music):
        print("[AudioManager] ✅ All sound files are fully registered!\n")
    else:
        print("[AudioManager] ⚠️ Some files are missing.\n")


"""
Run this with:
py -m app.utilities
"""
import random

def test(page: ft.Page):
    page.title = "app.utilities test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.center()
    
    ms = random.randint(1, 100000)
    
    def on_randomize(_):
        ms = random.randint(1, 100000)
        test_text.value = f"{ms}ms -> {format_ms(ms)}"
        test_text.update()
    
    test_text = ft.Text(f"{ms}ms -> {format_ms(ms)}")

    form = ft.Column([
        ft.Text("Testing utilities..."),
        test_text,
        ft.ElevatedButton("Randomize", on_click=on_randomize),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    page.add(form)
    

if __name__ == "__main__":
    ft.app(target=test)