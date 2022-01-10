"""Object model."""

from typing import Optional, List
import datetime
import enum

import sqlalchemy
from sqlmodel import Field, Relationship
from sqlmodel import SQLModel
from pydantic import EmailStr
from decimal import Decimal

import pandas

# TODO: support currencies
# from money.money import Money
# from money.currency import Currency

from delorean import Delorean as Time
from datetime import timedelta as Timespan

from sqlmodel.main import RelationshipInfo


# TODO: created & modified time stamps


class Address(SQLModel, table=True):
    """Postal address."""

    id: Optional[int] = Field(default=None, primary_key=True)
    street: str
    number: str
    city: str
    country: str


class Freelancer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # name: str
    # business_name: Optional[str]
    # email: EmailStr
    # TODO: address
    # address_id: Optional[int] = Field(default=None, foreign_key="address.id")
    # address: Optional[Address] = Relationship()
    # VAT_number: str
    # business_account: Optional["BankAccount"]


class Bank(SQLModel, table=True):
    """A bank."""

    id: Optional[int] = Field(default=None, primary_key=True)
    BLZ: str  # TODO: add type / validator


class BankAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    IBAN: str  # TODO: add type / validator
    BIC: str  # TODO: add type / validator
    username: str  # online banking user name
    # owner: User


class Contact(SQLModel, table=True):
    """An entry in the address book."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    e_mail: Optional[EmailStr]
    invoicing_contact_of: List["Client"] = Relationship(
        back_populates="invoicing_contact"
    )
    # post address


class Client(SQLModel, table=True):
    """A client the freelancer has contracted with."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # Client 1:1 invoicing Contact
    invoicing_contact_id: Optional[int] = Field(default=None, foreign_key="contact.id")
    invoicing_contact: Optional[Contact] = Relationship(
        back_populates="invoicing_contact_of"
    )
    # contracts: List["Contract"] = Relationship(back_populates="client")
    # non-invoice related contact person?


class Rate(SQLModel, table=True):
    class Cycle(enum.Enum):
        HOURLY = 0
        DAILY = 1

    id: Optional[int] = Field(default=None, primary_key=True)
    amount: Decimal
    # currency: Currency  # TODO:
    cycle: "Rate.Cycle" = Field(
        sa_column=sqlalchemy.Column(sqlalchemy.Enum("Rate.Cycle"))
    )


# class BillingCycle(SQLModel, table=True):
#     """Billing cycle associated with a contract."""
#     id: Optional[int] = Field(default=None, primary_key=True)
#     contracts: List["Contract"] = Relationship(back_populates="billing_cycle")
#     # TODO: billing time
#     # TODO: billing period


class Contract(SQLModel, table=True):
    """A contract defines the business conditions of a project"""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    date: datetime.datetime
    # Contract n:1 Client
    client_id: Optional[int] = Field(default=None, foreign_key="client.id")
    client: Client = Relationship(back_populates="contracts")
    rate: Rate

    # billing_cycle: BillingCycle = Relationship(back_populates="contracts")
    # rate: Optional[Rate]
    # projects: List["Project"] = Relationship(back_populates="contract")
    # invoices: List["Invoice"] = Relationship(back_populates="contract")


class Project(SQLModel, table=True):
    """A project is a group of contract work for a client."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    # Project m:n Contract
    contract: Contract = Relationship(back_populates="projects")
    # Project 1:n Timesheet
    timesheets: List["Timesheet"] = Relationship(back_populates="project")
    # volume
    volume: Optional[int]  # TODO: project volume


class Timesheet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Timesheet n:1 Project
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    project: Project = Relationship(back_populates="timesheets")

    # period: str
    # client: str
    # comment: str


class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Invoice 1:n Timesheet
    timesheet_id: Optional[int] = Field(default=None, foreign_key="timesheet.id")
    timesheet: Timesheet = Relationship(back_populates="invoice")
    # Invoice n:1 Contract
    contract_id: Optional[int] = Field(default=None, foreign_key="contract.id")
    contract: Contract = Relationship(back_populates="invoices")
    date: datetime.date
    due_date: datetime.date
    sent_date: datetime.date
    sent: bool
    paid: bool
    cancelled: bool
    # payment: Optional["Payment"] = Relationship(back_populates="invoice")

    # invoice items
    items: List["InvoiceItem"] = Relationship(back_populates="invoice")

    #
    total: Decimal
    VAT_total: Decimal


class InvoiceItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    #
    invoice_id: Optional[int] = Field(default=None, foreign_key="invoice.id")
    amount: int
    text: str
    unit: str
    unit_price: int  # TODO: Money
    VAT_rate: float


# class Payment(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     # invoice: Invoice = Relationship(back_populates="payment")


class Cycle:
    pass

    # TODO: monthly, quarterly, yearly...


class Tax:
    country: str
    cycle: Cycle


class ValueAddedTax(Tax):
    """Value added tax."""

    pass


class IncomeTax(Tax):
    """Income tax."""

    pass


if __name__ == "__main__":

    central_services = Client(
        name="Central Services", e_mail="info@centralservices.com"
    )

    my_contract = Contract(client=central_services)

    my_project = Project(name="Ducts", contract=my_contract)

    print(central_services.contracts)
