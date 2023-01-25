import typing
from typing import Callable, List, Optional, Union
from dataclasses import dataclass
import datetime

from flet import (
    AlertDialog,
    Column,
    Container,
    Dropdown,
    ElevatedButton,
    FilledButton,
    Icon,
    Image,
    PopupMenuButton,
    PopupMenuItem,
    ProgressBar,
    margin,
    NavigationRail,
    Row,
    Text,
    TextField,
    TextStyle,
    UserControl,
    alignment,
    border_radius,
    dropdown,
    icons,
    padding,
)

from res import colors, dimens, fonts, image_paths

from .abstractions import DialogHandler
from . import utils

lgSpace = Container(height=dimens.SPACE_LG, width=dimens.SPACE_STD, padding=0, margin=0)
mdSpace = Container(height=dimens.SPACE_MD, width=dimens.SPACE_MD, padding=0, margin=0)
stdSpace = Container(
    height=dimens.SPACE_STD, width=dimens.SPACE_STD, padding=0, margin=0
)
smSpace = Container(height=dimens.SPACE_SM, width=dimens.SPACE_SM, padding=0, margin=0)
xsSpace = Container(height=dimens.SPACE_XS, width=dimens.SPACE_XS, padding=0, margin=0)


def get_heading(
    title: str = "",
    size: int = fonts.SUBTITLE_1_SIZE,
    color: Optional[str] = None,
    align: str = utils.TXT_ALIGN_LEFT,
    show: bool = True,
):
    """Displays text formatted as a headline"""
    return Text(
        title,
        font_family=fonts.HEADLINE_FONT,
        weight=fonts.BOLD_FONT,
        size=size,
        color=color,
        text_align=align,
        visible=show,
    )


def get_sub_heading_txt(
    subtitle: str = "",
    size: int = fonts.SUBTITLE_2_SIZE,
    color: Optional[str] = None,
    align: str = utils.TXT_ALIGN_LEFT,
    show: bool = True,
    expand: bool = False,
):
    """Displays text formatted as a headline"""
    return Text(
        subtitle,
        font_family=fonts.HEADLINE_FONT,
        size=size,
        color=color,
        text_align=align,
        visible=show,
        expand=expand,
    )


def get_heading_with_subheading(
    title: str,
    subtitle: str,
    alignment_in_container: str = utils.START_ALIGNMENT,
    txt_alignment: str = utils.TXT_ALIGN_LEFT,
    title_size: int = fonts.SUBTITLE_1_SIZE,
    subtitle_size: int = fonts.SUBTITLE_2_SIZE,
    subtitle_color: Optional[str] = None,
):
    """Displays text formatted as a headline with a subtitle below it"""
    return Column(
        spacing=0,
        horizontal_alignment=alignment_in_container,
        controls=[
            get_heading(
                title=title,
                size=title_size,
                align=txt_alignment,
            ),
            get_sub_heading_txt(
                subtitle=subtitle,
                size=subtitle_size,
                align=txt_alignment,
                color=subtitle_color,
            ),
        ],
    )


def get_body_txt(
    txt: str = "",
    size: int = fonts.BODY_1_SIZE,
    color: Optional[str] = None,
    show: bool = True,
    col: Optional[dict] = None,
    align: str = utils.TXT_ALIGN_LEFT,
    **kwargs,
):
    """Displays text standard-formatted for body"""
    return Text(
        col=col,
        value=txt,
        color=color,
        size=size,
        visible=show,
        text_align=align,
        **kwargs,
    )


def get_std_txt_field(
    on_change: typing.Optional[Callable] = None,
    label: str = "",
    hint: str = "",
    keyboard_type: str = utils.KEYBOARD_TEXT,
    on_focus: typing.Optional[Callable] = None,
    initial_value: typing.Optional[str] = None,
    expand: typing.Optional[int] = None,
    width: typing.Optional[int] = None,
    show: bool = True,
):
    """Displays commonly used text field in app forms"""
    txtFieldPad = padding.symmetric(horizontal=dimens.SPACE_XS)

    return TextField(
        label=label,
        keyboard_type=keyboard_type,
        content_padding=txtFieldPad,
        hint_text=hint,
        hint_style=TextStyle(size=fonts.CAPTION_SIZE),
        value=initial_value,
        focused_border_width=1,
        on_focus=on_focus,
        on_change=on_change,
        password=keyboard_type == utils.KEYBOARD_PASSWORD,
        expand=expand,
        width=width,
        disabled=keyboard_type == utils.KEYBOARD_NONE,
        text_size=fonts.BODY_1_SIZE,
        label_style=TextStyle(size=fonts.BODY_2_SIZE),
        error_style=TextStyle(size=fonts.BODY_2_SIZE, color=colors.ERROR_COLOR),
        visible=show,
    )


