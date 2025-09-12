import flet as ft
from app.containers import default_row, default_column
from app.audio import AudioManager
from app.styles import mobile_view, mobile_appbar, base_page, hor_div
from app.components import (
    random_music_btn, random_sfx_btn, master_volume_slider,  audio_duration_slider, audio_balance_slider, sfx_btn, music_btn
)
from app.storage import Storage
from app.file_declarations import Sound, SFX, Music
from app.popups import notif_dialog
from enum import Enum


class DEFAULTS(Enum):
    MEDIA_LABEL = "No Music Playing"
    MEDIA_DESC = "Play any music for it to display here."
    MEDIA_SEEK = "0:00/0:00"


# TODO: Refactor sound button components to be able to update dynamically, instead of relying on rebuilding them.
class AudioApp:
    def __init__(self, page: ft.Page):
        self.audio = AudioManager(page)
        self.storage = Storage(page)
        self.page = page
        self.landscape = False
        self.paused = False
        self.safe = True
        self.overlap_sfx = True
        self.show_audio_settings = True
        self.loop_music = True
        self.sfx_buttons = []
        self.music_buttons = []
        self.alt_sfx = []
        self.alt_music = []
    
    # ----- APP FUNCTIONS -----
    def load_app(self):
        print("Starting SeBored!")
        self._setup_page()
        self._setup_ui()
        print("Finished loading SeBored.")
    
    # ----- INTERNAL APP FUNCTIONS -----
    # UI Functions
    def _setup_page(self):
        if self.page.platform == ft.PagePlatform.WINDOWS:
            mobile_view(self.page, self.landscape, self.storage)
        else:
            base_page(self.page, storage=self.storage)
        mobile_appbar(self.page, storage=self.storage)
        
        loading_control = default_column([
            ft.Text("Loading SeBored...", text_align=ft.TextAlign.CENTER, size=20),
            ft.ProgressRing(width=200, height=200, stroke_width=5, padding=20)
        ])
        self.page.add(loading_control)
        self.audio.validate()
        self.alt_sfx, self.alt_music = self.audio.generate_non_explicits()
        self.page.remove(loading_control)

    def _setup_ui(self):
        self.media_label = ft.Text(DEFAULTS.MEDIA_LABEL.value, size=20, color=ft.Colors.PRIMARY)
        self.media_desc = ft.Text(DEFAULTS.MEDIA_DESC.value, size=14, color=ft.Colors.SECONDARY)
        self.media_seek = ft.Text(DEFAULTS.MEDIA_SEEK.value, size=16, color=ft.Colors.SECONDARY, offset=ft.Offset(0, -0.1))
        
        self.mobile_dev_btn = ft.IconButton(
            on_click=self._change_orientation,
            adaptive=True,
            icon=ft.Icons.STAY_CURRENT_LANDSCAPE
        )
        self.pause_btn = ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=self._on_pause, disabled=True)
        self.stop_btn = ft.IconButton(icon=ft.Icons.STOP, on_click=self._on_stop, disabled=True)
        
        self.mv_slider = master_volume_slider(self.audio, self.page, self.storage)
        self.mv_slider.padding = 5
        self.b_slider = audio_balance_slider(self.audio, self.storage)
        self.b_slider.padding = 5
        self.audio_slider = audio_duration_slider(self.audio, self.media_seek)
        self.audio_slider.padding = 5
        
        self.button_controls = ft.ResponsiveRow(
            controls=[],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self._rebuild_sound_buttons(initial=True)
        
        self.sound_buttons = default_column([self.button_controls])
        self.sound_buttons.scroll = ft.ScrollMode.AUTO
        
        self.audio_controls = default_column([
            default_row([ft.Text("Master Volume", offset=ft.Offset(0, -0.1), text_align=ft.TextAlign.CENTER, width=100), self.mv_slider]),
            default_row([ft.Text("Audio Balance", offset=ft.Offset(0, -0.1), text_align=ft.TextAlign.CENTER, width=100), self.b_slider])
        ], expand=False)
        
        self.media_btns = ft.Container(ft.Row([self.pause_btn, self.stop_btn], tight=True, spacing=0), padding=0, margin=0, expand=False)
        self.media_controls = ft.Container(default_column([
            self.media_label,
            self.media_desc,
            ft.Row([self.media_seek, self.audio_slider, self.media_btns])
        ], expand=False))
        
        self.audio_settings_expansion = ft.ExpansionPanelList(
            controls=[ft.ExpansionPanel(
                header=ft.ListTile(title=ft.Text("Audio Settings"), leading=ft.Icon(ft.Icons.SPEAKER)),
                content=self.audio_controls
            )], elevation=8, visible=self.show_audio_settings
        )
        
        explicit_content_label = f"{'Enable' if self.safe else 'Disable'} Explicit Content"
        self.settings_menu_button = ft.PopupMenuButton(items=[
            ft.PopupMenuItem(text=explicit_content_label, icon=ft.Icons.MODE, on_click=self._toggle_explicit_content),
            ft.PopupMenuItem(text="Overlapping SFX", icon=ft.Icons.SPEAKER_GROUP, checked=self.overlap_sfx, on_click=self._toggle_overlap_sfx),
            ft.PopupMenuItem(text="Show Audio Settings", icon=ft.Icons.SETTINGS, checked=self.show_audio_settings, on_click=self._toggle_audio_settings),
            ft.PopupMenuItem(text="Loop Music", icon=ft.Icons.LOOP, checked=self.loop_music, on_click=self._toggle_loop_music)
        ])
        
        if self.page.platform == ft.PagePlatform.WINDOWS:
            self.page.appbar.actions.insert(0, self.mobile_dev_btn)
            self.page.appbar.actions.insert(1, self.settings_menu_button)
        
        self.form = ft.Container(
            default_column([
                self.audio_settings_expansion,
                hor_div(),
                self.sound_buttons,
                hor_div(),
                self.media_controls
            ]),
            expand=True
        )
        
        self.draggable_form = ft.Container(ft.WindowDragArea(self.form, maximizable=False), expand=True)
        self.page.add(self.draggable_form)

    # Component Functions
    def _rebuild_sound_buttons(self, initial=False):
        # Create random buttons with current settings
        self.rnd_sfx_btn = random_sfx_btn(
            audio=self.audio, 
            page=self.page, 
            safe=self.safe, 
            snackbar=True, 
            alt_sfx=self.alt_sfx, 
            overlap=self.overlap_sfx
        )
        self.rnd_music_btn = random_music_btn(
            audio=self.audio, 
            safe=self.safe, 
            loop=self.loop_music, 
            callbacks=[self._music_btn_pressed], 
            alt_music=self.alt_music
        )
        
        # Clear and rebuild button controls
        self.button_controls.controls.clear()
        self.button_controls.controls.append(self.rnd_sfx_btn)
        self.button_controls.controls.append(self.rnd_music_btn)
        
        # Rebuild SFX buttons
        self.sfx_buttons.clear()
        for sfx in SFX:
            temp_btn = sfx_btn(
                audio=self.audio, 
                page=self.page, 
                sfx=sfx, 
                overlap=self.overlap_sfx, 
                snackbar=True
            )
            if sfx.value.explicit:
                temp_btn.disabled = self.safe
            self.button_controls.controls.append(temp_btn)
            self.sfx_buttons.append(temp_btn)
        
        # Rebuild music buttons
        self.music_buttons.clear()
        for music in Music:
            temp_btn = music_btn(
                audio=self.audio, 
                music=music, 
                loop=self.loop_music, 
                callbacks=[self._music_btn_pressed]
            )
            if music.value.explicit:
                temp_btn.disabled = self.safe
            self.button_controls.controls.append(temp_btn)
            self.music_buttons.append(temp_btn)
        
        # Only update if not initial call (i.e., after controls are added to page)
        if not initial:
            self.button_controls.update()
            self.sound_buttons.update()
    
    def _update_components(self):
        self.pause_btn.update()
        self.stop_btn.update()
        self.media_label.update()
        self.media_desc.update()
        self.media_seek.update()
        self.audio_slider.update()

    def _reset_components(self):
        self.paused = False
        self.pause_btn.icon = ft.Icons.PLAY_ARROW
        self.pause_btn.disabled = True
        self.stop_btn.disabled = True
        self.media_label.value = DEFAULTS.MEDIA_LABEL.value
        self.media_desc.value = DEFAULTS.MEDIA_DESC.value
        self.media_seek.value = DEFAULTS.MEDIA_SEEK.value
        self.audio_slider.disabled = True
        self.audio_slider.value = 0
        self._update_components()
    
    # Button Functions
    def _on_pause(self, _):
        if self.paused:
            self.audio.resume_music()
            self.paused = False
            self.pause_btn.icon = ft.Icons.PLAY_ARROW
        else:
            self.audio.pause_music()
            self.paused = True
            self.pause_btn.icon = ft.Icons.PAUSE
        self.pause_btn.update()

    def _on_stop(self, _):
        if self.audio.music:
            self.paused = False
            self.pause_btn.icon = ft.Icons.PLAY_ARROW
            self.audio.stop_music()
            self._reset_components()

    def _music_btn_pressed(self, _):
        self.paused = False
        self.pause_btn.icon = ft.Icons.PLAY_ARROW
        self.pause_btn.disabled = False
        self.stop_btn.disabled = False
        music: Sound = self.audio.music.data
        self.media_label.value = music.title
        self.media_desc.value = music.description
        self.audio_slider.disabled = False
        self._update_components()

    def _change_orientation(self, _):
        self.landscape = not self.landscape
        print(f"Changing page orientation to {'landscape' if self.landscape else 'portrait'}")
        mobile_view(self.page, self.landscape)
        self.mobile_dev_btn.icon = ft.Icons.STAY_CURRENT_LANDSCAPE if not self.landscape else ft.Icons.STAY_CURRENT_PORTRAIT
        self.page.update()

    def _toggle_explicit_content(self, e: ft.ControlEvent):
        self.safe = not self.safe
        # Update alt_sfx and alt_music based on safe mode
        if self.safe:
            self.alt_sfx, self.alt_music = self.audio.generate_non_explicits()
        else:
            self.alt_sfx = list(SFX)
            self.alt_music = list(Music)
        msg = f"Explicit content is now {'disabled' if self.safe else 'enabled'}"
        popup_menu_item: ft.PopupMenuItem = e.control
        popup_menu_item.text = f"{'Enable' if self.safe else 'Disable'} Explicit Content"
        
        self._rebuild_sound_buttons()
        
        print(msg)
        self.page.open(notif_dialog(title="Explicit Content", content=msg))
        self.page.update()

    def _toggle_overlap_sfx(self, e: ft.ControlEvent):
        self.overlap_sfx = not self.overlap_sfx
        msg = f"Overlapping SFX is now {self.overlap_sfx}"
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = self.overlap_sfx
        
        self._rebuild_sound_buttons()
        
        print(msg)
        self.page.open(notif_dialog(title="Overlapping SFX", content=msg))
        self.page.update()

    def _toggle_audio_settings(self, e: ft.ControlEvent):
        self.show_audio_settings = not self.show_audio_settings
        msg = f"Now {'showing' if self.show_audio_settings else 'hiding'} the Audio Settings."
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = self.show_audio_settings
        self.audio_settings_expansion.visible = self.show_audio_settings
        print(msg)
        self.page.open(notif_dialog(title="Audio Settings", content=msg))
        self.page.update()

    def _toggle_loop_music(self, e: ft.ControlEvent):
        self.loop_music = not self.loop_music
        msg = f"Music is {'now looping' if self.loop_music else 'no longer looping'}."
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = self.loop_music
        
        self._rebuild_sound_buttons()
        
        print(msg)
        self.page.open(notif_dialog(title="Music Settings", content=msg))
        self.page.update()