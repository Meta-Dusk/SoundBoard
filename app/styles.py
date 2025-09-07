import flet as ft


def base_page(page: ft.Page):
    page.title = "SeBoard"
    page.adaptive = True
    page.window.center()

def mobile_view(page: ft.Page, landscape: bool = False):
    base_page(page)
    if landscape:
        page.window.width = 844
        page.window.height = 390
    else:    
        page.window.width = 390
        page.window.height = 844
        
    page.window.resizable = False
    page.window.maximizable = False