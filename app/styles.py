import flet as ft

from .file_declarations import Images


def base_page(page: ft.Page) -> None:
    page.title = "SeBored"
    page.adaptive = True
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.center()

def mobile_view(page: ft.Page, landscape: bool = False) -> None:
    base_page(page)
    if landscape:
        page.window.width = 844
        page.window.height = 390
    else:    
        page.window.width = 390
        page.window.height = 844
        
    page.window.resizable = False
    page.window.maximizable = False
    page.window.frameless = True

def preset_appbar(page: ft.Page) -> None:
    leading_control = ft.Image(
        src=Images.SEB.value.str_path, fit=ft.ImageFit.COVER,
        border_radius=ft.border_radius.all(50), expand=True,
        filter_quality=ft.FilterQuality.LOW
    )
    page.appbar = ft.AppBar(
        leading=ft.WindowDragArea(leading_control, maximizable=False),
        leading_width=40, toolbar_height=40,
        title=ft.WindowDragArea(ft.Text("SeBored", style=ft.TextStyle(size=20, letter_spacing=3)), maximizable=False),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )
    
def mobile_appbar(page: ft.Page) -> None:
    preset_appbar(page)
    page.appbar.actions = [
        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=20, on_click=lambda _: page.window.close())
    ]
    
    
"""
Run this file to test some style functions. Run with:
py -m app.styles
"""
def test(page: ft.Page):
    base_page(page)
    
    form = [ft.Text("This should center everything!")]
    for i in range(50):
        form.append(ft.Text(f"I am text! ID:{i}"))
    
    column = ft.Column(
        controls=form, expand=True, scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.START
    )
    columns = []
    for i in range(3):
        columns.append(ft.Container(content=column, expand=i))
        
    controls = ft.Row(expand=3, controls=columns)
    
    page.add(controls)
    
if __name__ == "__main__":
    ft.app(test)