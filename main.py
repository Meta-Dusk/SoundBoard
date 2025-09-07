import flet as ft

from app.containers import default_row, default_column, default_container, true_center_container
from app.audio import AudioManager, Music, SFX
from app.buttons import square_button
from app.styles import mobile_view
from app.components import random_music_btn, random_sfx_btn, master_volume_slider
from enum import Enum


class DEFAULT(Enum):
    MEDIA_LABEL = "No Music Playing"
    MEDIA_DESC = "Play any music for it to display here."
    

def sample_btn(
    text: str = "Sample Button",
    on_click: ft.OptionalControlEventCallable = None
):
    return ft.ElevatedButton(
        text=text,
        on_click=on_click,
        adaptive=True, expand=True,
        width=50, height=50,
        icon=ft.Icons.STAY_CURRENT_LANDSCAPE
    )


def main(page: ft.Page):
    dev_mode: bool = True
    landscape: bool = False
    
    paused: bool = False
    
    def on_pause(_):
        nonlocal paused
        if paused:
            audio.resume_music()
            paused = False
            pause_btn.icon = ft.Icons.PLAY_ARROW
        else:
            audio.pause_music()
            paused = True
            pause_btn.icon = ft.Icons.PAUSE
        pause_btn.update()
        
    def on_stop(_):
        nonlocal paused
        if audio.music:
            paused = False
            pause_btn.icon = ft.Icons.PLAY_ARROW
            audio.stop_music()
            reset_values(_)
    
    mobile_view(page, landscape)
    audio = AudioManager(page)
        
    def enable_pause(_):
        nonlocal paused
        paused = False
        pause_btn.icon = ft.Icons.PLAY_ARROW
        pause_btn.disabled = False
        stop_btn.disabled = False
        media_label.value = audio.music.data.title
        media_desc.value = audio.music.data.description
        update_components(_)
    
    def update_components(_):
        pause_btn.update()
        stop_btn.update()
        media_label.update()
        media_desc.update()
    
    def reset_values(_):
        nonlocal paused
        paused = False
        pause_btn.icon = ft.Icons.PLAY_ARROW
        pause_btn.disabled = True
        stop_btn.disabled = True
        media_label.value = DEFAULT.MEDIA_LABEL.value
        media_desc.value = DEFAULT.MEDIA_DESC.value
        update_components(_)
        
    def on_resized(_):
        update_components(_)
        mv_slider.update()
    
    def change_orientation(_):
        nonlocal landscape
        landscape = not landscape
        mobile_view(page, landscape)
        mobile_dev_btn.text = "Enter Landscape Mode" if not landscape else "Enter Portrait Mode"
        mobile_dev_btn.icon = ft.Icons.STAY_CURRENT_LANDSCAPE if not landscape else ft.Icons.STAY_CURRENT_PORTRAIT
        page.update()
        mobile_dev_btn.update()
    
    page.on_resized = on_resized
        
    mobile_dev_btn = ft.ElevatedButton(
        text="Enter Landscape Mode",
        on_click=change_orientation,
        adaptive=True, expand=True,
        width=50, height=50,
        icon=ft.Icons.STAY_CURRENT_LANDSCAPE
    )
    pause_btn = ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=on_pause, disabled=True)
    stop_btn = ft.IconButton(icon=ft.Icons.STOP, on_click=on_stop, disabled=True)
    mv_slider = master_volume_slider(audio, page)
    
    media_label = ft.Text("No music playing", size=20, color=ft.Colors.PRIMARY)
    media_desc = ft.Text("Play any music for it to display here.", size=14, color=ft.Colors.SECONDARY)
    
    form: ft.Control
    form_controls = default_row([
        random_sfx_btn(audio, snackbar=True, page=page),
        random_music_btn(audio, callbacks=[enable_pause])
    ])
    volume_controls = default_column([
        ft.Text("Master Volume"),
        default_row([mv_slider])
    ], expand=False)
    media_controls = default_column([
        media_label,
        media_desc,
        default_row([pause_btn, stop_btn], expand=False)
    ])
    
    if (page.platform == ft.PagePlatform.WINDOWS and dev_mode):
        page.open(ft.SnackBar(ft.Text("Dev mode is currently on"), duration=2000))
        
        dev_buttons = ft.Container(default_row([mobile_dev_btn]))
        dev_form = default_column([
            dev_buttons,
            volume_controls,
            form_controls,
            media_controls
        ], expand=False)
        form = dev_form
    else:
        form = default_column([
            volume_controls,
            form_controls,
            media_controls
        ], expand=False)
    
    align_form = true_center_container(form)
    
    page.add(align_form)


if __name__ == "__main__":
    ft.app(main, assets_dir="assets")