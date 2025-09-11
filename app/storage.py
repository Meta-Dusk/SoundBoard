import flet as ft

from enum import Enum
from typing import Any
from .utilities import default_prefixes, is_empty


# Windows Path: C:\Users\MY_PC\AppData\Roaming\Appveyor Systems Inc\Flet
class Storage:
    """
    The `Storage` handles local data in the `shared_preferences` module.
    The saved data are platform-dependent.
    When making an instance of this, refer to the Args below:
    
    Args:
        page (Page): The `Page` instance.
        debug (bool): Set to `True` to receive debug messages.
    """
    def __init__(self, page: ft.Page, debug: bool = True):
        self.page = page
        self.debug = debug
        
    
    def _debug_msg(self, msg: str) -> None:
        if self.debug:
            print(msg)
        
    def get(self, key: Enum | str) -> (Any | None):
        """
        Get a value from local storage `client_storage` dictionary.
        
        Args:
            key (Enum | str): Takes an `Enum` class, which should be structure the same as a dictionary, but can take a string for manual checking.
        
        Returns:
            (Any | None): Will only return a value if it exists; otherwise, it will create a new entry.
        """
        debug_name = "[Storage.get]"
        if isinstance(key, str):
            return self.page.client_storage.get(default_prefixes(key))
            
        key_str = default_prefixes(key.name)
        if self.page.client_storage.contains_key(key_str):
            return self.page.client_storage.get(key_str)
        else:
            self._debug_msg(f"{debug_name} Missing entry, attempting to make a new one for: {key.name} with value of {key.value}")
            if self.set(key, key.value):
                self._debug_msg(f"{debug_name} Entry created.")
                return self.get(key)
            else:
                return None

    def set(self, key: Enum | str, value: any) -> bool:
        """
        Set a key and value pair to the local storage `client_storage` dictionary.
        
        Args:
            key (str): The key "name" of an entry
            value (Any): A value to be assigned to the key
        
        Returns:
            bool: `True` if setting the key and value pair was successful.
        """
        debug_name = "[Storage.set]"
        if is_empty(key):
            self._debug_msg(f"{debug_name} Key can't be None or empty. Received key: {key} and value: {value}")
            return False
        if isinstance(key, Enum):
            key = key.name
        if self.page.client_storage.set(default_prefixes(key), value):
            self._debug_msg(f"{debug_name} Setting dict: {key}: {value}")
            return True
        else:
            self._debug_msg(f"{debug_name} Something went wrong setting dict: {key}: {value}")
            return False
        
    def check(self, key: Enum | str) -> bool:
        """
        Checks if an entry exists in the local storage `client_storage` dictionary.
        
        Args:
            key (Enum | str): The key "name" of an entry
        
        Returns:
            bool: `True` if key exists.
        """
        debug_name = "[Storage.check]"
        if is_empty(key):
            self._debug_msg(f"{debug_name} Key \'{key}\' can't be None or empty")
            return False
        if isinstance(key, Enum):
            key = key.name
        if self.page.client_storage.contains_key(default_prefixes(key)):
            self._debug_msg(f"{debug_name} Found {key} in storage.")
            return True
        else:
            self._debug_msg(f"{debug_name} Key \'{key}\' is not in storage.")
            return False

    def remove(self, key: Enum | str) -> bool:
        """
        Removes an entry exists in the local storage `client_storage` dictionary.
        
        Args:
            key (Enum | str): The key "name" of an entry
        
        Returns:
            bool: `True` if removal success.
        """
        debug_name = "[Storage.remove]"
        if is_empty(key):
            self._debug_msg(f"{debug_name} Key can't be None or empty")
            return False
        if isinstance(key, Enum):
            key = key.name
        if self.page.client_storage.remove(default_prefixes(key)):
            self._debug_msg(f"{debug_name} Key \'{key}\' successfully removed.")
            return True
        else:
            self._debug_msg(f"{debug_name} Something went wrong trying to remove \'{key}\'")
            return False


"""
Run this with:
py -m app.storage
"""
def test(page: ft.Page):
    page.title = "app.storage test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.center()
    
    storage = Storage(page)
    
    def on_set_storage(_):
        key = user_input_key.value
        value = user_input_value.value
        if storage.set(key, value):
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
        value = storage.get(key)
        if value is not None:
            info_text.value = f"Key \'{key}\' contains: {value}"
            user_input_key.error_text = ""
            user_input_value.value = value
            user_input_value.update()
        else:
            info_text.value = "Couldn't get an unknown key"
            user_input_key.error_text = "Unknown Key"
        user_input_key.update()
        info_text.update()
        
    def on_check_storage(_):
        key = user_input_key.value
        if storage.check(key):
            info_text.value = f"{key} exists."
        else:
            info_text.value = f"Key \'{key}\' unknown"
        user_input_key.update()
        info_text.update()
        
    def on_remove_storage(_):
        key = user_input_key.value
        if storage.remove(key):
            info_text.value = f"Removal of {key} success."
            user_input_key.value = ""
        else:
            info_text.value = f"Key \'{key}\' unknown"
        user_input_key.update()
        info_text.update()
    
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
        ft.Divider(),
        info_text,
        input_row,
        button_row
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    page.add(form)
    

if __name__ == "__main__":
    ft.app(target=test)