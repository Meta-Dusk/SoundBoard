import flet as ft
import flet_audio as fa

from app.containers import true_center_container, default_column


def main(page: ft.Page):
    audio_test = fa.Audio(src="assets/sfx/fn.mp3")
    
    test_txt = ft.Text("This is an app with background audio.")
    test_btn = ft.ElevatedButton("Play SFX", on_click=lambda _: audio_test.play())
    
    form = true_center_container(default_column([
        test_txt,
        test_btn
    ]))
    
    page.overlay.append(audio_test)
    page.add(form)

ft.app(main)