import numpy as np
import pandas as pd
import plotly.graph_objs as go

PLOTLY_TEMPLATE = "plotly_white"


def prepare_data_plot(df, well, col):
    df = df.groupby(well)[col].agg(["mean", "std"]).reset_index()
    df["lb"] = df["mean"] - df["std"]
    df["ub"] = df["mean"] + df["std"]

    # Add 'pos' column -> pos = position (eg. B01 = 1*24+1)
    df["pos"] = df[well].apply(lambda x: (ord(x[0]) - ord("A")) * 24 + int(x[1:]))
    df = df.sort_values("pos")

    return df


def plot_zscore(
    compounds_df: pd.DataFrame,
    control_pos_df: pd.DataFrame,
    control_neg_df: pd.DataFrame,
    z_score_limits: tuple = None,
) -> go.Figure:
    WELL = "Destination Well"
    Z_SCORE = "Z-SCORE"
    fig = go.Figure()

    compounds_df = prepare_data_plot(compounds_df, WELL, Z_SCORE)
    control_pos_df = prepare_data_plot(control_pos_df, WELL, Z_SCORE)
    control_neg_df = prepare_data_plot(control_neg_df, WELL, Z_SCORE)

    # to be updated
    dfs = [compounds_df, control_pos_df, control_neg_df]
    colors = ["rgb(66,167,244)", "rgb(0,255,0)", "rgb(255,0,0)"]
    colors_shade = ["rgba(66,167,244,0.4)", "rgba(0,255,0,0.2)", "rgba(255,0,0,0.2)"]
    names = ["COMPOUNDS", "CONTROL POS", "CONTROL NEG"]

    for i, df in enumerate(dfs):
        fig.add_trace(
            go.Scatter(
                x=df["pos"],
                y=df["mean"],
                line=dict(color=colors[i]),
                mode="lines",
                name=names[i],
                legendgroup=names[i],
                hovertemplate=f"{WELL}: %{{x}}<br>z-score: %{{y:.2f}}<extra></extra>",  # TO IMPROVE
            )
        )

        fig.add_trace(
            go.Scatter(
                x=pd.concat(
                    [df["pos"], df["pos"][::-1]], ignore_index=True
                ),  # well, then well reversed
                y=pd.concat(
                    [df["ub"], df["lb"][::-1]], ignore_index=True
                ),  # upper, then lower reversed
                fill="toself",
                fillcolor=colors_shade[i],
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                showlegend=False,
                name="Shaded Area",
                legendgroup=names[i],
            )
        )

    fig.update_xaxes(showticklabels=False)
    fig.update_layout(
        title=f"Z-score plot",
        xaxis_title="Well",
        yaxis_title="z-score",
        margin=dict(t=50, b=30, l=30, r=30),
        template=PLOTLY_TEMPLATE,
    )

    if z_score_limits is not None:
        fig.add_hline(
            y=z_score_limits[0],
            line_width=3,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"MIN: {z_score_limits[0]:.2f}",
            annotation_font_color="gray",
        )
        fig.add_hline(
            y=z_score_limits[1],
            line_width=3,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"MAX: {z_score_limits[1]:.2f}",
            annotation_font_color="gray",
        )

    return fig
