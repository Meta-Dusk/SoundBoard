import flet as ft


def simple_popup(msg: str, duration_in_ms: int = 1000):
    """A basic `SnackBar` that only shows text. Works as a basic non-obtrusive notification."""
    return ft.SnackBar(ft.Text(msg), duration=duration_in_ms)

def notif_dialog(title: str = "Top Text", content: str = "Bottom Text"):
    """A basic `AlertDialog` that works as a high-level notification."""
    return ft.AlertDialog(
        title=title, content=ft.Text(content, text_align=ft.TextAlign.CENTER), title_padding=ft.padding.all(25),
        alignment=ft.alignment.center, icon=ft.Icon(ft.Icons.NOTIFICATIONS, size=40)
    )