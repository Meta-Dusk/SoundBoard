import flet as ft

from app.containers import default_row, default_column, default_container, true_center_container
from app.audio import AudioManager, Music, SFX
from app.buttons import square_button
from app.styles import mobile_view
from app.components import random_music_btn, random_sfx_btn


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
    dev_mode: bool = True
    landscape: bool = False
    
    mobile_view(page, landscape)
    audio = AudioManager(page)
    
    def rotate_phone(e):
        nonlocal landscape
        
        landscape = not landscape
        mobile_view(page, landscape)
        page.update()
        
    mobile_dev_btn = sample_btn("Rotate Phone", rotate_phone)
    
    form: ft.Control
    form_controls = default_row([
        random_sfx_btn(audio), random_music_btn(audio)
    ])
    
    if (page.platform == ft.PagePlatform.WINDOWS and dev_mode):
        dev_buttons = ft.Container(default_row([
            mobile_dev_btn
        ]))
        dev_form = default_column([
            dev_buttons,
            form_controls
        ])
        form = dev_form
    else:
        form = form_controls
    
    align_form = true_center_container(form)
    
    page.add(align_form)


if __name__ == "__main__":
    ft.app(main, assets_dir="assets")