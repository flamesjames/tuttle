from typing import Callable, Mapping, Optional

from flet import (
    AlertDialog,
    Card,
    Column,
    Container,
    GridView,
    Icon,
    ListTile,
    ResponsiveRow,
    Row,
    Text,
    UserControl,
    border_radius,
    icons,
    padding,
)

from clients.intent import ClientsIntent
from core import utils, views
from core.abstractions import DialogHandler, TuttleView, TuttleViewParams
from core.intent_result import IntentResult
from res import colors, dimens, fonts, res_utils

from tuttle.model import Address, Client, Contact


class ClientCard(UserControl):
    """Formats a single client info into a card ui display"""

    def __init__(
        self,
        client: Client,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
    ):
        super().__init__()
        self.client = client
        self.client_info_container = Column(spacing=0, run_spacing=0)
        self.on_edit_clicked = on_edit
        self.on_delete_clicked = on_delete

    def build(self):
        if self.client.invoicing_contact:
            invoicing_contact_info = self.client.invoicing_contact.print_address()
        else:
            invoicing_contact_info = "*not specified"
        editable = True if self.on_edit_clicked or self.on_delete_clicked else None

        editor_controls = (
            views.context_pop_up_menu(
                on_click_delete=lambda e: self.on_delete_clicked(self.client),
                on_click_edit=lambda e: self.on_edit_clicked(self.client),
            )
            if editable
            else views.smSpace
        )

        self.client_info_container.controls = [
            ListTile(
                leading=Icon(
                    utils.TuttleComponentIcons.client_icon,
                    size=dimens.ICON_SIZE,
                ),
                title=views.get_body_txt(self.client.name),
                trailing=editor_controls,
            ),
            views.mdSpace,
            ResponsiveRow(
                controls=[
                    views.get_body_txt(
                        txt="Invoicing Contact",
                        color=colors.GRAY_COLOR,
                        size=fonts.BODY_2_SIZE,
                        col={"xs": "12"},
                    ),
                    views.get_body_txt(
                        txt=invoicing_contact_info,
                        size=fonts.BODY_2_SIZE,
                        col={"xs": "12"},
                    ),
                ],
                spacing=dimens.SPACE_XS,
                run_spacing=0,
                vertical_alignment=utils.CENTER_ALIGNMENT,
            ),
        ]

        card = Card(
            elevation=2,
            expand=True,
            content=Container(
                expand=True,
                padding=padding.all(dimens.SPACE_STD),
                border_radius=border_radius.all(12),
                content=self.client_info_container,
            ),
        )
        return card


class ClientViewPopUp(DialogHandler, UserControl):
    """Pop up used to displaying a client"""

    def __init__(
        self,
        dialog_controller: Callable[[any, utils.AlertDialogControls], None],
        client: Client,
    ):
        # dimensions of the pop up and the elements inside
        # accounting for margins and paddings

        pop_up_width = int(dimens.MIN_WINDOW_WIDTH * 0.8)

        dialog = AlertDialog(
            content=Container(
                content=Column(
                    scroll=utils.AUTO_SCROLL,
                    controls=[ClientCard(client=client)],
                ),
                width=pop_up_width,
            ),
        )
        super().__init__(dialog=dialog, dialog_controller=dialog_controller)


