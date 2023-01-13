from enum import Enum
from typing import Callable, Optional
from clients.view import ClientEditorPopUp
import flet
from contracts.intent import ContractsIntent
from core.abstractions import TuttleView, DialogHandler, TuttleViewParams
from res import colors, dimens, fonts, res_utils
from contracts.intent import ContractsIntent
from core import utils, views
from core.intent_result import IntentResult
from core.models import (
    get_cycle_from_value,
    get_cycle_values_as_list,
    get_time_unit_values_as_list,
)
from tuttle.model import (
    Contract,
    Client,
)

LABEL_WIDTH = 80


class ContractCard(flet.UserControl):
    """Formats a single contract info into a flet.Card ui display"""

    def __init__(
        self, contract: Contract, on_click_view, on_click_edit, on_click_delete
    ):
        super().__init__()
        self.contract = contract
        self.product_info_container = flet.Column()
        self.on_click_view = on_click_view
        self.on_click_edit = on_click_edit
        self.on_click_delete = on_click_delete

    def build(self):
        self.product_info_container.controls = [
            views.get_headline_txt(txt=self.contract.title, size=fonts.SUBTITLE_1_SIZE),
            flet.ResponsiveRow(
                controls=[
                    flet.Text(
                        "Billing Cycle",
                        color=colors.GRAY_COLOR,
                        size=fonts.BODY_2_SIZE,
                        col={"xs": "12", "sm": "5", "md": "3"},
                    ),
                    flet.Text(
                        self.contract.billing_cycle,
                        size=fonts.BODY_2_SIZE,
                        col={"xs": "12", "sm": "7", "md": "9"},
                    ),
                ],
                spacing=dimens.SPACE_XS,
                run_spacing=0,
                vertical_alignment=utils.CENTER_ALIGNMENT,
            ),
            flet.ResponsiveRow(
                controls=[
                    flet.Text(
                        "Start date",
                        color=colors.GRAY_COLOR,
                        size=fonts.BODY_2_SIZE,
                        col={"xs": "12", "sm": "5", "md": "3"},
                    ),
                    flet.Text(
                        self.contract.start_date.strftime("%d/%m/%Y")
                        if self.contract.start_date
                        else "",
                        size=fonts.BODY_2_SIZE,
                        col={"xs": "12", "sm": "7", "md": "9"},
                    ),
                ],
                spacing=dimens.SPACE_XS,
                run_spacing=0,
                vertical_alignment=utils.CENTER_ALIGNMENT,
            ),
            flet.ResponsiveRow(
                controls=[
                    flet.Text(
                        "End date",
                        color=colors.GRAY_COLOR,
                        size=fonts.BODY_2_SIZE,
                        col={"xs": "12", "sm": "5", "md": "3"},
                    ),
                    flet.Text(
                        self.contract.end_date.strftime("%d/%m/%Y")
                        if self.contract.end_date
                        else "",
                        size=fonts.BODY_2_SIZE,
                        color=colors.ERROR_COLOR,
                        col={"xs": "12", "sm": "7", "md": "9"},
                    ),
                ],
                spacing=dimens.SPACE_XS,
                run_spacing=0,
                vertical_alignment=utils.CENTER_ALIGNMENT,
            ),
            views.view_edit_delete_pop_up(
                on_click_view=lambda e: self.on_click_view(self.contract.id),
                on_click_edit=lambda e: self.on_click_edit(self.contract.id),
                on_click_delete=lambda e: self.on_click_delete(self.contract.id),
            ),
        ]
        return flet.Card(
            elevation=2,
            expand=True,
            content=flet.Container(
                expand=True,
                padding=flet.padding.all(dimens.SPACE_STD),
                border_radius=flet.border_radius.all(12),
                content=self.product_info_container,
            ),
        )


