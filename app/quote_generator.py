import flet as ft
import requests
import random

from datetime import date
from .containers import default_column
from .styles import base_page, mobile_appbar


# Hardcoded fallback quotes
LOCAL_QUOTES = [
    {"quote": "They must often change, who would be constant in happiness or wisdom.", "author": "Confucius"},
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"quote": "Success is not the key to happiness. Happiness is the key to success.", "author": "Albert Schweitzer"},
]


def test(page: ft.Page):
    base_page(page)
    mobile_appbar(page)
    page.padding = 20

    # Initialize page.data for quotes and last refresh date
    page.data = {
        "quotes": LOCAL_QUOTES.copy(),  # Start with local quotes
        "last_refresh": None  # No refresh yet
    }

    # UI Components
    quote_text = ft.Text("Click to get a quote", size=20, italic=True, weight=ft.FontWeight.BOLD, font_family="Roboto")
    author_text = ft.Text("", size=16, color=ft.Colors.SECONDARY)
    attribution_text = ft.Text(
        spans=[
            ft.TextSpan(
                text="Powered by ZenQuotes",
                style=ft.TextStyle(color=ft.Colors.BLUE_600, size=12, decoration=ft.TextDecoration.UNDERLINE),
                on_click=lambda e: page.launch_url("https://zenquotes.io/")
            )
        ]
    )

    def fetch_quotes():
        """Fetch a batch of quotes from ZenQuotes API."""
        try:
            response = requests.get("https://zenquotes.io/api/quotes", timeout=5)
            response.raise_for_status()  # Raises HTTPError for bad status codes
            quotes = [
                {"quote": q["q"], "author": q["a"]}
                for q in response.json()
                if q["q"]  # Ensure non-empty quotes
            ]
            return quotes  # ZenQuotes returns ~50 quotes
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:
                print("Rate limit exceeded (HTTP 429)")
                page.open(ft.SnackBar(ft.Text("Rate limit reached. Using local quotes. Try again later."), duration=3000))
            else:
                print(f"HTTP error: {err}")
                page.open(ft.SnackBar(ft.Text("API error occurred. Using local quotes."), duration=2000))
            return LOCAL_QUOTES
        except requests.exceptions.ConnectionError as err:
            print(f"Connection error: {err}")
            page.open(ft.SnackBar(ft.Text("Network connection failed. Using local quotes."), duration=2000))
            return LOCAL_QUOTES
        except requests.exceptions.Timeout as err:
            print(f"Timeout error: {err}")
            page.open(ft.SnackBar(ft.Text("API request timed out. Using local quotes."), duration=2000))
            return LOCAL_QUOTES
        except requests.exceptions.RequestException as err:
            print(f"General request error: {err}")
            page.open(ft.SnackBar(ft.Text("Failed to fetch quotes. Using local quotes."), duration=2000))
            return LOCAL_QUOTES

    def refresh_quotes_if_needed():
        """Refresh quote list if it's a new day."""
        today = date.today()
        if page.data["last_refresh"] != today:
            page.data["quotes"] = fetch_quotes()
            page.data["last_refresh"] = today
            print(f"Refreshed quotes on {today}. Total quotes: {len(page.data['quotes'])}")
            if page.data["quotes"] == LOCAL_QUOTES:
                page.open(ft.SnackBar(ft.Text("Using local quotes due to network error"), duration=2000))

    def show_quote(_):
        """Display a random quote from the pre-generated list."""
        refresh_quotes_if_needed()  # Check if refresh is needed
        quote = random.choice(page.data["quotes"])
        quote_text.value = f"\"{quote['quote']}\""
        author_text.value = f"— {quote['author']}"
        page.update()

    # Initial quote fetch
    page.add(default_column([
        ft.Text("Loading Quotes...", text_align=ft.TextAlign.CENTER, size=20),
        ft.ProgressRing(width=200, height=200)
    ]))
    refresh_quotes_if_needed()
    page.controls.clear()

    # Layout
    page.add(default_column([
        quote_text,
        author_text,
        attribution_text,
        ft.ElevatedButton("Get Quote", on_click=show_quote)
    ], spacing=10))


if __name__ == "__main__":
    ft.app(target=test)