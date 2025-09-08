import flet as ft

from app.containers import default_row, default_column, true_center_container
from app.audio import AudioManager
from app.styles import mobile_view
from app.components import random_music_btn, random_sfx_btn, master_volume_slider, audio_duration_slider, audio_balance_slider
from app.utilities import generate_non_explicits
from app.buttons import toggle_button_classic
from enum import Enum


class DEFAULTS(str, Enum):
    MEDIA_LABEL = "No Music Playing"
    MEDIA_DESC = "Play any music for it to display here."
    MEDIA_SEEK = "0:00/0:00"
    EXPLICIT_OFF = "Disable Explicit Content"
    EXPLICIT_ON = "Enable Explicit Content"


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
            reset_components()
    
    mobile_view(page, landscape)
    audio = AudioManager(page)
    # audio.debug = False
    safe: bool = audio.settings["SAFE"]
    safe_sfx, safe_music = generate_non_explicits()
        
    def music_btn_pressed(_):
        nonlocal paused
        paused = False
        pause_btn.icon = ft.Icons.PLAY_ARROW
        pause_btn.disabled = False
        stop_btn.disabled = False
        media_label.value = audio.music.data.title
        media_desc.value = audio.music.data.description
        audio_slider.disabled = False
        update_components()
    
    def update_components():
        pause_btn.update()
        stop_btn.update()
        media_label.update()
        media_desc.update()
        media_seek.update()
        audio_slider.update()
    
    def reset_components():
        nonlocal paused
        paused = False
        pause_btn.icon = ft.Icons.PLAY_ARROW
        pause_btn.disabled = True
        stop_btn.disabled = True
        media_label.value = DEFAULTS.MEDIA_LABEL.value
        media_desc.value = DEFAULTS.MEDIA_DESC.value
        media_seek.value = DEFAULTS.MEDIA_SEEK.value
        audio_slider.disabled = True
        audio_slider.value = 0
        update_components()
        
    def on_resized(_):
        update_components()
        mv_slider.update()
    
    def change_orientation(_):
        nonlocal landscape
        landscape = not landscape
        mobile_view(page, landscape)
        mobile_dev_btn.text = "Enter Landscape Mode" if not landscape else "Enter Portrait Mode"
        mobile_dev_btn.icon = ft.Icons.STAY_CURRENT_LANDSCAPE if not landscape else ft.Icons.STAY_CURRENT_PORTRAIT
        page.update()
        mobile_dev_btn.update()
    
    def toggle_explicit_content(_):
        audio.settings["SAFE"] = not audio.settings["SAFE"]
        safe: bool = audio.settings["SAFE"]
        print(f"Toggled explicit content to {safe}")
        
        explicit_toggle_btn.text = DEFAULTS.EXPLICIT_OFF.value if not safe else DEFAULTS.EXPLICIT_ON.value
            
        audio._save_settings()
        explicit_toggle_btn.update()
    
    page.on_resized = on_resized
    page.auto_scroll = True
    
    media_label = ft.Text(DEFAULTS.MEDIA_LABEL.value, size=20, color=ft.Colors.PRIMARY)
    media_desc = ft.Text(DEFAULTS.MEDIA_DESC.value, size=14, color=ft.Colors.SECONDARY)
    media_seek = ft.Text(DEFAULTS.MEDIA_SEEK.value, size=16, color=ft.Colors.SECONDARY)
    
    mobile_dev_btn = ft.ElevatedButton(
        text="Enter Landscape Mode",
        on_click=change_orientation,
        adaptive=True, expand=True, width=50,
        icon=ft.Icons.STAY_CURRENT_LANDSCAPE
    )
    pause_btn = ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=on_pause, disabled=True)
    stop_btn = ft.IconButton(icon=ft.Icons.STOP, on_click=on_stop, disabled=True)
    explicit_toggle_btn_text = DEFAULTS.EXPLICIT_OFF.value if not safe else DEFAULTS.EXPLICIT_ON.value
    explicit_toggle_btn = toggle_button_classic(explicit_toggle_btn_text, on_click=toggle_explicit_content)
    
    mv_slider = master_volume_slider(audio, page)
    audio_slider = audio_duration_slider(audio, media_seek)
    b_slider = audio_balance_slider(audio)
    
    form: ft.Control
    form_controls = default_row([
        random_sfx_btn(audio, snackbar=True, page=page, alt_sfx=safe_sfx),
        random_music_btn(audio, callbacks=[music_btn_pressed], alt_music=safe_music)
    ])
    volume_controls = default_column([
        ft.Text("Master Volume"),
        default_row([mv_slider]),
        ft.Text("Audio Balance"),
        default_row([b_slider])
    ], expand=False)
    
    media_btns = ft.Container(default_row([pause_btn, stop_btn]))
    media_controls = ft.Container(default_column([
        media_label,
        media_desc,
        media_seek,
        default_row([audio_slider, media_btns])
    ]))
    
    if (page.platform == ft.PagePlatform.WINDOWS and dev_mode): # Dev mode for Windows
        page.open(ft.SnackBar(ft.Text("Dev mode is currently on"), duration=2000))
        
        dev_buttons = ft.Container(default_row([mobile_dev_btn]))
        dev_form = default_column([
            dev_buttons,
            ft.Divider(),
            volume_controls,
            explicit_toggle_btn,
            ft.Divider(),
            form_controls,
            ft.Divider(),
            media_controls
        ], expand=False)
        form = dev_form
    else: # Default look for all platforms
        form = default_column([
            volume_controls,
            explicit_toggle_btn,
            ft.Divider(),
            form_controls,
            ft.Divider(),
            media_controls
        ], expand=False)
    
    align_form = true_center_container(form)
    
    page.add(align_form)


if __name__ == "__main__":
    ft.app(main, assets_dir="assets")