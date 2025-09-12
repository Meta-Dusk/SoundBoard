import flet as ft
from app.main_app import AudioApp


def main(page: ft.Page):
    app = AudioApp(page)
    app.load_app()

if __name__ == "__main__":
    ft.app(main, assets_dir="assets")