class ContractEditorScreen(TuttleView, flet.UserControl):
    def __init__(
        self,
        params: TuttleViewParams,
        contract_id: str,
    ):
        super().__init__(
            params,
        )
        self.horizontal_alignment_in_parent = utils.CENTER_ALIGNMENT
        self.intent_handler = ContractsIntent()

        self.loading_indicator = views.horizontal_progress
        self.new_client_pop_up = None

        # info of contract being edited / created
        self.contract_id = contract_id
        self.contract_to_edit: Optional[Contract] = None
        self.clients_map = {}
        self.contacts_map = {}
        self.title = ""
        self.selected_client = None
        self.rate = ""
        self.currency = ""
        self.vat_rate = ""
        self.time_unit = None
        self.unit_PW = ""
        self.volume = ""
        self.term_of_payment = ""
        self.billing_cycle = None

    def on_title_changed(self, e):
        self.title = e.control.value

    def on_rate_changed(self, e):
        self.rate = e.control.value

    def on_currency_changed(self, e):
        self.currency = e.control.value

    def on_volume_changed(self, e):
        self.volume = e.control.value

    def on_top_changed(self, e):
        self.term_of_payment = e.control.value

    def on_upw_changed(self, e):
        self.unit_PW = e.control.value

    def on_vat_rate_changed(self, e):
        self.vat_rate = e.control.value

    def on_unit_selected(self, e):
        self.time_unit = e.control.value

    def on_billing_cycle_selected(self, e):
        self.billing_cycle = get_cycle_from_value(e.control.value)

    def clear_title_error(self, e):
        if self.title_field.error_text:
            self.title_field.error_text = None
            if self.mounted:
                self.update()

    def clear_rate_error(self, e):
        if self.rate_field.error_text:
            self.rate_field.error_text = None
            if self.mounted:
                self.update()

    def clear_currency_error(self, e):
        if self.currency_field.error_text:
            self.currency_field.error_text = None
            if self.mounted:
                self.update()

    def clear_volume_error(self, e):
        if self.volume_field.error_text:
            self.volume_field.error_text = None
            if self.mounted:
                self.update()

    def clear_top_error(self, e):
        if self.termOfPayment_field.error_text:
            self.termOfPayment_field.error_text = None
            if self.mounted:
                self.update()

    def clear_upw_error(self, e):
        if self.unitPW_field.error_text:
            self.unitPW_field.error_text = None
            if self.mounted:
                self.update()

    def clear_vat_rate_error(self, e):
        if self.vatRate_field.error_text:
            self.vatRate_field.error_text = None
            if self.mounted:
                self.update()

    def show_progress_bar_disable_action(self):
        self.loading_indicator.visible = True
        self.submit_btn.disabled = True

    def enable_action_remove_progress_bar(self):
        self.loading_indicator.visible = False
        self.submit_btn.disabled = False

    def did_mount(self):
        self.mounted = True
        self.show_progress_bar_disable_action()
        self.load_contract()
        self.load_clients()
        self.load_contacts()
        self.enable_action_remove_progress_bar()
        if self.mounted:
            self.update()

    """ LOADING DATA """

    def load_contract(
        self,
    ):
        if self.contract_id is None:
            return
        result = self.intent_handler.get_contract_by_id(self.contract_id)
        if result.was_intent_successful:
            self.contract_to_edit = result.data
        else:
            self.show_snack(
                "Failed to load the contract! Please go back and retry", True
            )

    def load_clients(self):
        self.clients_map = self.intent_handler.get_all_clients_as_map()
        self.clients_field.error_text = (
            "Please create a new client" if len(self.clients_map) == 0 else None
        )
        views.update_dropdown_items(self.clients_field, self.get_clients_as_list())

    def load_contacts(self):
        self.contacts_map = self.intent_handler.get_all_contacts_as_map()

    def get_clients_as_list(self):
        """transforms a map of id-client_title to a list for dropdown options"""
        clients = []
        for key in self.clients_map:
            clients.append(self.get_client_dropdown_item(key))
        return clients

    def get_client_dropdown_item(self, key):
        return f"#{key} {self.clients_map[key].title}"

    def on_client_selected(self, e):
        # parse selected value to extract id
        selected = e.control.value
        id = ""
        for c in selected:
            if c == "#":
                continue
            if c == " ":
                break
            id = id + c

        if self.clients_field.error_text:
            self.clients_field.error_text = None
            if self.mounted:
                self.update()
        if int(id) in self.clients_map:
            self.selected_client = self.clients_map[int(id)]

    """ CLIENT POP UP """

    def on_add_client_clicked(self, e):
        if self.new_client_pop_up:
            self.new_client_pop_up.close_dialog()

        self.new_client_pop_up = ClientEditorPopUp(
            dialog_controller=self.dialog_controller,
            on_submit=self.on_client_set_from_pop_up,
            contacts_map=self.contacts_map,
        )
        self.new_client_pop_up.open_dialog()

    def on_client_set_from_pop_up(self, client):
        if client:
            result: IntentResult = self.intent_handler.save_client(client)
            if result.was_intent_successful:
                self.selected_client: Client = result.data
                self.clients_map[self.selected_client.id] = self.selected_client
                views.update_dropdown_items(
                    self.clients_field, self.get_clients_as_list()
                )
                item = self.get_client_dropdown_item(self.selected_client.id)
                self.clients_field.value = item
            else:
                self.show_snack(result.error_msg, True)
        if self.mounted:
            self.update()

    """ SAVING """

    def on_save(self, e):
        if not self.title:
            self.title_field.error_text = "Contract title is required"
            self.update()
            return

        if self.selected_client is None:
            self.clients_field.error_text = "Please select a client"
            self.update()
            return

        signatureDate = self.signatureDate_field.get_date()
        if signatureDate is None:
            self.show_snack("Please specify the signature date", True)
            return

        startDate = self.startDate_field.get_date()
        if startDate is None:
            self.show_snack("Please specify the start date", True)
            return

        endDate = self.endDate_field.get_date()
        if endDate is None:
            self.show_snack("Please specify the end date", True)
            return

        if startDate > endDate:
            self.show_snack(
                "The end date of the contract cannot be before the start date", True
            )
            return

        self.show_progress_bar_disable_action()
        result: IntentResult = self.intent_handler.save_contract(
            title=self.title,
            signature_date=signatureDate,
            start_date=startDate,
            end_date=endDate,
            client=self.selected_client,
            rate=self.rate,
            currency=self.currency,
            VAT_rate=self.vat_rate,
            unit=self.time_unit,
            units_per_workday=self.unit_PW,
            volume=self.volume,
            term_of_payment=self.term_of_payment,
            billing_cycle=self.billing_cycle,
            contract=self.contract_to_edit,
        )
        # TODO add contract if updating
        msg = (
            "New contract created successfully"
            if result.was_intent_successful
            else result.error_msg
        )
        isError = not result.was_intent_successful
        self.enable_action_remove_progress_bar()
        self.show_snack(msg, isError)
        if not isError:
            # re route back
            self.on_navigate_back()

    def build(self):
        self.title_field = views.get_std_txt_field(
            label="Title",
            hint="Contract's title",
            on_change=self.on_title_changed,
            on_focus=self.clear_title_error,
        )

        self.rate_field = views.get_std_txt_field(
            label="Rate",
            hint="Contract's rate",
            on_change=self.on_rate_changed,
            on_focus=self.clear_rate_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )

        self.currency_field = views.get_std_txt_field(
            label="Currency",
            hint="Payment currency",
            on_change=self.on_currency_changed,
            on_focus=self.clear_currency_error,
        )

        self.vatRate_field = views.get_std_txt_field(
            label="Vat",
            hint="Vat rate",
            on_change=self.on_vat_rate_changed,
            on_focus=self.clear_vat_rate_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )

        self.unitPW_field = views.get_std_txt_field(
            label="Units per workday",
            hint="",
            on_change=self.on_upw_changed,
            on_focus=self.clear_upw_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )

        self.volume_field = views.get_std_txt_field(
            label="Volume (optional)",
            hint="",
            on_change=self.on_volume_changed,
            on_focus=self.clear_volume_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )

        self.termOfPayment_field = views.get_std_txt_field(
            label="Term of payment (optional)",
            hint="",
            on_change=self.on_top_changed,
            on_focus=self.clear_top_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )

        self.clients_field = views.get_dropdown(
            label="Client",
            on_change=self.on_client_selected,
            items=self.get_clients_as_list(),
        )
        self.units_field = views.get_dropdown(
            label="Time Unit",
            on_change=self.on_unit_selected,
            items=get_time_unit_values_as_list(),
        )

        self.billingCycle_field = views.get_dropdown(
            label="Billing Cycle",
            on_change=self.on_billing_cycle_selected,
            items=get_cycle_values_as_list(),
        )

        self.signatureDate_field = views.DateSelector(label="Signed on Date")
        self.startDate_field = views.DateSelector(label="Start Date")
        self.endDate_field = views.DateSelector(label="End Date")
        self.submit_btn = views.get_primary_btn(
            label="Create Contract", on_click=self.on_save
        )
        view = flet.Container(
            expand=True,
            padding=flet.padding.all(dimens.SPACE_MD),
            margin=flet.margin.symmetric(vertical=dimens.SPACE_MD),
            content=flet.Card(
                expand=True,
                content=flet.Container(
                    flet.Column(
                        expand=True,
                        controls=[
                            flet.Row(
                                controls=[
                                    flet.IconButton(
                                        icon=flet.icons.CHEVRON_LEFT_ROUNDED,
                                        on_click=self.on_navigate_back,
                                    ),
                                    views.get_headline_with_subtitle(
                                        title="New Contract",
                                        subtitle="Create a new contract",
                                    ),
                                ]
                            ),
                            self.loading_indicator,
                            views.mdSpace,
                            self.title_field,
                            views.smSpace,
                            self.currency_field,
                            self.rate_field,
                            self.termOfPayment_field,
                            self.unitPW_field,
                            self.vatRate_field,
                            self.volume_field,
                            views.smSpace,
                            flet.Row(
                                alignment=utils.SPACE_BETWEEN_ALIGNMENT,
                                vertical_alignment=utils.CENTER_ALIGNMENT,
                                spacing=dimens.SPACE_STD,
                                controls=[
                                    self.clients_field,
                                    flet.IconButton(
                                        icon=flet.icons.ADD_CIRCLE_OUTLINE,
                                        on_click=self.on_add_client_clicked,
                                    ),
                                ],
                            ),
                            views.smSpace,
                            self.units_field,
                            views.smSpace,
                            self.billingCycle_field,
                            views.smSpace,
                            self.signatureDate_field,
                            views.smSpace,
                            self.startDate_field,
                            views.mdSpace,
                            self.endDate_field,
                            views.mdSpace,
                            self.submit_btn,
                        ],
                    ),
                    padding=flet.padding.all(dimens.SPACE_MD),
                    width=dimens.MIN_WINDOW_WIDTH,
                ),
            ),
        )

        return view

    def will_unmount(self):
        try:
            self.mounted = False
            if self.new_client_pop_up:
                self.new_client_pop_up.dimiss_open_dialogs()
        except Exception as e:
            print(e)