class ClientEditorPopUp(DialogHandler, UserControl):
    """Pop up used for editing a client"""

    def __init__(
        self,
        dialog_controller: Callable[[any, utils.AlertDialogControls], None],
        on_submit: Callable,
        contacts_map: Mapping[int, Contact],
        client: Optional[Client] = None,
    ):
        # dimensions of the pop up and the elements inside
        # accounting for margins and paddings
        pop_up_height = dimens.MIN_WINDOW_HEIGHT
        pop_up_width = int(dimens.MIN_WINDOW_WIDTH * 0.8)
        half_of_pop_up_width = int(dimens.MIN_WINDOW_WIDTH * 0.35)

        self.client = client if client is not None else Client()
        self.invoicing_contact = (
            self.client.invoicing_contact
            if self.client.invoicing_contact is not None
            else Contact()
        )
        self.address = (
            self.invoicing_contact.address
            if self.invoicing_contact.address is not None
            else Address()
        )
        if not self.invoicing_contact.address:
            self.invoicing_contact.address = self.address
        self.contacts_as_map = contacts_map
        self.contact_options = self.get_contacts_as_list()

        title = "Edit Client" if client is not None else "New Client"

        initial_selected_contact = self.get_contact_dropdown_item(
            self.invoicing_contact.id
        )

        self.first_name_field = views.get_std_txt_field(
            on_change=self.on_fname_changed,
            label="First Name",
            hint=self.invoicing_contact.first_name,
            initial_value=self.invoicing_contact.first_name,
        )

        self.last_name_field = views.get_std_txt_field(
            on_change=self.on_lname_changed,
            label="Last Name",
            hint=self.invoicing_contact.last_name,
            initial_value=self.invoicing_contact.last_name,
        )
        self.company_field = views.get_std_txt_field(
            on_change=self.on_company_changed,
            label="Company",
            hint=self.invoicing_contact.company,
            initial_value=self.invoicing_contact.company,
        )
        self.email_field = views.get_std_txt_field(
            on_change=self.on_email_changed,
            label="Email",
            hint=self.invoicing_contact.email,
            initial_value=self.invoicing_contact.email,
        )

        self.street_field = views.get_std_txt_field(
            on_change=self.on_street_changed,
            label="Street",
            hint=self.invoicing_contact.address.street,
            initial_value=self.invoicing_contact.address.street,
            width=half_of_pop_up_width,
        )
        self.street_num_field = views.get_std_txt_field(
            on_change=self.on_street_num_changed,
            label="Street No.",
            hint=self.invoicing_contact.address.number,
            initial_value=self.invoicing_contact.address.number,
            width=half_of_pop_up_width,
        )
        self.postal_code_field = views.get_std_txt_field(
            on_change=self.on_postal_code_changed,
            label="Postal code",
            hint=self.invoicing_contact.address.postal_code,
            initial_value=self.invoicing_contact.address.postal_code,
            width=half_of_pop_up_width,
        )
        self.city_field = views.get_std_txt_field(
            on_change=self.on_city_changed,
            label="City",
            hint=self.invoicing_contact.address.city,
            initial_value=self.invoicing_contact.address.city,
            width=half_of_pop_up_width,
        )
        self.country_field = views.get_std_txt_field(
            on_change=self.on_country_changed,
            label="Country",
            hint=self.invoicing_contact.address.country,
            initial_value=self.invoicing_contact.address.country,
        )

        dialog = AlertDialog(
            content=Container(
                height=pop_up_height,
                content=Column(
                    scroll=utils.AUTO_SCROLL,
                    controls=[
                        views.get_heading(title=title, size=fonts.HEADLINE_4_SIZE),
                        views.xsSpace,
                        views.get_std_txt_field(
                            on_change=self.on_client_name_changed,
                            label="Client's name",
                            hint=self.client.name,
                            initial_value=self.client.name,
                        ),
                        views.xsSpace,
                        views.get_heading(
                            title="Invoicing Contact",
                            size=fonts.SUBTITLE_2_SIZE,
                            color=colors.GRAY_COLOR,
                        ),
                        views.xsSpace,
                        views.get_dropdown(
                            on_change=self.on_contact_selected,
                            label="Select contact",
                            items=self.contact_options,
                            initial_value=initial_selected_contact,
                        ),
                        views.xsSpace,
                        self.first_name_field,
                        self.last_name_field,
                        self.company_field,
                        self.email_field,
                        Row(
                            vertical_alignment=utils.CENTER_ALIGNMENT,
                            controls=[self.street_field, self.street_num_field],
                        ),
                        Row(
                            vertical_alignment=utils.CENTER_ALIGNMENT,
                            controls=[
                                self.postal_code_field,
                                self.city_field,
                            ],
                        ),
                        self.country_field,
                        views.xsSpace,
                    ],
                ),
                width=pop_up_width,
            ),
            actions=[
                views.get_primary_btn(
                    label="Done", on_click=self.on_submit_btn_clicked
                ),
            ],
        )
        super().__init__(dialog=dialog, dialog_controller=dialog_controller)
        self.title = ""
        self.fname = ""
        self.lname = ""
        self.company = ""
        self.email = ""
        self.street = ""
        self.street_num = ""
        self.postal_code = ""
        self.city = ""
        self.country = ""
        self.on_submit = on_submit

    def get_contacts_as_list(self):
        """transforms a map of id-contact_name to a list for dropdown options"""
        contacts_list = []
        for key in self.contacts_as_map:
            item = self.get_contact_dropdown_item(key)
            if item:
                contacts_list.append(item)
        return contacts_list

    def get_contact_dropdown_item(self, key):
        if key is not None and key in self.contacts_as_map:
            return f"#{key} {self.contacts_as_map[key].name}"
        return ""

    def on_contact_selected(self, e):
        # parse selected value to extract id
        selected = e.control.value
        id = ""
        for c in selected:
            if c == "#":
                continue
            if c == " ":
                break
            id = id + c
        if int(id) in self.contacts_as_map:
            self.invoicing_contact: Contact = self.contacts_as_map[int(id)]
            self.set_invoicing_contact_fields()

    def set_invoicing_contact_fields(self):
        self.first_name_field.value = self.invoicing_contact.first_name
        self.last_name_field.value = self.invoicing_contact.last_name
        self.company_field.value = self.invoicing_contact.company
        self.email_field.value = self.invoicing_contact.email
        self.street_field.value = self.invoicing_contact.address.street
        self.street_num_field.value = self.invoicing_contact.address.number
        self.postal_code_field.value = self.invoicing_contact.address.postal_code
        self.city_field.value = self.invoicing_contact.address.city
        self.country_field.value = self.invoicing_contact.address.country
        self.dialog.update()

    def on_client_name_changed(self, e):
        self.title = e.control.value

    def on_fname_changed(self, e):
        self.fname = e.control.value

    def on_lname_changed(self, e):
        self.lname = e.control.value

    def on_company_changed(self, e):
        self.company = e.control.value

    def on_email_changed(self, e):
        self.email = e.control.value

    def on_street_changed(self, e):
        self.street = e.control.value

    def on_street_num_changed(self, e):
        self.street_num = e.control.value

    def on_postal_code_changed(self, e):
        self.postal_code = e.control.value

    def on_city_changed(self, e):
        self.city = e.control.value

    def on_country_changed(self, e):
        self.country = e.control.value

    def on_submit_btn_clicked(self, e):
        self.client.name = (
            self.title.strip() if self.title.strip() else self.client.name
        )
        self.invoicing_contact.first_name = (
            self.fname.strip()
            if self.fname.strip()
            else self.invoicing_contact.first_name
        )
        self.invoicing_contact.last_name = (
            self.lname.strip()
            if self.lname.strip()
            else self.invoicing_contact.last_name
        )
        self.invoicing_contact.company = (
            self.company.strip()
            if self.company.strip()
            else self.invoicing_contact.company
        )
        self.invoicing_contact.email = (
            self.email.strip() if self.email.strip() else self.invoicing_contact.email
        )
        self.address.street = (
            self.street.strip()
            if self.street.strip()
            else self.invoicing_contact.address.street
        )

        self.address.number = (
            self.street_num.strip()
            if self.street_num.strip()
            else self.invoicing_contact.address.number
        )
        self.address.postal_code = (
            self.postal_code.strip()
            if self.postal_code.strip()
            else self.invoicing_contact.address.postal_code
        )
        self.address.city = (
            self.city.strip()
            if self.city.strip()
            else self.invoicing_contact.address.city
        )
        self.address.country = (
            self.country.strip()
            if self.country.strip()
            else self.invoicing_contact.address.country
        )
        self.invoicing_contact.address = self.address
        self.client.invoicing_contact = self.invoicing_contact
        self.close_dialog()
        self.on_submit(self.client)

    def build(self):
        return self.dialog


