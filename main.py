from nicegui import native, ui, app
from app.startup import startup

app.on_startup(startup)

ui.run(port=native.find_open_port())