class ContractStates(Enum):
    ALL = 1
    ACTIVE = 2
    COMPLETED = 3
    UPCOMING = 4


class ContractFiltersView(flet.UserControl):
    """Create and Handles contracts view filtering buttons"""

    def __init__(self, onStateChanged: Callable[[ContractStates], None]):
        super().__init__()
        self.currentState = ContractStates.ALL
        self.stateTofilterButtonsMap = {}
        self.onStateChangedCallback = onStateChanged

    def filter_button(
        self,
        state: ContractStates,
        label: str,
        onClick: Callable[[ContractStates], None],
    ):
        button = flet.ElevatedButton(
            text=label,
            col={"xs": 6, "sm": 3, "lg": 2},
            on_click=lambda e: onClick(state),
            height=dimens.CLICKABLE_PILL_HEIGHT,
            color=colors.PRIMARY_COLOR
            if state == self.currentState
            else colors.GRAY_COLOR,
            style=flet.ButtonStyle(
                elevation={
                    utils.PRESSED: 3,
                    utils.SELECTED: 3,
                    utils.HOVERED: 4,
                    utils.OTHER_CONTROL_STATES: 2,
                },
            ),
        )
        return button

    def on_filter_button_clicked(self, state: ContractStates):
        """sets the new state and updates selected button"""
        self.stateTofilterButtonsMap[self.currentState].color = colors.GRAY_COLOR
        self.currentState = state
        self.stateTofilterButtonsMap[self.currentState].color = colors.PRIMARY_COLOR
        self.update()
        self.onStateChangedCallback(state)

    def get_filter_button_label(self, state: ContractStates):
        if state.value == ContractStates.ACTIVE.value:
            return "Active"
        elif state.value == ContractStates.UPCOMING.value:
            return "Upcoming"
        elif state.value == ContractStates.COMPLETED.value:
            return "Completed"
        else:
            return "All"

    def set_filter_buttons(self):
        for state in ContractStates:
            button = self.filter_button(
                label=self.get_filter_button_label(state),
                state=state,
                onClick=self.on_filter_button_clicked,
            )
            self.stateTofilterButtonsMap[state] = button

    def build(self):
        if len(self.stateTofilterButtonsMap) == 0:
            # set the buttons
            self.set_filter_buttons()

        self.filters = flet.ResponsiveRow(
            controls=list(self.stateTofilterButtonsMap.values())
        )
        return self.filters