def get_std_multiline_field(
    on_change,
    label: str,
    hint: str,
    on_focus: typing.Optional[Callable] = None,
    keyboardType: str = utils.KEYBOARD_MULTILINE,
    minLines: int = 3,
    maxLines: int = 5,
):
    """Displays commonly used textarea field in app forms"""
    txtFieldHintStyle = TextStyle(size=fonts.CAPTION_SIZE)

    return TextField(
        label=label,
        keyboard_type=keyboardType,
        hint_text=hint,
        hint_style=txtFieldHintStyle,
        focused_border_width=1,
        min_lines=minLines,
        max_lines=maxLines,
        on_focus=on_focus,
        on_change=on_change,
        text_size=fonts.BODY_1_SIZE,
        label_style=TextStyle(size=fonts.BODY_2_SIZE),
        error_style=TextStyle(size=fonts.BODY_2_SIZE, color=colors.ERROR_COLOR),
    )


def get_error_txt(
    txt: str,
    show: bool = True,
):
    """Displays text formatted for errors / warnings"""
    return get_body_txt(txt, color=colors.ERROR_COLOR, show=show)


def get_primary_btn(
    on_click,
    label: str,
    width: int = 200,
    icon: Optional[str] = None,
    show: bool = True,
):
    """An elevated button with primary styling"""
    return FilledButton(label, width=width, on_click=on_click, icon=icon, visible=show)


def get_secondary_btn(
    on_click,
    label: str,
    width: int = 200,
    icon: Optional[str] = None,
):
    """An elevated button with secondary styling"""
    return ElevatedButton(
        label,
        width=width,
        on_click=on_click,
        icon=icon,
    )


def get_danger_button(
    on_click,
    label: str,
    width: int = 200,
    icon: Optional[str] = None,
):
    """An elevated button with danger styling"""
    return ElevatedButton(
        label,
        width=width,
        on_click=on_click,
        icon=icon,
        color=colors.DANGER_COLOR,
    )


def get_profile_photo_img(pic_src: str = image_paths.default_avatar):

    return Image(
        src=pic_src,
        width=72,
        height=72,
        border_radius=border_radius.all(36),
        fit=utils.CONTAIN,
    )


def get_image(path: str, semantic_label: str, width: int):
    return Container(
        width=width,
        content=Image(src=path, fit=utils.CONTAIN, semantics_label=semantic_label),
    )


def get_app_logo(width: int = 12):
    """Returns app logo"""
    return Container(
        width=width,
        content=Image(
            src=image_paths.logoPath, fit=utils.CONTAIN, semantics_label="logo"
        ),
    )


def get_labelled_logo():
    """Returns app logo with app name next to it"""
    return Row(
        vertical_alignment=utils.CENTER_ALIGNMENT,
        controls=[
            get_app_logo(),
            get_heading(
                "Tuttle",
                size=fonts.HEADLINE_3_SIZE,
            ),
        ],
    )


horizontal_progress = ProgressBar(
    width=320,
    height=4,
)


def update_dropdown_items(dropDown: Dropdown, items: List[str]):
    options = []
    for item in items:
        options.append(
            dropdown.Option(
                text=item,
            )
        )
    dropDown.options = options


