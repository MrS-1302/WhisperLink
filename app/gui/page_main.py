from nicegui import ui
import time
import re
from threading import Thread
import random
from app.workers.downloader import Downloader

from app.utils.database_structure import db

cards_container = None
offset = 0 # Új globális változó az eltoláshoz
LOADING_LIMIT = 10 # Hány kártyát töltsön be egyszerre
is_loading_cards = False # ÚJ: Jelzi, hogy éppen töltődnek-e a kártyák
has_more_cards = True # ÚJ: Jelzi, hogy van-e még betölthető kártya

def create_card(text: str, card_id: str = None, disable: bool = True, top: bool = True):
    """
    Létrehoz egy új kártyát a megadott szöveggel és opcionális azonosítóval.
    Ha van azonosító, az a kártya és a benne lévő címke HTML ID-jeként is beállítódik.
    """
    with cards_container:
        # A kártya létrehozása, opcionálisan ID-vel a későbbi frissítéshez
        with ui.card().classes('w-full').style('box-shadow: 0px 0px 4px 3px rgba(0,0,0,0.2);') as card_element:
            if card_id:
                card_element.props(f'id={card_id}')
            
            # A címke létrehozása, opcionálisan ID-vel
            card_label = ui.label(text).classes('text-lg font-semibold').props(f'id=label-{card_id}' if card_id else '')

            # Gombok a kártyán
            with ui.row().classes('w-full justify-end no-wrap').style('align-items: center;'):
                progressbarText = ui.label('Downloading').classes('hidden')
                def format_main_seq_progress(progress: float | None) -> str:
                    if progress is None:
                        return ""
                    return f"{progressbarText.text} - {progress:.1%}"


                progressbar = ui.linear_progress(show_value=False, size="35px", value=random.uniform(0, 1)).props("rounded")
                with progressbar:
                    label = ui.label().classes("absolute-center text-sm text-black").style('margin-top: 1px; font-weight: 500;')
                    label.bind_text_from(progressbar, "value", backward=lambda p: format_main_seq_progress(p))
                
                # Példa a progress bar frissítésére
                def test():
                    progressbarText.text = 'Transcribe' if random.choice([True, False]) else 'Downloading'
                    progressbar.set_value(random.uniform(0, 1))
                ui.timer(random.randint(1,5), test)

                content_copy = ui.button(icon='content_copy', on_click=lambda: ui.notify(f'Megnyomtad a Másolás gombot a "{text}" kártyánál'))
                edit = ui.button(icon='edit', on_click=lambda: ui.notify(f'Megnyomtad a Szerkesztés gombot a "{text}" kártyánál'))
                delete = ui.button(icon='delete', on_click=lambda: ui.notify(f'Megnyomtad a Törlés gombot a "{text}" kártyánál'))

            # Kontextus menü a kártyán
            with ui.context_menu():
                ui.menu_item('Copy')
                ui.menu_item('Edit')
                ui.menu_item('Delete')

    # Az új kártya áthelyezése a lista elejére
    if disable:
        content_copy.disable()
        edit.disable()
        delete.disable()
    if top: card_element.move(target_index=0)
    return (card_label, content_copy, edit, delete)

async def load_cards():
    """
    Betölti az adatbázisból a linkeket és létrehozza a kártyákat.
    """
    global offset, is_loading_cards, has_more_cards

    if is_loading_cards or not has_more_cards: # Csak akkor töltünk, ha nem töltünk éppen és van még kártya
        return

    is_loading_cards = True # Beállítjuk a töltési állapotot

    rows = db.fetch_all(f"SELECT LinkID, Link, Title FROM links ORDER BY LinkID DESC LIMIT {LOADING_LIMIT} OFFSET {offset}")
    
    if rows:
        for row in rows:
            link_id, link, title = row
            create_card(title or link, card_id=f'card-{link_id}', disable=False, top=False)
        offset += len(rows) # Növeljük az offsetet a betöltött kártyák számával
        if len(rows) < LOADING_LIMIT: # Ha kevesebb kártya jött vissza, mint a limit, akkor nincs több
            has_more_cards = False
    else:
        # Nincs több betölthető kártya
        has_more_cards = False
        ui.notify('Nincs több betölthető kártya.', type='info')

    is_loading_cards = False # Visszaállítjuk a töltési állapotot

async def create():
    global cards_container, offset, is_loading_cards, has_more_cards

    ui.add_head_html('<style>body {background-color: #fce1b6; }</style>')
    ui.page_title('WhisperLink | Main page')

    # Reset állapotváltozók, amikor az oldal létrejön
    offset = 0
    is_loading_cards = False
    has_more_cards = True

    # Funkció a beviteli mező tartalmának beküldésére
    def submit() -> None:
        regex = r'^(https?://)?(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)$'
        if text_input.value != '':
            if not re.match(regex, text_input.value):
                ui.notify('Érvénytelen URL formátum!', color='red')
                return
            
            card_uuid = str(time.time()).replace('.', '') 
            card_label, content_copy, edit, delete = create_card(text_input.value, card_id=f'card-{card_uuid}')
            downloader = Downloader(text_input.value)
            thread = Thread(target=downloader.download)
            thread.start()

            # Funkció a cím ellenőrzésére és a kártya frissítésére
            def check_title():
                title = downloader.get_title()
                if title and title != 'N/A':
                    card_label.set_text(title)
                    content_copy.enable()
                    edit.enable()
                    delete.enable()
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
        cards_container = ui.column().classes('w-full').props('id=cards-container')

    with ui.page_sticky(x_offset=18, y_offset=18).style('z-index:99;'):
        ui.button(icon='settings', on_click=lambda: ui.notify('Meow?'), color="#FEF3E2") \
            .props('fab') \
            .style('color: black;')
    
    # Kezdeti kártyák betöltése
    await load_cards()

    # Infinite scroll funkció
    async def check_scroll_position():
        global is_loading_cards, has_more_cards
        if not has_more_cards: # Ha nincs több kártya, nem ellenőrizzük a görgetést
            return

        # Ellenőrizzük, hogy a felhasználó elég közel van-e az oldal aljához
        # Növeljük az időtúllépést 5 másodpercre
        scroll_threshold_reached = await ui.run_javascript('window.pageYOffset + window.innerHeight >= document.body.offsetHeight - 200', timeout=5.0) # 200px puffer
        
        if scroll_threshold_reached and not is_loading_cards: # Ha elérte a küszöböt ÉS nem töltünk éppen
            await load_cards()

    # Indítjuk a timert a görgetési pozíció ellenőrzésére
    ui.timer(0.2, check_scroll_position) # Gyakrabban ellenőrizzük, pl. 200ms-enként