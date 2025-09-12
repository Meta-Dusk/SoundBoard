import flet as ft
import requests
import random

from datetime import date
from enum import Enum
from .containers import default_column, default_row
from .styles import base_page, mobile_appbar, mobile_view, hor_div
from .storage import Storage


# Hardcoded fallback quotes
LOCAL_QUOTES = [
    {"quote": "They must often change, who would be constant in happiness or wisdom.", "author": "Confucius"},
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"quote": "Success is not the key to happiness. Happiness is the key to success.", "author": "Albert Schweitzer"},
]


class QuoteKeys(Enum):
    QUOTES = "quotes"
    LAST_REFRESH = "last_refresh"


class QuoteApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = Storage(page, debug=True)
        self.landscape = False
    
    # ----- APP FUNCTIONS -----
    def load_app(self):
        print("Starting the Quote Generator!")
        self._setup_page()
        self._setup_ui()
        print("Quoting Generator finished loading.")
    
    # ----- INTERNAL APP FUNCTIONS -----
    # UI Functions
    def _setup_page(self):
        if self.page.platform == ft.PagePlatform.WINDOWS:
            mobile_view(self.page, self.landscape, self.storage)
        else:
            base_page(self.page, storage=self.storage)
        mobile_appbar(self.page, storage=self.storage)
        self.page.padding = 20

    def _setup_ui(self):
        self.page.controls.clear()
        self.quote_text = ft.Text("Click to get a quote", size=20, italic=True, weight=ft.FontWeight.BOLD, font_family="Roboto")
        self.author_text = ft.Text("", size=16, color=ft.Colors.SECONDARY)
        self.attribution_text = ft.Text(
            spans=[
                ft.TextSpan(
                    text="Powered by ZenQuotes",
                    style=ft.TextStyle(color=ft.Colors.BLUE_600, size=15, decoration=ft.TextDecoration.UNDERLINE),
                    on_click=lambda e: self.page.launch_url("https://zenquotes.io/")
                )
            ]
        )

        # Initial quote fetch
        self.page.add(default_column([
            ft.Text("Loading Quotes...", text_align=ft.TextAlign.CENTER, size=20),
            ft.ProgressRing(width=200, height=200)
        ]))
        self._refresh_quotes_if_needed()
        self.page.controls.clear()
        
        # Optional AppBar Buttons
        if self.page.platform == ft.PagePlatform.WINDOWS:
            self.mobile_dev_btn = ft.IconButton(
                on_click=self._change_orientation,
                adaptive=True,
                icon=ft.Icons.STAY_CURRENT_LANDSCAPE
            )
            self.page.appbar.actions.insert(0, self.mobile_dev_btn)
        
        # Buttons
        self.get_quote_btn = ft.ElevatedButton(
            text="Get Quote", on_click=self._show_quote, expand=True, height=50
        )
        self.exit_to_main = ft.ElevatedButton(
            text="Go Back", on_click=self._exit_to_main, expand=True, height=50
        )
        
        # Layout
        text_column = ft.Column(
            [
                self.quote_text,
                self.author_text
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        main_form = ft.Column([
            text_column,
            hor_div(),
            default_row([self.get_quote_btn, self.exit_to_main])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.add(ft.Column(
            [
                ft.Container(expand=True),
                main_form,
                ft.Container(expand=True),
                self.attribution_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True))
    
    def _change_orientation(self, _):
        self.landscape = not self.landscape
        print(f"Changing page orientation to {'landscape' if self.landscape else 'portrait'}")
        mobile_view(self.page, self.landscape)
        self.mobile_dev_btn.icon = ft.Icons.STAY_CURRENT_LANDSCAPE if not self.landscape else ft.Icons.STAY_CURRENT_PORTRAIT
        self.page.update()
    
    def _exit_to_main(self, _):
        # Implement :)
        pass
    
    # Quote Functions
    def _fetch_quotes(self):
        """Fetch a batch of quotes from ZenQuotes API."""
        try:
            response = requests.get("https://zenquotes.io/api/quotes", timeout=5)
            response.raise_for_status()
            quotes = [
                {"quote": q["q"], "author": q["a"]}
                for q in response.json()
                if q["q"]
            ]
            return quotes
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:
                print("Rate limit exceeded (HTTP 429)")
                self.page.open(ft.SnackBar(ft.Text("Rate limit reached. Using local quotes. Try again later."), duration=3000))
            else:
                print(f"HTTP error: {err}")
                self.page.open(ft.SnackBar(ft.Text("API error occurred. Using local quotes."), duration=2000))
            return LOCAL_QUOTES
        except requests.exceptions.ConnectionError as err:
            print(f"Connection error: {err}")
            self.page.open(ft.SnackBar(ft.Text("Network connection failed. Using local quotes."), duration=2000))
            return LOCAL_QUOTES
        except requests.exceptions.Timeout as err:
            print(f"Timeout error: {err}")
            self.page.open(ft.SnackBar(ft.Text("API request timed out. Using local quotes."), duration=2000))
            return LOCAL_QUOTES
        except requests.exceptions.RequestException as err:
            print(f"General request error: {err}")
            self.page.open(ft.SnackBar(ft.Text("Failed to fetch quotes. Using local quotes."), duration=2000))
            return LOCAL_QUOTES

    def _refresh_quotes_if_needed(self):
        """Refresh quote list if it's a new day."""
        today = date.today()
        last_refresh = self.storage.get(QuoteKeys.LAST_REFRESH)
        
        # Convert stored date string to date object if it exists
        if last_refresh and isinstance(last_refresh, str):
            try:
                last_refresh = date.fromisoformat(last_refresh)
            except ValueError:
                last_refresh = None

        if last_refresh != today:
            quotes = self._fetch_quotes()
            self.storage.set(QuoteKeys.QUOTES, quotes)
            self.storage.set(QuoteKeys.LAST_REFRESH, today.isoformat())  # Store as string
            print(f"Refreshed quotes on {today}. Total quotes: {len(quotes)}")
            if quotes == LOCAL_QUOTES:
                self.page.open(ft.SnackBar(ft.Text("Using local quotes due to network error"), duration=2000))
        elif not self.storage.check(QuoteKeys.QUOTES):
            # If no quotes are stored, use local quotes
            self.storage.set(QuoteKeys.QUOTES, LOCAL_QUOTES)
            print("No stored quotes found. Using local quotes.")

    def _show_quote(self, _):
        """Display a random quote from the stored list."""
        self._refresh_quotes_if_needed()
        quotes = self.storage.get(QuoteKeys.QUOTES) or LOCAL_QUOTES
        quote = random.choice(quotes)
        self.quote_text.value = f"\"{quote['quote']}\""
        self.author_text.value = f"— {quote['author']}"
        self.page.update()


def main(page: ft.Page):
    app = QuoteApp(page)
    app.load_app()


if __name__ == "__main__":
    ft.app(target=main)