class CreateContractScreen(TuttleView, flet.UserControl):
    def __init__(self, params):
        super().__init__(params=params)
        self.horizontal_alignment_in_parent = utils.CENTER_ALIGNMENT
        self.intent_handler = ContractsIntent()

        self.loading_indicator = views.horizontal_progress
        self.new_client_pop_up: Optional[DialogHandler] = None

        # info of contract being edited / created
        self.clients_map = {}
        self.contacts_map = {}
        self.title = ""
        self.client = None
        self.rate = ""
        self.currency = ""
        self.vat_rate = ""
        self.time_unit = None
        self.unit_pw = ""
        self.volume = ""
        self.term_of_payment = ""
        self.billing_cycle = None

    def on_title_changed(self, e):
        self.title = e.control.value

    def on_rate_changed(self, e):
        self.rate = e.control.value

    def on_currency_changed(self, e):
        self.currency = e.control.value

    def on_volume_changed(self, e):
        self.volume = e.control.value

    def on_top_changed(self, e):
        self.term_of_payment = e.control.value

    def on_upw_changed(self, e):
        self.unit_pw = e.control.value

    def on_vat_rate_changed(self, e):
        self.vat_rate = e.control.value

    def on_unit_selected(self, e):
        self.time_unit = e.control.value

    def on_billing_cycle_selected(self, e):
        self.billing_cycle = get_cycle_from_value(e.control.value)

    def clear_title_error(self, e):
        if self.title_field.error_text:
            self.title_field.error_text = None
            self.update()

    def clear_rate_error(self, e):
        if self.rate_field.error_text:
            self.rate_field.error_text = None
            self.update()

    def clear_currency_error(self, e):
        if self.currency_field.error_text:
            self.currency_field.error_text = None
            self.update()

    def clear_volume_error(self, e):
        if self.volume_field.error_text:
            self.volume_field.error_text = None
            self.update()

    def clear_top_error(self, e):
        if self.term_of_payment_field.error_text:
            self.term_of_payment_field.error_text = None
            self.update()

    def clear_upw_error(self, e):
        if self.unit_PW_field.error_text:
            self.unit_PW_field.error_text = None
            self.update()

    def clear_vat_rate_error(self, e):
        if self.vat_rate_field.error_text:
            self.vat_rate_field.error_text = None
            self.update()

    def show_progress_bar_disable_action(self):
        self.loading_indicator.visible = True
        self.submit_btn.disabled = True

    def enable_action_remove_progress_bar(self):
        self.loading_indicator.visible = False
        self.submit_btn.disabled = False

    def did_mount(self):
        self.mounted = True
        self.show_progress_bar_disable_action()
        self.load_clients()
        self.load_contacts()
        self.enable_action_remove_progress_bar()
        if self.mounted:
            self.update()

    def load_clients(self):
        self.clients_map = self.intent_handler.get_all_clients_as_map()
        self.clients_field.error_text = (
            "Please create a new client" if len(self.clients_map) == 0 else None
        )
        views.update_dropdown_items(self.clients_field, self.get_clients_as_list())

    def load_contacts(self):
        self.contacts_map = self.intent_handler.get_all_contacts_as_map()

    def get_clients_as_list(self):
        """transforms a map of id-client_title to a list for dropdown options"""
        clients = []
        for key in self.clients_map:
            clients.append(self.get_client_dropdown_item(key))
        return clients

    def get_client_dropdown_item(self, key):
        return f"#{key} {self.clients_map[key].name}"

    def on_client_selected(self, e):
        # parse selected value to extract id
        selected = e.control.value
        id = ""
        for c in selected:
            if c == "#":
                continue
            if c == " ":
                break
            id = id + c

        if self.clients_field.error_text:
            self.clients_field.error_text = None
            self.update()
        if int(id) in self.clients_map:
            self.client = self.clients_map[int(id)]

    """ CLIENT POP UP """

    def on_add_client_clicked(self, e):
        if self.new_client_pop_up:
            self.new_client_pop_up.close_dialog()

        self.new_client_pop_up = ClientEditorPopUp(
            dialog_controller=self.dialog_controller,
            on_submit=self.on_client_set_from_pop_up,
            contacts_map=self.contacts_map,
        )
        self.new_client_pop_up.open_dialog()

    def on_client_set_from_pop_up(self, client):
        if client:
            result: IntentResult = self.intent_handler.save_client(client)
            if result.was_intent_successful:
                self.client: Client = result.data
                self.clients_map[self.client.id] = self.client
                views.update_dropdown_items(
                    self.clients_field, self.get_clients_as_list()
                )
                item = self.get_client_dropdown_item(self.client.id)
                self.clients_field.value = item
            else:
                self.show_snack(result.error_msg, True)
            if self.mounted:
                self.update()

    """ SAVING """

    def on_save(self, e):
        if not self.title:
            self.title_field.error_text = "Contract title is required"
            self.update()
            return

        if self.client is None:
            self.clients_field.error_text = "Please select a client"
            self.update()
            return

        signatureDate = self.signature_date_field.get_date()
        if signatureDate is None:
            self.show_snack("Please specify the signature date", True)
            return

        startDate = self.start_date_field.get_date()
        if startDate is None:
            self.show_snack("Please specify the start date", True)
            return

        endDate = self.end_date_field.get_date()
        if endDate is None:
            self.show_snack("Please specify the end date", True)
            return

        if startDate > endDate:
            self.show_snack(
                "The end date of the contract cannot be before the start date", True
            )
            return

        self.show_progress_bar_disable_action()
        result: IntentResult = self.intent_handler.save_contract(
            title=self.title,
            signature_date=signatureDate,
            start_date=startDate,
            end_date=endDate,
            client=self.client,
            rate=self.rate,
            currency=self.currency,
            VAT_rate=self.vat_rate,
            unit=self.time_unit,
            units_per_workday=self.unit_pw,
            volume=self.volume,
            term_of_payment=self.term_of_payment,
            billing_cycle=self.billing_cycle,
        )
        # TODO add contract if updating
        msg = (
            "New contract created successfully"
            if result.was_intent_successful
            else result.error_msg
        )
        isError = not result.was_intent_successful
        self.enable_action_remove_progress_bar()
        self.show_snack(msg, isError)
        if not isError:
            # re route back
            self.on_navigate_back()

    def build(self):
        self.title_field = views.get_std_txt_field(
            label="Title",
            hint="Contract's title",
            on_change=self.on_title_changed,
            on_focus=self.clear_title_error,
        )
        self.rate_field = views.get_std_txt_field(
            label="Rate",
            hint="Contract's rate",
            on_change=self.on_rate_changed,
            on_focus=self.clear_rate_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )
        self.currency_field = views.get_std_txt_field(
            label="Currency",
            hint="Payment currency",
            on_change=self.on_currency_changed,
            on_focus=self.clear_currency_error,
        )
        self.vat_rate_field = views.get_std_txt_field(
            label="Vat",
            hint="Vat rate",
            on_change=self.on_vat_rate_changed,
            on_focus=self.clear_vat_rate_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )
        self.unit_PW_field = views.get_std_txt_field(
            label="Units per workday",
            hint="",
            on_change=self.on_upw_changed,
            on_focus=self.clear_upw_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )
        self.volume_field = views.get_std_txt_field(
            label="Volume (optional)",
            hint="",
            on_change=self.on_volume_changed,
            on_focus=self.clear_volume_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )
        self.term_of_payment_field = views.get_std_txt_field(
            label="Term of payment (optional)",
            hint="",
            on_change=self.on_top_changed,
            on_focus=self.clear_top_error,
            keyboard_type=utils.KEYBOARD_NUMBER,
        )
        self.clients_field = views.get_dropdown(
            label="Client",
            on_change=self.on_client_selected,
            items=self.get_clients_as_list(),
        )
        self.units_field = views.get_dropdown(
            label="Time Unit",
            on_change=self.on_unit_selected,
            items=get_time_unit_values_as_list(),
        )
        self.billing_cycle_field = views.get_dropdown(
            label="Billing Cycle",
            on_change=self.on_billing_cycle_selected,
            items=get_cycle_values_as_list(),
        )
        self.signature_date_field = views.DateSelector(label="Signed on Date")
        self.start_date_field = views.DateSelector(label="Start Date")
        self.end_date_field = views.DateSelector(label="End Date")
        self.submit_btn = views.get_primary_btn(
            label="Create Contract", on_click=self.on_save
        )
        view = flet.Container(
            expand=True,
            padding=flet.padding.all(dimens.SPACE_MD),
            margin=flet.margin.symmetric(vertical=dimens.SPACE_MD),
            content=flet.Card(
                expand=True,
                content=flet.Container(
                    flet.Column(
                        expand=True,
                        controls=[
                            flet.Row(
                                controls=[
                                    flet.IconButton(
                                        icon=flet.icons.CHEVRON_LEFT_ROUNDED,
                                        on_click=self.on_navigate_back,
                                    ),
                                    views.get_headline_with_subtitle(
                                        title="New Contract",
                                        subtitle="Create a new contract",
                                    ),
                                ]
                            ),
                            self.loading_indicator,
                            views.mdSpace,
                            self.title_field,
                            views.smSpace,
                            self.currency_field,
                            self.rate_field,
                            self.term_of_payment_field,
                            self.unit_PW_field,
                            self.vat_rate_field,
                            self.volume_field,
                            views.smSpace,
                            flet.Row(
                                alignment=utils.SPACE_BETWEEN_ALIGNMENT,
                                vertical_alignment=utils.CENTER_ALIGNMENT,
                                spacing=dimens.SPACE_STD,
                                controls=[
                                    self.clients_field,
                                    flet.IconButton(
                                        icon=flet.icons.ADD_CIRCLE_OUTLINE,
                                        on_click=self.on_add_client_clicked,
                                    ),
                                ],
                            ),
                            views.smSpace,
                            self.units_field,
                            views.smSpace,
                            self.billing_cycle_field,
                            views.smSpace,
                            self.signature_date_field,
                            views.smSpace,
                            self.start_date_field,
                            views.mdSpace,
                            self.end_date_field,
                            views.mdSpace,
                            self.submit_btn,
                        ],
                    ),
                    padding=flet.padding.all(dimens.SPACE_MD),
                    width=dimens.MIN_WINDOW_WIDTH,
                ),
            ),
        )
        return view

    def will_unmount(self):
        try:
            self.mounted = True
            if self.new_client_pop_up:
                self.new_client_pop_up.dimiss_open_dialogs()
        except Exception as e:
            print(e)


