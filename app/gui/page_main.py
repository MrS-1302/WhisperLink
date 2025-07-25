from nicegui import ui
import time
import re
from threading import Thread
from app.workers.downloader import Downloader

from app.utils.cards import Card
from app.utils.database_structure import db

class MainPage:
    def __init__(self):
        self.cards_container = None
        self.LOADING_LIMIT = 10
        self.is_loading_cards = False
        self.has_more_cards = True
        self.last_card_id = 0

    async def load_cards(self):
        """
        Betölti az adatbázisból a linkeket és létrehozza a kártyákat.
        """

        if self.is_loading_cards or not self.has_more_cards: # Csak akkor töltünk, ha nem töltünk éppen és van még kártya
            return

        self.is_loading_cards = True # Beállítjuk a töltési állapotot

        test = f' WHERE LinkID < {self.last_card_id} '
        rows = db.fetch_all(f"SELECT LinkID, Link, Title FROM links {test if self.last_card_id != 0 else ''} ORDER BY LinkID DESC LIMIT {self.LOADING_LIMIT};")
        
        if rows:
            for row in rows:
                link_id, link, title = row
                Card(self.cards_container, title or link, card_id=link_id, disable=False, top=False)
                self.last_card_id = link_id  # Frissítjük az utolsó kártya ID-t
            if len(rows) < self.LOADING_LIMIT: # Ha kevesebb kártya jött vissza, mint a limit, akkor nincs több
                self.has_more_cards = False
        else:
            # Nincs több betölthető kártya
            self.has_more_cards = False
            ui.notify('Nincs több betölthető kártya.', type='info')

        self.is_loading_cards = False # Visszaállítjuk a töltési állapotot

    async def create(self):
        ui.add_head_html('<style>body {background-color: #fce1b6; }</style>')
        ui.page_title('WhisperLink | Main page')

        # Funkció a beviteli mező tartalmának beküldésére
        def submit() -> None:
            regex = r'^(https?://)?(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$'
            if text_input.value != '':
                if not re.match(regex, text_input.value):
                    ui.notify('Érvénytelen URL formátum!', color='red')
                    return
                
                card_uuid = str(time.time()).replace('.', '') 
                card = Card(self.cards_container, text_input.value, card_id=f'card-{card_uuid}')
                downloader = Downloader(text_input.value)
                thread = Thread(target=downloader.download)
                thread.start()

                # Funkció a cím ellenőrzésére és a kártya frissítésére
                def check_title():
                    title = downloader.get_title()
                    if title and title != 'N/A':
                        card.card_label.set_text(title)
                        card.buttons['content_copy'].enable()
                        card.buttons['edit'].enable()
                        card.buttons['delete'].enable()
                        polling_timer.deactivate()
                    # Ha még nincs cím, a polling folytatódik

                # Időzítő indítása a cím periodikus ellenőrzésére (pl. minden 1 másodpercben)
                polling_timer = ui.timer(1.0, check_title) 
                polling_timer.activate()

                text_input.set_value('') # A mező ürítése beküldés után
                text_input.run_method('blur') # Fókusz elvétele a beviteli mezőről

        # --- Fix Fejléc Szekció ---
        with ui.header().classes('q-py-sm').style('background-color: transparent; backdrop-filter: blur(10px); box-shadow: 0px 8px 20px 0px rgba(0,0,0,0.3);'):
            with ui.row().classes('w-full no-wrap items-center q-mx-auto max-w-screen-md q-px-md'):
                text_input = ui.input(placeholder='Link') \
                    .on('keydown.enter', submit) \
                    .props('rounded outlined bg-color=white clearable') \
                    .classes('flex-grow text-lg')
                
                ui.button(icon='arrow_forward', on_click=submit, color='#FEF3E2') \
                    .props('round') \
                    .classes('h-12 w-12 flex-none q-ml-sm') \
                    .style('color: black;')
        # --- Fix Fejléc Szekció Vége ---

        with ui.column().classes('q-mx-auto max-w-screen-md q-pa-md w-full'):
            self.cards_container = ui.column().classes('w-full').props('id=cards-container')

        with ui.page_sticky(x_offset=18, y_offset=18).style('z-index:99;'):
            ui.button(icon='settings', on_click=lambda: ui.notify('Meow?'), color="#FEF3E2") \
                .props('fab') \
                .style('color: black;')
        
        # Kezdeti kártyák betöltése
        await self.load_cards()

        # Infinite scroll funkció
        async def check_scroll_position():
            if not self.has_more_cards: # Ha nincs több kártya, nem ellenőrizzük a görgetést
                check_scroll_position_timer.deactivate()
                return

            # Ellenőrizzük, hogy a felhasználó elég közel van-e az oldal aljához
            # Növeljük az időtúllépést 5 másodpercre
            try:
                scroll_threshold_reached = await ui.run_javascript('window.pageYOffset + window.innerHeight >= document.body.offsetHeight - 200', timeout=5.0) # 200px puffer
            except Exception as e:
                pass

            if scroll_threshold_reached and not self.is_loading_cards: # Ha elérte a küszöböt ÉS nem töltünk éppen
                await self.load_cards()

        # Indítjuk a timert a görgetési pozíció ellenőrzésére
        check_scroll_position_timer = ui.timer(0.2, check_scroll_position) # Gyakrabban ellenőrizzük, pl. 200ms-enként