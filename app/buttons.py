import flet as ft


def square_button(
    text: str = "Square Button",
    on_click: ft.OptionalControlEventCallable = None,
    expand: bool = False
):
    return ft.ElevatedButton(
        text=text,
        width=100, height=100,
        adaptive=True, expand=expand,
        on_click=on_click,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
    )