class ContractsListView(TuttleView, flet.UserControl):
    def __init__(self, params: TuttleViewParams):
        super().__init__(params)
        self.intent_handler = ContractsIntent()
        self.loading_indicator = views.horizontal_progress
        self.no_contracts_control = flet.Text(
            value="You have not added any contracts yet",
            color=colors.ERROR_COLOR,
            visible=False,
        )
        self.title_control = flet.ResponsiveRow(
            controls=[
                flet.Column(
                    col={"xs": 12},
                    controls=[
                        views.get_headline_txt(
                            txt="My Contracts", size=fonts.HEADLINE_4_SIZE
                        ),
                        self.loading_indicator,
                        self.no_contracts_control,
                    ],
                )
            ]
        )
        self.contracts_container = flet.GridView(
            expand=False,
            max_extent=540,
            child_aspect_ratio=1.0,
            spacing=dimens.SPACE_STD,
            run_spacing=dimens.SPACE_MD,
        )
        self.contracts_to_display = {}
        self.pop_up_handler = None

    def display_currently_filtered_contracts(self):
        self.contracts_container.controls.clear()
        for key in self.contracts_to_display:
            contract = self.contracts_to_display[key]
            contractCard = ContractCard(
                contract=contract,
                on_click_view=self.on_view_contract_clicked,
                on_click_edit=self.on_edit_contract_clicked,
                on_click_delete=self.on_delete_contract_clicked,
            )
            self.contracts_container.controls.append(contractCard)

    def on_view_contract_clicked(self, contract_id: str):
        self.navigate_to_route(res_utils.CONTRACT_DETAILS_SCREEN_ROUTE, contract_id)

    def on_edit_contract_clicked(self, contract_id: str):
        self.navigate_to_route(res_utils.CONTRACT_EDITOR_SCREEN_ROUTE, contract_id)

    def on_delete_contract_clicked(self, contract_id: str):
        if contract_id not in self.contracts_to_display:
            return
        contract_title = self.contracts_to_display[contract_id].title
        if self.pop_up_handler:
            self.pop_up_handler.close_dialog()
        self.pop_up_handler = views.ConfirmDisplayPopUp(
            dialog_controller=self.dialog_controller,
            title="Are You Sure?",
            description=f"Are you sure you wish to delete this contract?\n{contract_title}",
            on_proceed=self.on_delete_contract_confirmed,
            proceed_button_label="Yes! Delete",
            data_on_confirmed=contract_id,
        )
        self.pop_up_handler.open_dialog()

    def on_delete_contract_confirmed(self, contract_id: str):
        self.loading_indicator.visible = True
        if self.mounted:
            self.update()
        result = self.intent_handler.delete_contract_by_id(contract_id=contract_id)
        is_error = not result.was_intent_successful
        msg = "Contract deleted!" if not is_error else result.error_msg
        self.show_snack(msg, is_error)
        if not is_error and contract_id in self.contracts_to_display:
            del self.contracts_to_display[contract_id]
            self.display_currently_filtered_contracts()
        self.loading_indicator.visible = False
        if self.mounted:
            self.update()

    def on_filter_contracts(self, filterByState: ContractStates):
        if filterByState.value == ContractStates.ACTIVE.value:
            self.contracts_to_display = self.intent_handler.get_active_contracts()
        elif filterByState.value == ContractStates.UPCOMING.value:
            self.contracts_to_display = self.intent_handler.get_upcoming_contracts()
        elif filterByState.value == ContractStates.COMPLETED.value:
            self.contracts_to_display = self.intent_handler.get_completed_contracts()
        else:
            self.contracts_to_display = self.intent_handler.get_all_contracts_as_map()
        self.display_currently_filtered_contracts()
        if self.mounted:
            self.update()

    def show_no_contracts(self):
        self.no_contracts_control.visible = True

    def did_mount(self):
        try:
            self.mounted = True
            self.loading_indicator.visible = True
            self.contracts_to_display = self.intent_handler.get_all_contracts_as_map()
            count = len(self.contracts_to_display)
            self.loading_indicator.visible = False
            if count == 0:
                self.show_no_contracts()
            else:
                self.display_currently_filtered_contracts()
            if self.mounted:
                self.update()
        except Exception as e:
            # log error
            print(f"exception raised @contracts.did_mount {e.__class__.__name__}")

    def build(self):
        view = flet.Column(
            controls=[
                self.title_control,
                views.mdSpace,
                ContractFiltersView(onStateChanged=self.on_filter_contracts),
                views.mdSpace,
                flet.Container(self.contracts_container, expand=True),
            ]
        )
        return view

    def will_unmount(self):
        self.mounted = False
        if self.pop_up_handler:
            self.pop_up_handler.dimiss_open_dialogs()


