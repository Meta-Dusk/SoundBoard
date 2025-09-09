import flet as ft

from typing import Sequence


def default_column(controls: Sequence[ft.Control], expand: bool | int = True):
    return ft.Column(
        controls=controls,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=expand, adaptive=True
    )
    
def default_row(controls: Sequence[ft.Control], expand: bool | int = True):
    return ft.Row(
        controls=controls,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=expand, adaptive=True
    )
    
def default_container(content: ft.Control):
    return ft.Container(
        content=content,
        alignment=ft.alignment.center,
        expand=True, adaptive=True
    )
    
def true_center_container(content: ft.Control):
    return default_row([default_column([default_container(content)])])

def expand_x_y(controls: Sequence[ft.Control]):
    return default_row([default_column([controls])])