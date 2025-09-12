import flet as ft

from app.containers import default_row, default_column
from app.audio import AudioManager
from app.styles import mobile_view, mobile_appbar, base_page
from app.components import (
    random_music_btn, random_sfx_btn, master_volume_slider, audio_duration_slider, audio_balance_slider,
    sfx_btn, music_btn)
from app.storage import Storage
from app.file_declarations import Sound, SFX, Music
from app.popups import notif_dialog
from enum import Enum


class DEFAULTS(Enum):
    MEDIA_LABEL = "No Music Playing"
    MEDIA_DESC = "Play any music for it to display here."
    MEDIA_SEEK = "0:00/0:00"


def main(page: ft.Page):
    # Setup - Temp Variables
    landscape: bool = False
    paused: bool = False
    safe: bool = True
    overlap_sfx: bool = True
    show_audio_settings: bool = True
    
    # Setup - Instances
    audio = AudioManager(page)
    storage = Storage(page)
    # audio.debug = False
    # storage.debug = False
    if page.platform == ft.PagePlatform.WINDOWS:
        mobile_view(page, landscape, storage)
    else:
        base_page(page, storage=storage)
    mobile_appbar(page, storage=storage)
    
    # Audio Setups
    safe_sfx, safe_music = audio.generate_non_explicits()
    audio.validate()
    
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
        
    def music_btn_pressed(_):
        nonlocal paused
        
        paused = False
        pause_btn.icon = ft.Icons.PLAY_ARROW
        pause_btn.disabled = False
        stop_btn.disabled = False
        
        music: Sound = audio.music.data
        media_label.value = music.title
        media_desc.value = music.description
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
        print(f"Changing page orientation to {"landscape" if landscape else "portrait"}")
        mobile_view(page, landscape)
        mobile_dev_btn.icon = ft.Icons.STAY_CURRENT_LANDSCAPE if not landscape else ft.Icons.STAY_CURRENT_PORTRAIT
        page.update()
    
    def toggle_explicit_content(e: ft.ControlEvent):
        nonlocal safe, button_controls
        
        safe = not safe
        msg = f"Explicit content is now {"disabled" if safe else "enabled"}"
        popup_menu_item: ft.PopupMenuItem = e.control
        popup_menu_item.text = explicit_content_label
        
        for ctrl in button_controls.controls:
            ctrl: ft.ElevatedButton
            data: SFX | Music = ctrl.data
            print(f"Sound Button Data: {data}")
            
            if isinstance(data, (SFX, Music)) and data.value.explicit:
                ctrl.disabled = safe
        
        print(msg)
        page.open(notif_dialog(title="Explicit Content", content=msg))
        page.update()
    
    def toggle_overlap_sfx(e: ft.ControlEvent):
        nonlocal overlap_sfx
        
        overlap_sfx = not overlap_sfx
        msg = f"Overlapping SFX is now {overlap_sfx}"
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = overlap_sfx
        
        print(msg)
        page.open(notif_dialog(title="Overlapping SFX", content=msg))
        page.update()
    
    def toggle_audio_settings(e: ft.ControlEvent):
        nonlocal show_audio_settings
        
        show_audio_settings = not show_audio_settings
        msg = f"Now {"showing" if show_audio_settings else "hiding"} the Audio Settings."
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = show_audio_settings
        audio_settings_expansion.visible = show_audio_settings
        
        print(msg)
        page.open(notif_dialog(title="Audio Settings", content=msg))
        page.update()
    
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
    rnd_sfx_btn = random_sfx_btn(audio, page, safe, snackbar=True, alt_sfx=safe_sfx, overlap=overlap_sfx)
    rnd_music_btn = random_music_btn(audio, page, safe, callbacks=[music_btn_pressed], alt_music=safe_music)
    
    mv_slider = master_volume_slider(audio, page, storage)
    mv_slider.padding = 5
    b_slider = audio_balance_slider(audio, storage)
    b_slider.padding = 5
    audio_slider = audio_duration_slider(audio, media_seek)
    audio_slider.padding = 5
    
    button_controls = ft.ResponsiveRow(
        controls=[rnd_sfx_btn, rnd_music_btn], expand=True,
        alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    for sfx in SFX:
        temp_btn = sfx_btn(audio, page, sfx, overlap_sfx, snackbar=True)
        if sfx.value.explicit:
            temp_btn.disabled = safe
        button_controls.controls.append(temp_btn)
    for music in Music:
        temp_btn = music_btn(audio, music, loop=True)
        if music.value.explicit:
            temp_btn.disabled = safe
        button_controls.controls.append(temp_btn)
    sound_buttons = default_column([button_controls])
    sound_buttons.scroll = ft.ScrollMode.AUTO
    
    audio_controls = default_column([
        default_row([ft.Text("Master Volume", offset=ft.Offset(0, -0.1), text_align=ft.TextAlign.CENTER, width=100), mv_slider]),
        default_row([ft.Text("Audio Balance", offset=ft.Offset(0, -0.1), text_align=ft.TextAlign.CENTER, width=100), b_slider])
    ], expand=False)
    
    media_btns = ft.Container(ft.Row([pause_btn, stop_btn], tight=True, spacing=0), padding=0, margin=0, expand=False)
    media_controls = ft.Container(default_column([
        media_label,
        media_desc,
        ft.Row([media_seek, audio_slider, media_btns])
    ], expand=False))
    
    audio_settings_expansion = ft.ExpansionPanelList(
        controls=[ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text("Audio Settings"), leading=ft.Icon(ft.Icons.SPEAKER)),
            content=audio_controls
        )], elevation=8, visible=show_audio_settings
    )
    
    explicit_content_label = f"{"Enable" if safe else "Disable"} Explicit Content"
    settings_menu_button = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(
                text=explicit_content_label,
                on_click=toggle_explicit_content, icon=ft.Icons.MODE
            ),
            ft.PopupMenuItem(
                text="Overlapping SFX", icon=ft.Icons.SPEAKER_GROUP, checked=overlap_sfx,
                on_click=toggle_overlap_sfx
            ),
            ft.PopupMenuItem(
                text="Show Audio Settings", icon=ft.Icons.SETTINGS, checked=show_audio_settings,
                on_click=toggle_audio_settings
            )
        ]
    )
    
    if (page.platform == ft.PagePlatform.WINDOWS):
        page.appbar.actions.insert(0, mobile_dev_btn)
        page.appbar.actions.insert(1, settings_menu_button)
        
    form = ft.Container(
        default_column([
            audio_settings_expansion,
            ft.Divider(),
            sound_buttons,
            ft.Divider(),
            media_controls
        ]),
        expand=True
    )
    
    draggable_form = ft.Container(ft.WindowDragArea(form, maximizable=False), expand=True)
    
    page.add(draggable_form)


if __name__ == "__main__":
    ft.app(main, assets_dir="assets")