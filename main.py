import flet as ft

from app.containers import default_row, default_column
from app.audio import AudioManager
from app.styles import mobile_view, mobile_appbar
from app.components import random_music_btn, random_sfx_btn, master_volume_slider, audio_duration_slider, audio_balance_slider
from app.utilities import generate_non_explicits, get_storage, set_storage
from enum import Enum


class DEFAULTS(str, Enum):
    MEDIA_LABEL = "No Music Playing"
    MEDIA_DESC = "Play any music for it to display here."
    MEDIA_SEEK = "0:00/0:00"
    EXPLICIT_OFF = "Disable Explicit Content"
    EXPLICIT_ON = "Enable Explicit Content"
    SAFE = True


def main(page: ft.Page):
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
    mobile_appbar(page)
    audio = AudioManager(page)
    # audio.debug = False
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
        page.update()
        mobile_dev_btn.icon = ft.Icons.STAY_CURRENT_LANDSCAPE if not landscape else ft.Icons.STAY_CURRENT_PORTRAIT
        mobile_dev_btn.update()
        page.appbar.update()
    
    def toggle_explicit_content(e: ft.ControlEvent):
        safe: bool = get_storage(DEFAULTS.SAFE, page)
        safe = not safe
        print(f"Toggled explicit content to {not safe}")
        
        popup_menu_item: ft.PopupMenuItem = e.control
        popup_menu_item.text = DEFAULTS.EXPLICIT_OFF.value if not safe else DEFAULTS.EXPLICIT_ON.value
        popup_menu_item.badge = None
        # popup_menu_item.update()
        page.open(ft.SnackBar(ft.Text(f"Explicit content is now {"disabled" if safe else "enabled"}"), duration=1500))
        page.update()
        
        set_storage(DEFAULTS.SAFE, safe, page)
    
    def toggle_overlap_sfx(e: ft.ControlEvent):
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = not toggle_item.checked
        print(f"Overlapping SFX is now {toggle_item.checked}")
        # toggle_item.update()
        # page.update()
    
    page.on_resized = on_resized
    page.auto_scroll = True
    
    media_label = ft.Text(DEFAULTS.MEDIA_LABEL.value, size=20, color=ft.Colors.PRIMARY)
    media_desc = ft.Text(DEFAULTS.MEDIA_DESC.value, size=14, color=ft.Colors.SECONDARY)
    media_seek = ft.Text(DEFAULTS.MEDIA_SEEK.value, size=16, color=ft.Colors.SECONDARY, offset=ft.Offset(0, -0.1))
    
    mobile_dev_btn = ft.IconButton(
        on_click=change_orientation,
        adaptive=True,
        icon=ft.Icons.STAY_CURRENT_LANDSCAPE
    )
    pause_btn = ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=on_pause, disabled=True)
    stop_btn = ft.IconButton(icon=ft.Icons.STOP, on_click=on_stop, disabled=True)
    
    mv_slider = master_volume_slider(audio, page)
    audio_slider = audio_duration_slider(audio, media_seek)
    audio_slider.padding = 5
    b_slider = audio_balance_slider(audio, page)
    
    overlap_sfx_menu_item = ft.PopupMenuItem(
        text="Overlapping SFX", icon=ft.Icons.SPEAKER_GROUP, checked=True,
        on_click=toggle_overlap_sfx
    )
    
    form = ft.Container(expand=True)
    form_controls = ft.Column([
        random_sfx_btn(audio, snackbar=True, page=page, alt_sfx=safe_sfx, overlap=overlap_sfx_menu_item.checked),
        random_music_btn(audio, callbacks=[music_btn_pressed], alt_music=safe_music, page=page)
    ], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    volume_controls = default_column([
        default_row([ft.Text("Master Volume"), mv_slider]),
        default_row([ft.Text("Audio Balance"), b_slider])
    ], expand=False)
    
    media_btns = ft.Container(ft.Row([pause_btn, stop_btn], tight=True, spacing=0), padding=0, margin=0, expand=False)
    media_controls = ft.Container(default_column([
        media_label,
        media_desc,
        ft.Row([media_seek, audio_slider, media_btns])
    ], expand=False))
    
    settings_menu_button = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                text=DEFAULTS.EXPLICIT_OFF.value if not get_storage(DEFAULTS.SAFE, page) else DEFAULTS.EXPLICIT_ON.value,
                on_click=toggle_explicit_content, icon=ft.Icons.MODE
            ),
            overlap_sfx_menu_item
        ]
    )
    
    if (page.platform == ft.PagePlatform.WINDOWS):
        page.appbar.actions.insert(0, mobile_dev_btn)
        page.appbar.actions.insert(1, settings_menu_button)

    form.content = default_column([
        volume_controls,
        ft.Divider(),
        form_controls,
        ft.Divider(),
        media_controls
    ])
    
    draggable_form = ft.Container(ft.WindowDragArea(form, maximizable=False), expand=True)
    
    page.add(draggable_form)


if __name__ == "__main__":
    ft.app(main, assets_dir="assets")