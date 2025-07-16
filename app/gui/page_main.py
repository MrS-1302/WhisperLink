from nicegui import ui
import time
import re
from threading import Thread
from app.workers.downloader import Downloader

cards_container = None

def create_card(text: str, card_id: str = None):
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
            with ui.row().classes('w-full justify-end no-wrap'):
                content_copy = ui.button(icon='content_copy', on_click=lambda: ui.notify(f'Megnyomtad a Másolás gombot a "{text}" kártyánál'))
                edit = ui.button(icon='edit', on_click=lambda: ui.notify(f'Megnyomtad a Szerkesztés gombot a "{text}" kártyánál'))
                delete = ui.button(icon='delete', on_click=lambda: ui.notify(f'Megnyomtad a Törlés gombot a "{text}" kártyánál'))

            # Kontextus menü a kártyán
            with ui.context_menu():
                ui.menu_item('Copy')
                ui.menu_item('Edit')
                ui.menu_item('Delete')

    # Az új kártya áthelyezése a lista elejére
    delete.disable()  # A törlés gomb kezdetben le van tiltva
    edit.disable()    # A szerkesztés gomb kezdetben le van tiltva
    content_copy.disable()  # A másolás gomb kezdetben le van tiltva
    card_element.move(target_index=0)
    return (card_label, content_copy, edit, delete)

def create():
    global cards_container

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
            card_label, content_copy, edit, delete = create_card(text_input.value, card_id=f'card-{card_uuid}')
            downloader = Downloader(text_input.value)
            thread = Thread(target=downloader.download)
            thread.start()

            # Funkció a cím ellenőrzésére és a kártya frissítésére
            def check_title():
                title = downloader.get_title()
                if title and title != 'N/A':
                    #ui.run_javascript(f"document.getElementById('label-card-{card_uuid}').innerText = '{title}';")
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
    # Ez a fejléc mindig az oldal tetején marad görgetéskor
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