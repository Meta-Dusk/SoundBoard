import flet as ft


def simple_popup(msg: str, duration_in_ms: int = 1000):
    return ft.SnackBar(ft.Text(msg), duration=duration_in_ms)