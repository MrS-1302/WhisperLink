from nicegui import ui
from . import page_main
from . import page_settings

def setup_pages():
    @ui.page('/')
    def main_page():
        page_main.create()

    @ui.page('/settings')
    def settings_page():
        page_settings.create()
    