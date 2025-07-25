from nicegui import ui
import random

class Card:
    def __init__(self, card_container, text: str, card_id: int = None, disable: bool = True, top: bool = True):
        self.card_container = card_container
        self.card_id = card_id
        self.text = text
        self.disable = disable
        self.top = top

        self.card_element = None
        self.card_label = None
        self.buttons = {
            'content_copy': None,
            'edit': None,
            'delete': None
        }
        self.progressbar = None
        self.progressbarText = 'Downloading'

        self.create()

    def create(self):
        """
        Létrehoz egy új kártyát a megadott szöveggel és opcionális azonosítóval.
        Ha van azonosító, az a kártya és a benne lévő címke HTML ID-jeként is beállítódik.
        """
        with self.card_container:
            with ui.card().classes('w-full').style('box-shadow: 0px 0px 4px 3px rgba(0,0,0,0.2);') as card_element:
                self.card_element = card_element
                if self.card_id:
                    card_element.props(f'id={self.card_id}')
                    self.card_id = self.card_id

                # A címke létrehozása, opcionálisan ID-vel
                self.card_label = ui.label(self.text).classes('text-lg font-semibold').props(f'id=label-{self.card_id}' if self.card_id else '')

                # Gombok a kártyán
                with ui.row().classes('w-full justify-end no-wrap').style('align-items: center;'):
                    def format_main_seq_progress(progress: float | None) -> str:
                        if progress is None:
                            return ""
                        return f"{self.progressbarText} - {progress:.1%}"

                    self.progressbar = ui.linear_progress(show_value=False, size="35px", value=random.uniform(0, 1)).props("rounded")
                    with self.progressbar:
                        progressbarLabel = ui.label().classes("absolute-center text-sm text-black").style('margin-top: 1px; font-weight: 500;')
                        progressbarLabel.bind_text_from(self.progressbar, "value", backward=lambda p: format_main_seq_progress(p))
                    
                    # Példa a progress bar frissítésére
                    def test():
                        self.progressbarText = 'Transcribe' if random.choice([True, False]) else 'Downloading'
                        self.progressbar.set_value(random.uniform(0, 1))
                    ui.timer(random.randint(1,5), test)

                    self.buttons['content_copy'] = ui.button(icon='content_copy', on_click=lambda: ui.notify(f'Megnyomtad a Másolás gombot a "{self.text}" kártyánál'))
                    self.buttons['edit'] = ui.button(icon='edit', on_click=lambda: ui.notify(f'Megnyomtad a Szerkesztés gombot a "{self.text}" kártyánál'))
                    self.buttons['delete'] = ui.button(icon='delete', on_click=lambda: ui.notify(f'Megnyomtad a Törlés gombot a "{self.text}" kártyánál'))

                # Kontextus menü a kártyán
                with ui.context_menu():
                    ui.menu_item('Copy')
                    ui.menu_item('Edit')
                    ui.menu_item('Delete')

        if self.disable:
            self.buttons['content_copy'].disable()
            self.buttons['edit'].disable()
            self.buttons['delete'].disable()
        if self.top: card_element.move(target_index=0)