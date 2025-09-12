import flet as ft

from enum import Enum


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