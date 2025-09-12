import flet as ft
from app.main_app import AudioApp


def main_app(page: ft.Page):
    app = AudioApp(page)
    app.load_app()

if __name__ == "__main__":
    ft.app(main_app, assets_dir="assets")