def get_dropdown(
    label: str,
    on_change: Callable,
    items: List[str],
    hint: Optional[str] = "",
    width: Optional[int] = None,
    initial_value: Optional[str] = None,
    show: bool = True,
):
    options = []
    for item in items:
        options.append(
            dropdown.Option(
                text=item,
            )
        )
    return Dropdown(
        label=label,
        hint_text=hint,
        options=options,
        text_size=fonts.BODY_1_SIZE,
        label_style=TextStyle(size=fonts.BODY_2_SIZE),
        on_change=on_change,
        width=width,
        value=initial_value,
        content_padding=padding.all(dimens.SPACE_XS),
        error_style=TextStyle(size=fonts.BODY_2_SIZE, color=colors.ERROR_COLOR),
        visible=show,
    )


class StandardDropdown(Dropdown):
    """
    A dropdown UI element that allows the user to select from a list of items.
    It allows to pass list of items, hint, width and initial_value as optional parameters to configure the dropdown as per requirement.
    """

    def __init__(
        self,
        label: str,
        on_change: Callable,
        options: List[Union[str, dropdown.Option]],
        hint: Optional[str] = "",
        width: Optional[int] = None,
        initial_value: Optional[str] = None,
    ):
        """
        Parameters
        ----------
        label : str
            Label to be displayed above the dropdown
        on_change : Callable
            A callback function that will be called when the user interacts with the dropdown
        items : List[Union[str, dropdown.Option]]
            list of items that the dropdown should have. Each item can be either a string or a dropdown.Option object
        hint : Optional[str]
            a hint that will be displayed when the user interacts with the dropdown
        width : Optional[int]
            Width of the dropdown element
        initial_value : Optional[str]
            Initial value of the dropdown element
        """
        options = []
        for item in options:
            if isinstance(item, str):
                options.append(dropdown.Option(text=item))
            elif isinstance(item, dropdown.Option):
                options.append(item)
            else:
                raise TypeError("item must be of type 'str' or 'dropdown.Option'")

        super().__init__(
            label=label,
            hint_text=hint,
            options=options,
            text_size=fonts.BODY_1_SIZE,
            label_style=TextStyle(size=fonts.BODY_2_SIZE),
            on_change=on_change,
            width=width,
            value=initial_value,
            content_padding=padding.all(dimens.SPACE_XS),
            error_style=TextStyle(size=fonts.BODY_2_SIZE, color=colors.ERROR_COLOR),
        )

    def update_items(self, items: List[str]):
        """
        Update the items of the dropdown
        Parameters:
        items: list of items to be set to the dropdown
        """
        options = []
        for item in items:
            options.append(dropdown.Option(text=item))
        self.options = options


class DateSelector(UserControl):
    """Date selector."""

    def __init__(
        self,
        label: str,
        initial_date: Optional[datetime.date] = None,
        label_color: Optional[str] = None,
    ):
        super().__init__()
        self.label = label
        self.initial_date = initial_date if initial_date else datetime.date.today()
        self.date = str(self.initial_date.day)
        self.month = str(self.initial_date.month)
        self.year = str(self.initial_date.year)
        self.label_color = label_color

        self.day_dropdown = get_dropdown(
            label="Day",
            hint="",
            on_change=self.on_date_set,
            items=[str(day) for day in range(1, 32)],
            width=50,
            initial_value=self.date,
        )

        self.month_dropdown = get_dropdown(
            label="Month",
            on_change=self.on_month_set,
            items=[str(month) for month in range(1, 13)],
            width=50,
            initial_value=self.month,
        )

        self.year_dropdown = get_dropdown(
            label="Year",
            on_change=self.on_year_set,
            # set items to a list of years -10 to + 10 years from now
            items=[
                str(year)
                for year in range(
                    datetime.date.today().year - 10, datetime.date.today().year + 10
                )
            ],
            width=100,
            initial_value=self.year,
        )

    def on_date_set(self, e):
        self.date = e.control.value

    def on_month_set(self, e):
        self.month = e.control.value

    def on_year_set(self, e):
        self.year = e.control.value

    def build(self):
        self.view = Container(
            content=Column(
                controls=[
                    get_body_txt(txt=self.label, color=self.label_color),
                    Row(
                        [
                            self.day_dropdown,
                            self.month_dropdown,
                            self.year_dropdown,
                        ],
                    ),
                ]
            ),
        )
        return self.view

    def set_date(self, date: Optional[datetime.date] = None):
        if date is None:
            return
        self.date = str(date.day)
        self.month = str(date.month)
        self.year = str(date.year)
        self.day_dropdown.value = self.date
        self.month_dropdown.value = self.month
        self.year_dropdown.value = self.year

        self.update()

    def get_date(self) -> Optional[datetime.date]:
        """Return the selected timeframe."""
        if self.year is None or self.month is None or self.date is None:
            return None

        date = datetime.date(
            year=int(self.year),
            month=int(self.month),
            day=int(self.date),
        )
        return date


