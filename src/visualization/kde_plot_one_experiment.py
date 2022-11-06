import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt


def make_KDE_plot(df):
    res = sn.kdeplot(df, x="VALUE", color="blue", fill="True", label="density of value")
    plt.hist(
        x=df["CTRL NEG Mean(VALUE)"],
        density=True,
        bins=len(df["CTRL NEG Mean(VALUE)"].unique()),
        color="red",
        alpha=0.3,
        label="density of control negative mean(VALUE)",
    )
    plt.hist(
        x=df["CTRL POS Mean(VALUE)"],
        density=True,
        bins=len(df["CTRL POS Mean(VALUE)"].unique()),
        color="green",
        alpha=0.3,
        label="density of control positive mean(VALUE)",
    )
    for idx, row in df.iterrows():
        plt.errorbar(
            row["CTRL NEG Mean(VALUE)"],
            0.00012,
            xerr=row["CTRL NEG Standard deviation(VALUE)"],
            yerr=0.000002,
            color="red",
            ls="dotted",
        )
        plt.errorbar(
            row["CTRL POS Mean(VALUE)"],
            0.00012,
            xerr=row["CTRL POS Standard deviation(VALUE)"],
            yerr=0.000002,
            color="green",
            ls="dotted",
        )
    plt.legend(loc="upper right")
    plt.title("KDE plot of value of experiments with mean and std of control")
    return plt