class ViewContractScreen(TuttleView, flet.UserControl):
    def __init__(
        self,
        params: TuttleViewParams,
        contract_id: str,
    ):
        super().__init__(params)
        self.intent_handler = ContractsIntent()
        self.contract_id = contract_id
        self.loading_indicator = views.horizontal_progress
        self.contract: Optional[Contract] = None
        self.pop_up_handler = None

    def display_contract_data(self):
        self.contract_title_control.value = self.contract.title
        self.client_control.value = self.contract.client.name
        self.contract_title_control.value = self.contract.title
        self.start_date_control.value = self.contract.start_date
        self.end_date_control.value = self.contract.end_date
        self.status_control.value = f"Status {self.contract.get_status()}"
        self.billing_cycle_control.value = self.contract.billing_cycle
        self.rate_control.value = self.contract.rate
        self.currency_control.value = self.contract.currency
        self.vat_rate_control.value = self.contract.VAT_rate
        self.unit_control.value = self.contract.unit
        self.units_per_workday_control.value = self.contract.units_per_workday
        self.volume_control.value = self.contract.volume
        self.term_of_payment_control.value = self.contract.term_of_payment
        self.signature_date_control.value = self.contract.signature_date

    def did_mount(self):
        self.mounted = True
        result: IntentResult = self.intent_handler.get_contract_by_id(self.contract_id)
        if not result.was_intent_successful:
            self.show_snack(result.error_msg, True)
        else:
            self.contract = result.data
            self.display_contract_data()
        self.loading_indicator.visible = False
        if self.mounted:
            self.update()

    def on_view_client_clicked(self, e):
        self.show_snack("Coming soon", False)

    def on_mark_as_complete_clicked(self, e):
        self.show_snack("Coming soon", False)

    def on_edit_clicked(self, e):
        if not self.contract:
            return
        self.navigate_to_route(res_utils.CONTRACT_EDITOR_SCREEN_ROUTE, self.contract.id)

    def on_delete_clicked(self, e):
        if self.contract is None:
            return
        if self.pop_up_handler:
            self.pop_up_handler.close_dialog()
        self.pop_up_handler = views.ConfirmDisplayPopUp(
            dialog_controller=self.dialog_controller,
            title="Are You Sure?",
            description=f"Are you sure you wish to delete this contract?\n{self.contract.title}",
            on_proceed=self.on_delete_confirmed,
            proceed_button_label="Yes! Delete",
            data_on_confirmed=self.contract.id,
        )
        self.pop_up_handler.open_dialog()

    def on_delete_confirmed(self, contract_id):
        result = self.intent_handler.delete_contract_by_id(contract_id)
        is_err = not result.was_intent_successful
        msg = result.error_msg if is_err else "Contract deleted!"
        self.show_snack(msg, is_err)
        if not is_err:
            # go back
            self.on_navigate_back()

    def get_body_element(self, label, control):
        return flet.ResponsiveRow(
            controls=[
                flet.Text(
                    label,
                    color=colors.GRAY_COLOR,
                    size=fonts.BODY_2_SIZE,
                    col={
                        "xs": 12,
                    },
                ),
                control,
            ],
            spacing=dimens.SPACE_XS,
            run_spacing=0,
            vertical_alignment=utils.CENTER_ALIGNMENT,
        )

    def build(self):
        """Called when page is built"""
        self.edit_contract_btn = flet.IconButton(
            icon=flet.icons.EDIT_OUTLINED,
            tooltip="Edit contract",
            on_click=self.on_edit_clicked,
        )
        self.mark_as_complete_btn = flet.IconButton(
            icon=flet.icons.CHECK_CIRCLE_OUTLINE,
            icon_color=colors.PRIMARY_COLOR,
            tooltip="Mark contract as completed",
            on_click=self.on_mark_as_complete_clicked,
        )
        self.delete_contract_btn = flet.IconButton(
            icon=flet.icons.DELETE_OUTLINE_ROUNDED,
            icon_color=colors.ERROR_COLOR,
            tooltip="Delete contract",
            on_click=self.on_delete_clicked,
        )

        self.client_control = flet.Text(
            size=fonts.SUBTITLE_2_SIZE,
        )
        self.contract_title_control = flet.Text(
            size=fonts.SUBTITLE_1_SIZE,
        )
        self.billing_cycle_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.rate_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.currency_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.vat_rate_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.unit_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.units_per_workday_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.volume_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.term_of_payment_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )

        self.signature_date_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.start_date_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )
        self.end_date_control = flet.Text(
            size=fonts.BODY_1_SIZE,
            text_align=utils.TXT_ALIGN_JUSTIFY,
        )

        self.status_control = flet.Text(
            size=fonts.BUTTON_SIZE, color=colors.PRIMARY_COLOR
        )

        page_view = flet.Row(
            [
                flet.Container(
                    padding=flet.padding.all(dimens.SPACE_STD),
                    width=int(dimens.MIN_WINDOW_WIDTH * 0.3),
                    content=flet.Column(
                        controls=[
                            flet.IconButton(
                                icon=flet.icons.KEYBOARD_ARROW_LEFT,
                                on_click=self.on_navigate_back,
                            ),
                            flet.TextButton(
                                "Client",
                                tooltip="View contract's client",
                                on_click=self.on_view_client_clicked,
                            ),
                        ]
                    ),
                ),
                flet.Container(
                    expand=True,
                    padding=flet.padding.all(dimens.SPACE_MD),
                    content=flet.Column(
                        controls=[
                            self.loading_indicator,
                            flet.Row(
                                controls=[
                                    flet.Icon(flet.icons.HANDSHAKE_ROUNDED),
                                    flet.Column(
                                        expand=True,
                                        spacing=0,
                                        run_spacing=0,
                                        controls=[
                                            flet.Row(
                                                vertical_alignment=utils.CENTER_ALIGNMENT,
                                                alignment=utils.SPACE_BETWEEN_ALIGNMENT,
                                                controls=[
                                                    flet.Text(
                                                        "Contract",
                                                        size=fonts.HEADLINE_4_SIZE,
                                                        font_family=fonts.HEADLINE_FONT,
                                                        color=colors.PRIMARY_COLOR,
                                                    ),
                                                    flet.Row(
                                                        vertical_alignment=utils.CENTER_ALIGNMENT,
                                                        alignment=utils.SPACE_BETWEEN_ALIGNMENT,
                                                        spacing=dimens.SPACE_STD,
                                                        run_spacing=dimens.SPACE_STD,
                                                        controls=[
                                                            self.edit_contract_btn,
                                                            self.mark_as_complete_btn,
                                                            self.delete_contract_btn,
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            self.get_body_element(
                                                "Title",
                                                self.contract_title_control,
                                            ),
                                            self.get_body_element(
                                                "Client", self.client_control
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            views.mdSpace,
                            self.get_body_element(
                                "Billing Cycle", self.billing_cycle_control
                            ),
                            self.get_body_element("Rate", self.rate_control),
                            self.get_body_element("Currency", self.currency_control),
                            self.get_body_element("Vat Rate", self.vat_rate_control),
                            self.get_body_element("Time Unit", self.unit_control),
                            self.get_body_element(
                                "Units per Workday",
                                self.units_per_workday_control,
                            ),
                            self.get_body_element("Volume", self.volume_control),
                            self.get_body_element(
                                "Term of Payment", self.term_of_payment_control
                            ),
                            self.get_body_element(
                                "Signed on Date", self.signature_date_control
                            ),
                            self.get_body_element(
                                "Start Date", self.start_date_control
                            ),
                            self.get_body_element("End Date", self.end_date_control),
                            views.mdSpace,
                            flet.Row(
                                spacing=dimens.SPACE_STD,
                                run_spacing=dimens.SPACE_STD,
                                alignment=utils.START_ALIGNMENT,
                                vertical_alignment=utils.CENTER_ALIGNMENT,
                                controls=[
                                    flet.Card(
                                        flet.Container(
                                            self.status_control,
                                            padding=flet.padding.all(dimens.SPACE_SM),
                                        ),
                                        elevation=2,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
            spacing=dimens.SPACE_XS,
            run_spacing=dimens.SPACE_MD,
            alignment=utils.START_ALIGNMENT,
            vertical_alignment=utils.START_ALIGNMENT,
            expand=True,
        )
        return page_view

    def will_unmount(self):
        self.mounted = False