class AlertDisplayPopUp(DialogHandler):
    """Pop up used for displaying alerts"""

    def __init__(
        self,
        dialog_controller: Callable[[any, utils.AlertDialogControls], None],
        title: str,
        description: str,
        on_complete: Optional[Callable] = None,
        button_label: str = "Got it",
        is_error: bool = True,
    ):
        pop_up_height = 150
        pop_up_width = int(dimens.MIN_WINDOW_WIDTH * 0.8)
        dialog = AlertDialog(
            content=Container(
                height=pop_up_height,
                content=Column(
                    scroll=utils.AUTO_SCROLL,
                    controls=[
                        get_heading(
                            title=title,
                            size=fonts.HEADLINE_4_SIZE,
                        ),
                        xsSpace,
                        get_body_txt(
                            txt=description,
                            size=fonts.SUBTITLE_1_SIZE,
                            color=colors.ERROR_COLOR if is_error else None,
                        ),
                    ],
                ),
            ),
            actions=[
                get_primary_btn(
                    label=button_label, on_click=self.on_complete_btn_clicked
                ),
            ],
        )
        super().__init__(dialog=dialog, dialog_controller=dialog_controller)
        self.on_complete_callback = on_complete

    def on_complete_btn_clicked(self, e):
        self.close_dialog()
        if self.on_complete_callback:
            self.on_complete_callback()


class ConfirmDisplayPopUp(DialogHandler):
    """Pop up used for displaying confirmation pop up"""

    def __init__(
        self,
        dialog_controller: Callable[[any, utils.AlertDialogControls], None],
        title: str,
        description: str,
        data_on_confirmed: any,
        on_proceed: Callable,
        on_cancel: Optional[Callable] = None,
        proceed_button_label: str = "Proceed",
        cancel_button_label: str = "Cancel",
    ):
        pop_up_height = 150
        pop_up_width = int(dimens.MIN_WINDOW_WIDTH * 0.8)
        dialog = AlertDialog(
            content=Container(
                height=pop_up_height,
                content=Column(
                    scroll=utils.AUTO_SCROLL,
                    controls=[
                        get_heading(
                            title=title,
                            size=fonts.HEADLINE_4_SIZE,
                        ),
                        xsSpace,
                        get_body_txt(
                            txt=description,
                            size=fonts.SUBTITLE_1_SIZE,
                        ),
                    ],
                ),
            ),
            actions=[
                get_secondary_btn(
                    label=cancel_button_label, on_click=self.on_cancel_btn_clicked
                ),
                get_primary_btn(
                    label=proceed_button_label, on_click=self.on_proceed_btn_clicked
                ),
            ],
        )
        super().__init__(dialog=dialog, dialog_controller=dialog_controller)
        self.on_proceed_callback = on_proceed
        self.on_cancel_callback = on_cancel
        self.data_on_confirmed = data_on_confirmed

    def on_cancel_btn_clicked(self, e):
        self.close_dialog()
        if self.on_cancel_callback:
            self.on_cancel_callback()

    def on_proceed_btn_clicked(self, e):
        self.close_dialog()
        self.on_proceed_callback(self.data_on_confirmed)


def pop_up_menu_item(icon, txt, on_click, is_delete: bool = False):
    return PopupMenuItem(
        content=Row(
            [
                Icon(
                    icon,
                    size=dimens.ICON_SIZE,
                    color=colors.ERROR_COLOR if is_delete else None,
                ),
                get_body_txt(
                    txt,
                    size=fonts.BUTTON_SIZE,
                    color=colors.ERROR_COLOR if is_delete else None,
                ),
            ]
        ),
        on_click=on_click,
    )


