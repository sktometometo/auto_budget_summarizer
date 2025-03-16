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
