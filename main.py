from nicegui import app as nicegui_app, native, ui
from app.gui.pages import setup_pages

nicegui_app.on_startup(setup_pages)

ui.run(native=False, port=native.find_open_port())