def context_pop_up_menu(
    on_click_edit: Optional[Callable] = None,
    on_click_delete: Optional[Callable] = None,
    view_item_lbl="View Details",
    delete_item_lbl="Delete",
    edit_item_lbl="Edit",
    on_click_view: Optional[Callable] = None,
    prefix_menu_items: Optional[list[PopupMenuItem]] = None,
    suffix_menu_items: Optional[list[PopupMenuItem]] = None,
):
    """Returns a customizable pop up menu button with optional view, edit and delete menus"""
    items = []
    if prefix_menu_items:
        items.extend(prefix_menu_items)
    if on_click_view:
        items.append(
            pop_up_menu_item(
                icons.VISIBILITY_OUTLINED, txt=view_item_lbl, on_click=on_click_view
            ),
        )
    if on_click_edit:
        items.append(
            pop_up_menu_item(
                icons.EDIT_OUTLINED,
                txt=edit_item_lbl,
                on_click=on_click_edit,
            )
        )
    if on_click_delete:
        items.append(
            pop_up_menu_item(
                icons.DELETE_OUTLINE,
                txt=delete_item_lbl,
                on_click=on_click_delete,
                is_delete=True,
            )
        )
    if suffix_menu_items:
        items.extend(suffix_menu_items)
    return PopupMenuButton(items=items)


def status_label(txt: str, is_done: bool):
    """Returns a text with a checked prefix icon"""
    return Row(
        controls=[
            Icon(
                icons.CHECK_CIRCLE_OUTLINE if is_done else icons.RADIO_BUTTON_UNCHECKED,
                size=dimens.SM_ICON_SIZE,
                color=colors.PRIMARY_COLOR if is_done else colors.GRAY_COLOR,
            ),
            get_body_txt(txt),
        ]
    )


def get_or_txt(show_lines: Optional[bool] = True, show: bool = True):
    """Returns a view representing ---- OR ----"""
    return Row(
        visible=show,
        alignment=utils.SPACE_BETWEEN_ALIGNMENT
        if show_lines
        else utils.CENTER_ALIGNMENT,
        vertical_alignment=utils.CENTER_ALIGNMENT,
        controls=[
            Container(
                height=2,
                bgcolor=colors.GRAY_COLOR,
                width=100,
                alignment=alignment.center,
                visible=show_lines,
            ),
            get_body_txt("OR", align=utils.TXT_ALIGN_CENTER, color=colors.GRAY_COLOR),
            Container(
                height=2,
                bgcolor=colors.GRAY_COLOR,
                width=100,
                alignment=alignment.center,
                visible=show_lines,
            ),
        ],
    )


@dataclass
class NavigationMenuItem:
    """defines a menu item used in navigation rails"""

    index: int
    label: str
    icon: str
    selected_icon: str
    destination: UserControl
    on_new_screen_route: Optional[str] = None
    on_new_intent: Optional[str] = None


def get_std_navigation_menu(
    title: str,
    on_change,
    selected_index: Optional[int] = 0,
    destinations=[],
    menu_height: int = 300,
    width: int = int(dimens.MIN_WINDOW_WIDTH * 0.3),
    left_padding: int = dimens.SPACE_STD,
    top_margin: int = dimens.SPACE_STD,
):
    """
    Returns a navigation menu for the application.

    :param title: Title of the navigation menu.
    :param on_change: Callable function to be called when the selected item in the menu changes.
    :param selected_index: The index of the selected item in the menu.
    :param destinations: List of destinations in the menu.
    :param menu_height: The height of the menu.
    :return: A NavigationRail widget containing the navigation menu.
    """
    return NavigationRail(
        leading=Container(
            content=get_sub_heading_txt(
                subtitle=title,
                align=utils.START_ALIGNMENT,
                expand=True,
                color=colors.GRAY_DARK_COLOR,
            ),
            expand=True,
            width=width,
            margin=margin.only(top=top_margin),
            padding=padding.only(left=left_padding),
        ),
        selected_index=selected_index,
        min_width=utils.COMPACT_RAIL_WIDTH,
        extended=True,
        height=menu_height,
        min_extended_width=width,
        destinations=destinations,
        on_change=on_change,
    )
