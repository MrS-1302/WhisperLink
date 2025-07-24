from nicegui import ui
import time
from . import page_main
from . import page_settings

def setup_pages():
    @ui.page('/')
    async def main_page():
        await page_main.create()

    @ui.page('/settings')
    def settings_page():
        page_settings.create()