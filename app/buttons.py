import flet as ft


def square_button(
    text: str = "Square Button", expand: bool = False,
    on_click: ft.OptionalControlEventCallable = None
):
    return ft.ElevatedButton(
        text=text,
        width=100, height=100,
        adaptive=True, expand=expand,
        on_click=on_click,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )
    
def toggle_button_classic(
    text: str = "Toggle Button", expand: bool = False,
    on_click: ft.OptionalControlEventCallable = None
) -> ft.TextButton:
    
    text_btn = ft.TextButton(
        text=text, expand=expand, on_click=on_click
    )
    return text_btn

def preset_sound_btn(
    text: str = "Sound Text", expand: bool = True, height: ft.OptionalNumber = 50,
    on_click: ft.OptionalEventCallable = None, col: ft.ResponsiveNumber = {"xs":12,"md":6,"lg":3},
    data: any = None, icon: ft.IconValue = None
) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        text=text, expand=expand, height=height, on_click=on_click, col=col, data=data, icon=icon
    )