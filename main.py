import flet as ft
from app.main_app import AudioApp
from app.quote_generator import QuoteApp

def main(page: ft.Page):
    # Initialize app instances
    audio_app = AudioApp(page)
    quote_app = QuoteApp(page)

    # Route-to-app mapping
    route_map = {
        "/": audio_app.load_app,
        "/quotes": quote_app.load_app
    }

    def route_change(_):
        # Clear current controls to ensure clean slate
        page.controls.clear()
        # Call the appropriate load_app() based on route
        route_handler = route_map.get(page.route, audio_app.load_app)  # Default to AudioApp if route not found
        route_handler()
        # Store the current route in history
        if not hasattr(page, 'route_history'):
            page.route_history = []
        if page.route not in page.route_history:
            page.route_history.append(page.route)
        page.update()

    def view_pop(_):
        # Remove the current route from history
        if hasattr(page, 'route_history') and len(page.route_history) > 1:
            page.route_history.pop()  # Remove current route
            previous_route = page.route_history[-1] if page.route_history else "/"
            page.go(previous_route)
        else:
            # If no previous route, go to home
            page.go("/")

    # Set up route handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Initialize with the current or default route
    page.go(page.route if page.route else "/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")