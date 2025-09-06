import flet as ft
import random

from app.containers import default_row, default_column
from app.audio import AudioManager, Music, SFX
from app.buttons import square_button


def sample_btn(
    text: str = "Sample Button",
    on_click: ft.OptionalControlEventCallable = None
):
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        adaptive=True, expand=True,
        width=50, height=50
    )

def main(page: ft.Page):
    audio = AudioManager(page)
    
    def play_random_sfx(e):
        audio.play_sfx(random.choice(list(SFX)))
        
    test_btn = sample_btn("Play random SFX", play_random_sfx)
    
    form = [test_btn, test_btn, test_btn]
    
    align_form = default_column([default_row(form)])
    
    page.add(align_form)


if __name__ == "__main__":
    ft.app(main, assets_dir="assets")