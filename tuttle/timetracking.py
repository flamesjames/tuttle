from dataclasses import dataclass
import datetime
from tabnanny import check

import pandas
from pandera import check_io
from pandera.typing import DataFrame


from . import schema
from .calendar import Calendar, CloudCalendar, FileCalendar
from .model import Project


@dataclass
class Timesheet:
    """dataframe-based timesheet"""

    table: pandas.DataFrame
    period: str
    client: str
    comment: str = None

    def total(self):
        total_hours = self.table["hours"].sum()
        return total_hours


def generate_timesheet(
    cal: Calendar,
    period: str,
    client: str,
    comment: str,
) -> Timesheet:
    # convert cal to data
    cal_data = cal.to_data()

    ts_table = (
        cal_data.loc[period]
        .query(f"title == '{client}'")
        .filter(["duration"])
        .sort_index()
    )

    ts_table = ts_table.groupby(by=ts_table.index.date).sum()
    ts_table["hours"] = (
        ts_table["duration"]
        .dt.components["hours"]
        .add((ts_table["duration"].dt.components["days"] * 24))
    )
    ts_table = (
        ts_table.assign(**{"comment": comment})
        # .reset_index()
        .filter(["hours", "comment"])  #
        .reset_index()
        .rename(columns={"index": "date"})
    )

    ts_table["date"] = pandas.to_datetime(ts_table["date"])
    ts_table = ts_table.set_index("date")

    ts = Timesheet(period=period, client=client, comment=comment, table=ts_table)

    return ts


def export_timesheet(
    timesheet: Timesheet,
    path: str,
):
    table = timesheet.table
    table = table.reset_index()
    table["date"] = table["date"].dt.strftime("%Y/%m/%d")
    table.loc["Total", :] = ("Total", table["hours"].sum(), "")
    table.to_excel(path, index=False)


@check_io(out=schema.time_tracking)
def calendar_to_timetracking_table(cal: Calendar) -> DataFrame:
    """Convert the raw calendar to time tracking data table."""
    if issubclass(type(cal), CloudCalendar):
        cal_data = cal.to_data()
        timetracking_table = cal_data.filter(
            ["begin", "end", "title", "duration"]
        ).rename(columns={"title": "title"})
        # TODO: extract tag
        timetracking_table["tag"] = timetracking_table["title"]
        return timetracking_table
    elif issubclass(cal, FileCalendar):
        raise NotImplementedError()
    else:
        raise NotImplementedError()


def total_time_tracked(by: str) -> DataFrame:
    """Calculate the total time spent, grouped by project, client..."""
    if by == "project":
        raise NotImplementedError()
    elif by == "client":
        raise NotImplementedError()
    else:
        raise ValueError()


@check_io(time_tracking_data=schema.time_tracking)
def progress(
    project: Project,
    time_tracking_data: DataFrame,
):
    tag = project.tag
    total_time = (
        time_tracking_data.filter(["tag", "duration"])
        .query(f"tag == @tag")
        .groupby("tag")
        .sum()
    )
    # TODO: work with project.unit
    budget = project.contract.volume * datetime.timedelta(hours=1)
    return total_time.loc[tag]["duration"] / budget
