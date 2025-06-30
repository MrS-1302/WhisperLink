from nicegui import Client, ui, app

def create_card(text: str):
    """Létrehoz egy kártyát szöveges tartalommal és három gombbal."""
    with ui.card().classes('w-full').style('box-shadow: 0px 0px 4px 3px rgba(0,0,0,0.2);'):
        #ui.label(text).classes('text-lg font-semibold')
        ui.skeleton().classes('w-full')
        with ui.row().classes('w-full justify-end no-wrap'):
            ui.button(icon='content_copy', on_click=lambda: ui.notify(f'Megnyomtad a Gomb 3-at a "{text}" kártyánál'))
            ui.button(icon='edit', on_click=lambda: ui.notify(f'Megnyomtad a Gomb 1-et a "{text}" kártyánál'))
            ui.button(icon='delete', on_click=lambda: ui.notify(f'Megnyomtad a Gomb 2-t a "{text}" kártyánál'))

        with ui.context_menu():
            ui.menu_item('Copy')
            ui.menu_item('Edit')
            ui.menu_item('Delete')

def startup() -> None:
    @ui.page('/')
    def main_page(client: Client):
        # A háttérszín beállítása az egész oldalra
        client.layout.style('background-color: #fce1b6') # Homokszínű árnyalat

        # Funkció a beviteli mező tartalmának beküldésére
        def submit() -> None:
            ui.notify(f'Beküldött szöveg: {text_input.value}')
            text_input.set_value('') # A mező ürítése beküldés után
            text_input.run_method('blur') # Fókusz elvétele a beviteli mezőről

        # --- Fix Fejléc Szekció ---
        # Ez a fejléc mindig az oldal tetején marad görgetéskor
        with ui.header().classes('q-py-sm').style('background-color: transparent; backdrop-filter: blur(10px); box-shadow: 0px 8px 20px 0px rgba(0,0,0,0.3);'): #('background: linear-gradient(180deg,rgba(138, 107, 77, 1) 0%, rgba(210, 181, 143, 1) 50%, rgba(252, 225, 182, 0.2) 100%);'): # Árnyék, fehér háttér, függőleges padding
            # A fejléc tartalma, ami középen van és a maximális szélességhez igazodik
            # A 'q-mx-auto max-w-screen-md q-px-md' biztosítja, hogy a fejléc tartalma
            # (input és gomb) szélességben megegyezzen a fő tartalommal alatta, és középen legyen.
            with ui.row().classes('w-full no-wrap items-center q-mx-auto max-w-screen-md q-px-md'):
                text_input = ui.input(placeholder='Link') \
                    .on('keydown.enter', submit) \
                    .props('rounded outlined bg-color=white clearable') \
                    .classes('flex-grow text-lg')
                
                search_button = ui.button(icon='arrow_forward', on_click=submit, color='#FEF3E2') \
                    .props('round') \
                    .classes('h-12 w-12 flex-none q-ml-sm') \
                    .style('color: black;')
        # --- Fix Fejléc Szekció Vége ---

        # Fő Tartalmi Terület (görgethető)
        # Ez az oszlop most a fix fejléc alatt helyezkedik el.
        # A 'q-mx-auto max-w-screen-md q-pa-md w-full' továbbra is gondoskodik a
        # horizontális középre igazításról és a maximális szélességről.
        with ui.column().classes('q-mx-auto max-w-screen-md q-pa-md w-full'):
            # A korábbi elválasztó vonal már nem szükséges, mivel a fejléc önmagában
            # is elválasztást biztosít.

            # Példa kártyák - hozzáadtam még néhányat a görgetés teszteléséhez
            create_card('Ez az első kártya tartalma.')
            create_card('Második kártya, kicsit hosszabb szöveggel, hogy lássuk, hogyan viselkedik.')
            create_card('És itt a harmadik kártya.')
            create_card('Negyedik kártya. Ez már segít a görgetés tesztelésében.')
            create_card('Ötödik kártya.')
            create_card('Hatodik kártya.')
            create_card('Hetedik kártya.')
            create_card('Nyolcadik kártya.')
            create_card('Kilencedik kártya.')
            create_card('Tizedik kártya. Remélhetőleg már görgethető az oldal!')

        with ui.page_sticky(x_offset=18, y_offset=18).style('z-index:99;'):
            ui.button(icon='settings', on_click=lambda: ui.notify('Meow?'), color="#FEF3E2") \
                .props('fab') \
                .style('color: black;')