class ClientsListView(TuttleView, UserControl):
    def __init__(self, params: TuttleViewParams):
        super().__init__(params=params)
        self.intent = ClientsIntent()
        self.loading_indicator = views.horizontal_progress
        self.no_clients_control = views.get_body_txt(
            txt="You have not added any clients yet.",
            color=colors.ERROR_COLOR,
            show=False,
        )
        self.title_control = ResponsiveRow(
            controls=[
                Column(
                    col={"xs": 12},
                    controls=[
                        views.get_heading(
                            title="My Clients", size=fonts.HEADLINE_4_SIZE
                        ),
                        self.loading_indicator,
                        self.no_clients_control,
                    ],
                )
            ]
        )
        self.clients_container = GridView(
            expand=False,
            max_extent=540,
            child_aspect_ratio=1.0,
            spacing=dimens.SPACE_STD,
            run_spacing=dimens.SPACE_MD,
        )
        self.clients_to_display = {}
        self.contacts = {}
        self.editor = None

    def parent_intent_listener(self, intent: str, data: any):
        if intent == res_utils.ADD_CLIENT_INTENT:
            if self.editor is not None:
                self.editor.close_dialog()
            self.editor = ClientEditorPopUp(
                self.dialog_controller,
                on_submit=self.on_save_client,
                contacts_map=self.contacts,
            )
            self.editor.open_dialog()
        return

    def load_all_clients(self):
        self.clients_to_display = self.intent.get_all_clients_as_map()

    def load_all_contacts(self):
        self.contacts = self.intent.get_all_contacts_as_map()

    def refresh_clients(self):
        self.clients_container.controls.clear()
        for key in self.clients_to_display:
            client = self.clients_to_display[key]
            clientCard = ClientCard(
                client=client,
                on_edit=self.on_edit_client_clicked,
                on_delete=self.on_delete_client_clicked,
            )
            self.clients_container.controls.append(clientCard)

    def on_edit_client_clicked(self, client: Client):
        if self.editor is not None:
            self.editor.close_dialog()
        self.editor = ClientEditorPopUp(
            self.dialog_controller,
            on_submit=self.on_save_client,
            contacts_map=self.contacts,
            client=client,
        )
        self.editor.open_dialog()

    def on_delete_client_clicked(self, client: Client):
        if self.editor is not None:
            self.editor.close_dialog()
        self.editor = views.ConfirmDisplayPopUp(
            dialog_controller=self.dialog_controller,
            title="Are You Sure?",
            description=f"Are you sure you wish to delete this client's info?\n{client.name}",
            on_proceed=self.on_delete_confirmed,
            proceed_button_label="Yes! Delete",
            data_on_confirmed=client.id,
        )
        self.editor.open_dialog()

    def on_delete_confirmed(self, client_id):
        self.loading_indicator.visible = True
        self.update_self()
        result = self.intent.delete_client_by_id(client_id)
        is_error = not result.was_intent_successful
        msg = result.error_msg if is_error else "Client deleted!"
        self.show_snack(msg, is_error)
        if not is_error and client_id in self.clients_to_display:
            del self.clients_to_display[client_id]
            self.refresh_clients()
        self.loading_indicator.visible = False
        self.update_self()

    def on_save_client(self, client_to_save: Client):
        is_updating = client_to_save.id is not None
        self.loading_indicator.visible = True
        self.update_self()
        result: IntentResult = self.intent.save_client(client_to_save)
        if not result.was_intent_successful:
            self.show_snack(result.error_msg, True)
        else:
            self.clients_to_display[result.data.id] = result.data
            self.refresh_clients()
            msg = (
                "The client's info has been updated"
                if is_updating
                else "A new client has been added"
            )
            self.show_snack(msg, False)
        self.loading_indicator.visible = False
        self.update_self()

    def show_no_clients(self):
        self.no_clients_control.visible = True

    def did_mount(self):
        self.mounted = True
        self.loading_indicator.visible = True
        self.load_all_clients()
        count = len(self.clients_to_display)
        self.loading_indicator.visible = False
        if count == 0:
            self.show_no_clients()
        else:
            self.refresh_clients()
        self.load_all_contacts()
        self.update_self()

    def build(self):
        view = Column(
            controls=[
                self.title_control,
                views.mdSpace,
                Container(self.clients_container, expand=True),
            ],
        )
        return view

    def will_unmount(self):
        self.mounted = False
        if self.editor:
            self.editor.dimiss_open_dialogs()