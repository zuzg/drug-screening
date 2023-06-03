import numpy as np
import pandas as pd
import plotly.graph_objs as go

PLOTLY_TEMPLATE = "plotly_white"


def prepare_data_plot(df, well, col, id_pos="index", range_max=None):
    df = df.groupby(well)[col].agg(["mean", "std"]).reset_index()
    if df["std"].isna().any():
        df["std"] = 0.0
        df["lb"] = df["mean"]
        df["ub"] = df["mean"]
    else:
        df["lb"] = df["mean"] - df["std"]
        df["ub"] = df["mean"] + df["std"]
    df = df.sort_values("mean")

    if range_max is not None:
        x_positions = [0]
        frac = range_max / len(df)
        i = frac
        while i < range_max:
            x_positions.append(i)
            i += frac
        df[id_pos] = x_positions
    else:
        #     df[id_pos] = range(0, no_items, no_items/len(df))
        df[id_pos] = range(len(df))

    return df


def plot_zscore(
    compounds_df: pd.DataFrame,
    control_pos_df: pd.DataFrame,
    control_neg_df: pd.DataFrame,
    z_score_limits: tuple = None,
) -> go.Figure:
    id_pos = "index"
    PLATE = "Destination Plate Barcode"
    WELL = "Destination Well"
    Z_SCORE = "Z-SCORE"
    fig = go.Figure()

    if z_score_limits:
        mask = (compounds_df[Z_SCORE] >= z_score_limits[0]) & (
            compounds_df[Z_SCORE] <= z_score_limits[1]
        )
        compounds_outside_df = compounds_df[~mask].copy()

    else:
        z_score_limits = compounds_df[Z_SCORE].min(), compounds_df[Z_SCORE].max()
        compounds_outside_df = None

    # TBD: preserve this data somewhere
    plot_compounds_df = prepare_data_plot(compounds_df, WELL, Z_SCORE)
    range_max = len(plot_compounds_df)
    plot_control_pos_df = prepare_data_plot(
        control_pos_df, WELL, Z_SCORE, range_max=range_max
    )
    plot_control_neg_df = prepare_data_plot(
        control_neg_df, WELL, Z_SCORE, range_max=range_max
    )

    # to be updated
    dfs = [plot_control_pos_df, plot_control_neg_df, plot_compounds_df]
    colors = ["rgb(0,128,0)", "rgb(255,0,0)", "rgb(31, 119, 180)"]
    colors_shade = ["rgba(0,128,0,0.2)", "rgba(255,0,0,0.2)", "rgba(31, 119, 180,0.4)"]
    names = ["CONTROL POS", "CONTROL NEG", "COMPOUNDS"]

    for i, df in enumerate(dfs):
        fig.add_trace(
            go.Scatter(
                x=df[id_pos],
                y=df["mean"],
                line=dict(color=colors[i]),
                mode="lines",
                name=names[i],
                legendgroup=names[i],
                customdata=np.stack((df[WELL], df["std"]), axis=-1),
                hovertemplate="well: %{customdata[0]}<br>avg z-score: %{y:.2f} &plusmn;%{customdata[1]:.2f}<extra></extra>",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=pd.concat(
                    [df[id_pos], df[id_pos][::-1]], ignore_index=True
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

    if compounds_outside_df is not None:
        compounds_outside_df = compounds_outside_df.merge(
            plot_compounds_df[[WELL, id_pos]], on=WELL
        )
        fig.add_trace(
            go.Scatter(
                x=compounds_outside_df[id_pos],
                y=compounds_outside_df[Z_SCORE],
                mode="markers",
                marker=dict(color="rgb(31, 119, 180)", size=8),
                name="COMPOUNDS OUTSIDE",
                customdata=np.stack(
                    (compounds_outside_df[PLATE], compounds_outside_df[WELL]), axis=-1
                ),
                hovertemplate="plate: %{customdata[0]}<br>well: %{customdata[1]}<br>z-score: %{y:.2f}<extra>CMPD ID</extra>",
            )
        )

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

    fig.update_xaxes(showticklabels=False)
    fig.update_layout(
        title=f"Z-score plot",
        # xaxis_title="Well",
        xaxis=dict(
            {
                "title": "Well",
                "visible": True,
                "showticklabels": True,
                "tickfont": {"size": 1, "color": "rgba(0,0,0,0)"},
            }
        ),
        yaxis_title="z-score",
        margin=dict(t=50, b=30, l=30, r=30),
        template=PLOTLY_TEMPLATE,
    )

    return fig
