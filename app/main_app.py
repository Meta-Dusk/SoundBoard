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
        self._audio = AudioManager(page)
        self._storage = Storage(page)
        self._page = page
        self._landscape = False
        self._paused = False
        self._safe = True
        self._overlap_sfx = True
        self._show_audio_settings = True
        self._loop_music = True
        self._sfx_buttons = []
        self._music_buttons = []
        self._alt_sfx = []
        self._alt_music = []
    
    # ----- APP FUNCTIONS -----
    def load_app(self):
        print("Starting SeBored!")
        self._setup_page()
        self._setup_ui()
        print("Finished loading SeBored.")
    
    # ----- INTERNAL APP FUNCTIONS -----
    # UI Functions
    def _setup_page(self):
        if self._page.platform == ft.PagePlatform.WINDOWS:
            mobile_view(self._page, self._landscape, self._storage)
        else:
            base_page(self._page, storage=self._storage)
        mobile_appbar(self._page, storage=self._storage)
        
        loading_control = default_column([
            ft.Text("Loading SeBored...", text_align=ft.TextAlign.CENTER, size=20),
            ft.ProgressRing(width=200, height=200, stroke_width=5, padding=20)
        ])
        self._page.add(loading_control)
        self._audio.validate()
        self._alt_sfx, self._alt_music = self._audio.generate_non_explicits()
        self._page.remove(loading_control)

    def _setup_ui(self):
        self._page.controls.clear()
        
        # Text
        self.media_label = ft.Text(DEFAULTS.MEDIA_LABEL.value, size=20, color=ft.Colors.PRIMARY)
        self.media_desc = ft.Text(DEFAULTS.MEDIA_DESC.value, size=14, color=ft.Colors.SECONDARY)
        self.media_seek = ft.Text(DEFAULTS.MEDIA_SEEK.value, size=16, color=ft.Colors.SECONDARY, offset=ft.Offset(0, -0.1))
        explicit_content_label = f"{'Enable' if self._safe else 'Disable'} Explicit Content"
        
        # Buttons
        self.pause_btn = ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=self._on_pause, disabled=True)
        self.stop_btn = ft.IconButton(icon=ft.Icons.STOP, on_click=self._on_stop, disabled=True)
        self.settings_menu_button = ft.PopupMenuButton(items=[
            ft.PopupMenuItem(text=explicit_content_label, icon=ft.Icons.MODE, on_click=self._toggle_explicit_content),
            ft.PopupMenuItem(text="Overlapping SFX", icon=ft.Icons.SPEAKER_GROUP, checked=self._overlap_sfx, on_click=self._toggle_overlap_sfx),
            ft.PopupMenuItem(text="Show Audio Settings", icon=ft.Icons.SETTINGS, checked=self._show_audio_settings, on_click=self._toggle_audio_settings),
            ft.PopupMenuItem(text="Loop Music", icon=ft.Icons.LOOP, checked=self._loop_music, on_click=self._toggle_loop_music),
            ft.PopupMenuItem(text="Open Motivational Quotes", icon=ft.Icons.FORMAT_QUOTE, on_click=self._open_quote_generator)
        ])
        
        # Sliders
        self.mv_slider = master_volume_slider(self._audio, self._page, self._storage)
        self.mv_slider.padding = 5
        self.b_slider = audio_balance_slider(self._audio, self._storage)
        self.b_slider.padding = 5
        self._audio_slider = audio_duration_slider(self._audio, self.media_seek)
        self._audio_slider.padding = 5
        
        # Layouts
        self.button_controls = ft.ResponsiveRow(
            controls=[],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        self._rebuild_sound_buttons(initial=True)
        
        self.sound_buttons = default_column([self.button_controls])
        self.sound_buttons.scroll = ft.ScrollMode.AUTO
        
        self._audio_controls = default_column([
            default_row([ft.Text("Master Volume", offset=ft.Offset(0, -0.1), text_align=ft.TextAlign.CENTER, width=100), self.mv_slider]),
            default_row([ft.Text("Audio Balance", offset=ft.Offset(0, -0.1), text_align=ft.TextAlign.CENTER, width=100), self.b_slider])
        ], expand=False)
        
        self.media_btns = ft.Container(ft.Row([self.pause_btn, self.stop_btn], tight=True, spacing=0), padding=0, margin=0, expand=False)
        self.media_controls = ft.Container(default_column([
            self.media_label,
            self.media_desc,
            ft.Row([self.media_seek, self._audio_slider, self.media_btns])
        ], expand=False))
        
        self._audio_settings_expansion = ft.ExpansionPanelList(
            controls=[ft.ExpansionPanel(
                header=ft.ListTile(title=ft.Text("Audio Settings"), leading=ft.Icon(ft.Icons.SPEAKER)),
                content=self._audio_controls
            )], elevation=8, visible=self._show_audio_settings
        )
        
        # Optional Platform-Specific Controls
        if self._page.platform == ft.PagePlatform.WINDOWS:
            self.mobile_dev_btn = ft.IconButton(
                on_click=self._change_orientation,
                adaptive=True,
                icon=ft.Icons.STAY_CURRENT_LANDSCAPE
            )
            self._page.appbar.actions.insert(0, self.mobile_dev_btn)
            self._page.appbar.actions.insert(1, self.settings_menu_button)
        else:
            self._page.appbar.actions.insert(0, self.settings_menu_button)
        
        # Finalizing Layout
        self.form = ft.Container(
            default_column([
                self._audio_settings_expansion,
                hor_div(),
                self.sound_buttons,
                hor_div(),
                self.media_controls
            ]),
            expand=True
        )
        
        self.draggable_form = ft.Container(ft.WindowDragArea(self.form, maximizable=False), expand=True)
        self._page.add(self.draggable_form)

    # Component Functions
    def _rebuild_sound_buttons(self, initial=False):
        # Create random buttons with current settings
        self.rnd_sfx_btn = random_sfx_btn(
            audio=self._audio, 
            page=self._page, 
            safe=self._safe, 
            snackbar=True, 
            alt_sfx=self._alt_sfx, 
            overlap=self._overlap_sfx
        )
        self.rnd_music_btn = random_music_btn(
            audio=self._audio, 
            safe=self._safe, 
            loop=self._loop_music, 
            callbacks=[self._music_btn_pressed], 
            alt_music=self._alt_music
        )
        
        # Clear and rebuild button controls
        self.button_controls.controls.clear()
        self.button_controls.controls.append(self.rnd_sfx_btn)
        self.button_controls.controls.append(self.rnd_music_btn)
        
        # Rebuild SFX buttons
        self._sfx_buttons.clear()
        for sfx in SFX:
            temp_btn = sfx_btn(
                audio=self._audio, 
                page=self._page, 
                sfx=sfx, 
                overlap=self._overlap_sfx, 
                snackbar=True
            )
            if sfx.value.explicit:
                temp_btn.disabled = self._safe
            self.button_controls.controls.append(temp_btn)
            self._sfx_buttons.append(temp_btn)
        
        # Rebuild music buttons
        self._music_buttons.clear()
        for music in Music:
            temp_btn = music_btn(
                audio=self._audio, 
                music=music, 
                loop=self._loop_music, 
                callbacks=[self._music_btn_pressed]
            )
            if music.value.explicit:
                temp_btn.disabled = self._safe
            self.button_controls.controls.append(temp_btn)
            self._music_buttons.append(temp_btn)
        
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
        self._audio_slider.update()

    def _reset_components(self):
        self._paused = False
        self.pause_btn.icon = ft.Icons.PLAY_ARROW
        self.pause_btn.disabled = True
        self.stop_btn.disabled = True
        self.media_label.value = DEFAULTS.MEDIA_LABEL.value
        self.media_desc.value = DEFAULTS.MEDIA_DESC.value
        self.media_seek.value = DEFAULTS.MEDIA_SEEK.value
        self._audio_slider.disabled = True
        self._audio_slider.value = 0
        self._update_components()
    
    # Button Functions
    def _open_quote_generator(self, _):
        return
        print("Opening Motivational Quote Generator...")
        self._page.controls.clear()
        self._page.appbar.actions.clear()
        print("Finished loading Motivational Quote Generator!")
    
    def _on_pause(self, _):
        if self._paused:
            self._audio.resume_music()
            self._paused = False
            self.pause_btn.icon = ft.Icons.PLAY_ARROW
        else:
            self._audio.pause_music()
            self._paused = True
            self.pause_btn.icon = ft.Icons.PAUSE
        self.pause_btn.update()

    def _on_stop(self, _):
        if self._audio.music:
            self._paused = False
            self.pause_btn.icon = ft.Icons.PLAY_ARROW
            self._audio.stop_music()
            self._reset_components()

    def _music_btn_pressed(self, _):
        self._paused = False
        self.pause_btn.icon = ft.Icons.PLAY_ARROW
        self.pause_btn.disabled = False
        self.stop_btn.disabled = False
        music: Sound = self._audio.music.data
        self.media_label.value = music.title
        self.media_desc.value = music.description
        self._audio_slider.disabled = False
        self._update_components()

    def _change_orientation(self, _):
        self._landscape = not self._landscape
        print(f"Changing page orientation to {'landscape' if self._landscape else 'portrait'}")
        mobile_view(self._page, self._landscape)
        self.mobile_dev_btn.icon = ft.Icons.STAY_CURRENT_LANDSCAPE if not self._landscape else ft.Icons.STAY_CURRENT_PORTRAIT
        self._page.update()

    def _toggle_explicit_content(self, e: ft.ControlEvent):
        self._safe = not self._safe
        # Update alt_sfx and alt_music based on safe mode
        if self._safe:
            self._alt_sfx, self._alt_music = self._audio.generate_non_explicits()
        else:
            self._alt_sfx = list(SFX)
            self._alt_music = list(Music)
        msg = f"Explicit content is now {'disabled' if self._safe else 'enabled'}"
        popup_menu_item: ft.PopupMenuItem = e.control
        popup_menu_item.text = f"{'Enable' if self._safe else 'Disable'} Explicit Content"
        
        self._rebuild_sound_buttons()
        
        print(msg)
        self._page.open(notif_dialog(title="Explicit Content", content=msg))
        self._page.update()

    def _toggle_overlap_sfx(self, e: ft.ControlEvent):
        self._overlap_sfx = not self._overlap_sfx
        msg = f"Overlapping SFX is now {self._overlap_sfx}"
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = self._overlap_sfx
        
        self._rebuild_sound_buttons()
        
        print(msg)
        self._page.open(notif_dialog(title="Overlapping SFX", content=msg))
        self._page.update()

    def _toggle_audio_settings(self, e: ft.ControlEvent):
        self._show_audio_settings = not self._show_audio_settings
        msg = f"Now {'showing' if self._show_audio_settings else 'hiding'} the Audio Settings."
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = self._show_audio_settings
        self._audio_settings_expansion.visible = self._show_audio_settings
        print(msg)
        self._page.open(notif_dialog(title="Audio Settings", content=msg))
        self._page.update()

    def _toggle_loop_music(self, e: ft.ControlEvent):
        self._loop_music = not self._loop_music
        msg = f"Music is {'now looping' if self._loop_music else 'no longer looping'}."
        toggle_item: ft.PopupMenuItem = e.control
        toggle_item.checked = self._loop_music
        
        self._rebuild_sound_buttons()
        
        print(msg)
        self._page.open(notif_dialog(title="Music Settings", content=msg))
        self._page.update()