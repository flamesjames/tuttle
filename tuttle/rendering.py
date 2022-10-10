"""Document rendering."""

import os
import sys
from pathlib import Path
import shutil
import glob

import jinja2
from babel.numbers import format_currency
import pandas
from loguru import logger

# pdfkit needs wkhtmltopdf to be installed
if getattr(sys, "frozen", False):
    os.environ["PATH"] = sys._MEIPASS + os.pathsep + os.environ["PATH"]
import pdfkit


from .model import User, Invoice, Timesheet, Project
from .view import Timeline


def get_template_path(template_name) -> str:
    """Get the path to an HTML template by name"""
    app_dir = Path(__file__).parent.parent.resolve()
    template_path = app_dir / Path(f"templates/{template_name}")
    logger.info(f"Template path: {template_path}")
    return template_path


def convert_html_to_pdf(
    in_path,
    out_path,
    css_paths=[],
):
    """_summary_

    Args:
        source_dir (_type_): _description_
        dest_dir (_type_): _description_
    """
    logger.info(f"converting html to pdf: {in_path} -> {out_path}")
    try:
        pdfkit.from_file(input=in_path, output_path=out_path, css=css_paths)
    except OSError as ex:
        # Exit with code 1 due to network error: ProtocolUnknownError
        # ignore this error since a correct output is produced anyway
        pass


def render_invoice(
    user: User,
    invoice: Invoice,
    document_format: str = "html",
    out_dir: str = None,
    style: str = None,
) -> str:
    """Render an Invoice using an HTML template.

    Args:
        user (User): [description]
        invoice (Invoice): [description]

    Returns:
        str: [description]
    """

    def as_currency(number):
        return format_currency(
            number, currency=invoice.contract.currency, locale="en_US"
        )

    def as_percentage(number):
        return f"{number * 100:.1f} %"

    template_name = f"invoice-anvil"
    template_path = get_template_path(template_name)
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))

    template_env.filters["as_currency"] = as_currency
    template_env.filters["as_percentage"] = as_percentage

    invoice_template = template_env.get_template(f"invoice.html")
    html = invoice_template.render(
        user=user,
        invoice=invoice,
        style=style,
    )
    # TODO: output as PDF
    # output
    if out_dir is None:
        return html
    else:
        # write invoice html
        invoice_dir = Path(out_dir) / Path(invoice.prefix)
        invoice_dir.mkdir(parents=True, exist_ok=True)
        invoice_path = invoice_dir / Path(f"{invoice.prefix}.html")
        with open(invoice_path, "w") as invoice_file:
            invoice_file.write(html)
        # copy stylsheets
        if style:
            stylesheets = []
            stylesheet_folders = []
            if style == "anvil":
                stylesheets = ["invoice.css"]
                stylesheet_folders = [
                    "web",
                ]
            for stylesheet_path in stylesheets:
                stylesheet_path = template_path / stylesheet_path
                shutil.copy(stylesheet_path, invoice_dir)
            for stylesheet_folder_path in stylesheet_folders:
                full_stylesheet_folder_path = template_path / stylesheet_folder_path
                shutil.copytree(
                    full_stylesheet_folder_path,
                    invoice_dir / stylesheet_folder_path,
                    dirs_exist_ok=True,
                )
        if document_format == "pdf":
            css_paths = [
                path for path in glob.glob(f"{invoice_dir}/**/*.css", recursive=True)
            ]
            convert_html_to_pdf(
                in_path=str(invoice_path),
                css_paths=css_paths,
                out_path=invoice_dir / Path(f"{invoice.prefix}.pdf"),
            )
    # finally set the rendered flag
    invoice.rendered = True


def render_timesheet(
    user: User,
    timesheet: Timesheet,
    document_format: str = "html",
    out_dir: str = None,
    style: str = "anvil",
) -> str:
    """Render a Timeseheet using an HTML template.

    Args:
        user (User): [description]
        timesheet (Timesheet): [description]
        out_dir (str, optional): [description]. Defaults to None.

    Returns:
        str: [description]
    """
    template_name = "timesheet-anvil"
    template_path = get_template_path(template_name)
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    # filters
    template_env.filters["as_hours"] = lambda td: td / pandas.Timedelta("1 hour")

    timesheet_template = template_env.get_template("timesheet.html")
    html = timesheet_template.render(user=user, timesheet=timesheet, style=style)
    # output
    if out_dir is None:
        return html
    else:
        # write invoice html
        prefix = f"Timesheet-{timesheet.title}"
        timesheet_dir = Path(out_dir) / Path(prefix)
        timesheet_dir.mkdir(parents=True, exist_ok=True)
        timesheet_path = timesheet_dir / Path(f"{prefix}.html")
        with open(timesheet_path, "w") as timesheet_file:
            timesheet_file.write(html)
        # copy stylsheets
        if style:
            stylesheets = []
            stylesheet_folders = []
            if style == "anvil":
                stylesheets = ["timesheet.css"]
                stylesheet_folders = [
                    "web",
                ]
            for stylesheet_path in stylesheets:
                stylesheet_path = template_path / stylesheet_path
                shutil.copy(stylesheet_path, timesheet_dir)
            for stylesheet_folder_path in stylesheet_folders:
                full_stylesheet_folder_path = template_path / stylesheet_folder_path
                shutil.copytree(
                    full_stylesheet_folder_path,
                    timesheet_dir / stylesheet_folder_path,
                    dirs_exist_ok=True,
                )
        if document_format == "pdf":
            css_paths = [
                path for path in glob.glob(f"{timesheet_dir}/**/*.css", recursive=True)
            ]
            convert_html_to_pdf(
                in_path=str(timesheet_path),
                css_paths=css_paths,
                out_path=timesheet_dir / Path(f"{prefix}.pdf"),
            )


def render_timeline(
    timeline: Timeline,
    out_dir: str = None,
) -> str:
    """ """
    # TODO: fill template from https://codepen.io/carrrter/pen/ELLmyX
    template_name = "timeline"
    template_path = get_template_path(template_name)
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
    # filters
    template_env.filters["as_date_rev"] = lambda date: date.strftime(format="%d/%m/%Y")

    timesheet_template = template_env.get_template(f"{template_name}.html")
    html = timesheet_template.render(timeline=timeline)
    # output
    if out_dir is None:
        return html
    else:
        # write html
        prefix = f"Timeline"
        folder = Path(out_dir) / Path(prefix)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / Path(f"{prefix}.html")
        with open(path, "w") as html_file:
            html_file.write(html)
