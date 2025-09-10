import random
import flet as ft

from typing import Tuple, List, Any
from enum import Enum
from .file_declarations import Sound, SFX, Music


class PREFIXES(Enum):
    SIGNATURE = "MetaDusk"
    APP_NAME = "SeBored"
    

def default_prefixes(key: str) -> str:
    value = f"{PREFIXES.SIGNATURE.value}.{PREFIXES.APP_NAME.value}.{key}"
    print(f"Modifying entry: {value}")
    return value

def str_empty(var: str | Enum) -> bool:
    if isinstance(var, Enum):
        return False
    if var is None or var.strip() == "":
        return False
    return True

def format_ms(ms: int | float) -> str:
    """Converts the input of `milliseconds` into \"`minutes`:`seconds`\""""
    total_seconds = int(ms) // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def generate_non_explicits() -> Tuple[List[Sound], List[Sound]]:
    """
    Generates lists of `Audio` excluding those tagged as `explicit=True`
    Returns:
        Tuple: A tuple of lists, containing `Sound`, two of which are `safe_sfx` and `safe_music`
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


#----------- STORAGE -----------
# Path: C:\Users\MY_PC\AppData\Roaming\Appveyor Systems Inc\Flet
# TODO: Make a storage class to transfer all these storage methods, so that the page variable doesn't need to be repeatedly called.
def get_storage(key: Enum | str, page: ft.Page) -> (Any | None):
    """
    Get a value from local storage `client_storage` dictionary.
    
    Args:
        key (Enum | str): Takes an `Enum` class, which should be structure the same as a dictionary, but can take a string for manual checking
        page (Page): The `Page` instance
    
    Returns:
        (Any | None): Will only return a value if it exists; otherwise, it will create a new entry
    """
    if isinstance(key, str):
        return page.client_storage.get(default_prefixes(key))
        
    key_str = default_prefixes(key.name)
    if page.client_storage.contains_key(key_str):
        return page.client_storage.get(key_str)
    else:
        print(f"[get_storage] Missing entry, attempting to make a new one for: {key.name} with value of {key.value}")
        if set_storage(key, key.value, page):
            print("[get_storage] Entry created.")
            return get_storage(key, page)
        else:
            return None

def set_storage(key: Enum | str, value: any, page: ft.Page) -> bool:
    """
    Set a key and value pair to the local storage `client_storage` dictionary.
    
    Args:
        key (str): The key "name" of an entry
        value (Any): A value to be assigned to the key
        page (Page): The `Page` instance
    
    Returns:
        bool: `True` if setting the key and value pair was successful.
    """
    if str_empty(key):
        print(f"[set_storage] Key can't be None or empty. Received key: {key} and value: {value}")
        return False
    if isinstance(key, Enum):
        key = key.name
    if page.client_storage.set(default_prefixes(key), value):
        print(f"Setting dict: {key}: {value}")
        return True
    else:
        print(f"Something went wrong setting dict: {key}: {value}")
        return False
    
def check_storage(key: Enum | str, page: ft.Page) -> bool:
    """
    Checks if an entry exists in the local storage `client_storage` dictionary.
    
    Args:
        key (Enum | str): The key "name" of an entry
        page (Page): The `Page` instance
    
    Returns:
        bool: `True` if key exists.
    """
    if str_empty(key):
        print("[check_storage] Key can't be None or empty")
        return False
    if isinstance(key, Enum):
        key = key.name
    if get_storage(key, page) is not None or "":
        return True
    else:
        return False

def remove_storage(key: Enum | str, page: ft.Page) -> bool:
    """
    Removes an entry exists in the local storage `client_storage` dictionary.
    
    Args:
        key (Enum | str): The key "name" of an entry
        page (Page): The `Page` instance
    
    Returns:
        bool: `True` if removal success.
    """
    if str_empty(key):
        print("[remove_storage] Key can't be None or empty")
        return False
    if isinstance(key, Enum):
        key = key.name
    if page.client_storage.remove(default_prefixes(key)):
        return True
    else:
        return False

"""
Run this with:
py -m app.utilities
"""

def test(page: ft.Page):
    page.title = "app.utilities test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.center()
    
    ms = random.randint(1, 100000)
    
    def on_set_storage(_):
        key = user_input_key.value
        value = user_input_value.value
        if set_storage(key, value, page) or not (str_empty(key) or str_empty(value)):
            user_input_key.error_text = ""
            user_input_value.error_text = ""
            user_input_key.value = None
        else:
            user_input_key.error_text = "Key Error"
            user_input_value.error_text = "Value Error"
        user_input_key.update()
        user_input_value.update()
    
    def on_get_storage(_):
        key = user_input_key.value
        value = get_storage(key, page)
        print(f"get_storage = {value}")
        if value is not None:
            info_text.value = f"{key} has {value}"
            user_input_key.error_text = ""
        else:
            info_text.value = "Unknown"
            user_input_key.error_text = "Unknown Key"
        user_input_key.update()
        info_text.update()
        
    def on_check_storage(_):
        key = user_input_key.value
        if check_storage(key, page):
            info_text.value = f"{key} exists."
        else:
            info_text.value = f"Key \'{key}\' unknown"
        user_input_key.update()
        info_text.update()
        
    def on_remove_storage(_):
        key = user_input_key.value
        if remove_storage(key, page):
            info_text.value = f"Removal of {key} success."
            user_input_key.value = ""
        else:
            info_text.value = f"Key \'{key}\' unknown"
        user_input_key.update()
        info_text.update()
    
    def on_randomize(_):
        ms = random.randint(1, 100000)
        test_text.value = f"{ms}ms -> {format_ms(ms)}"
        test_text.update()
    
    test_text = ft.Text(f"{ms}ms -> {format_ms(ms)}")
    
    user_input_key = ft.TextField(hint_text="Enter Key Here")
    user_input_value = ft.TextField(hint_text="Enter Value Here")
    input_row = ft.Row([user_input_key, user_input_value], alignment=ft.MainAxisAlignment.CENTER)
    info_text = ft.Text("Information will go here")
    
    button_row = ft.Row([
        ft.ElevatedButton("Set Storage", on_click=on_set_storage),
        ft.ElevatedButton("Check Storage", on_click=on_check_storage),
        ft.ElevatedButton("Get Storage", on_click=on_get_storage),
        ft.ElevatedButton("Remove Storage", on_click=on_remove_storage)
    ], alignment=ft.MainAxisAlignment.CENTER)
    form = ft.Column([
        ft.Text("Testing utilities..."),
        test_text,
        ft.ElevatedButton("Randomize", on_click=on_randomize),
        ft.Divider(),
        info_text,
        input_row,
        button_row
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    page.add(form)
    

if __name__ == "__main__":
    ft.app(target=test)