import datetime
from typing import List, Optional, Tuple

import matplotlib
from matplotlib import pyplot as plt


def plot_balance(
    data: List[Tuple[str, int, str]],
    title: Optional[str] = None,
    filename: Optional[str] = None,
) -> None:

    matplotlib.rc("font", family="MS Gothic")

    data_income = sorted([entry for entry in data if entry[1] > 0], key=lambda x: x[1])
    data_expense = sorted(
        [(entry[0], -entry[1], entry[2]) for entry in data if entry[1] < 0],
        key=lambda x: x[1],
    )

    fig, ax = plt.subplots(figsize=(10, 15))
    for i in range(len(data_income)):
        ax.bar(0, data_income[i][1], bottom=sum([x[1] for x in data_income[:i]]))
        # text label
        ax.text(
            0,
            sum([x[1] for x in data_income[:i]]) + data_income[i][1] / 2,
            data_income[i][2],
            ha="center",
            va="center",
        )
    for i in range(len(data_expense)):
        ax.bar(1, data_expense[i][1], bottom=sum([x[1] for x in data_expense[:i]]))
        ax.text(
            1,
            sum([x[1] for x in data_expense[:i]]) + data_expense[i][1] / 2,
            data_expense[i][2],
            ha="center",
            va="center",
        )
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Income", "Expense"])
    ax.set_ylabel("Amount (JPY)")
    if title:
        ax.set_title(title)
    if filename:
        plt.savefig(filename)
    else:
        plt.show()


def plot_credit_usage(
    data_usage: List[Tuple[datetime.datetime, str, int, str, str]],
    title: Optional[str] = None,
    filename: Optional[str] = None,
):
    matplotlib.rc("font", family="MS Gothic")

    categories = sorted(list(set([entry[4] for entry in data_usage])))

    data = {}
    for entry in data_usage:
        if entry[4] not in data:
            data[entry[4]] = []
        data[entry[4]].append(entry)
    for key in data.keys():
        data[key] = sorted(data[key], key=lambda x: x[1])

    fig, ax = plt.subplots(figsize=(20, 15))
    for i, category in enumerate(categories):
        for j, entry in enumerate(data[category]):
            ax.bar(
                i,
                entry[2],
                bottom=sum([x[2] for x in data[category][:j]]),
                label=entry[4],
            )
            ax.text(
                i,
                sum([x[2] for x in data[category][:j]]) + entry[2] / 2,
                entry[1],
                ha="center",
                va="center",
            )
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories)
    ax.set_ylabel("Amount (JPY)")
    if title:
        ax.set_title(title)
    else:
        earliest_date = min([entry[0] for entry in data_usage])
        latest_date = max([entry[0] for entry in data_usage])
        ax.set_title("Credit Usage from {} to {}".format(earliest_date, latest_date))
    if filename:
        plt.savefig(filename)
    else:
        plt.show()
