import numpy as np
import pandas as pd
import plotly.graph_objs as go

PLOTLY_TEMPLATE = "plotly_white"


# TODO: move it to echo file parser (then no need for saving .pq twice)
def get_well_stats(df, well, col, id_pos="id_pos", range_max=None):
    """
    Returns dataframe with well statistics.

    :param df: dataframe with well statistics
    :param well: well column name
    :param col: column name with values (z-score)
    :param id_pos: column name with position id
    :param range_max: maximum value of x-axis
    :return: dataframe with well statistics
    """
    df = df.groupby(well)[col].agg(["mean", "std", "min", "max"]).reset_index()
    if df["std"].isna().any():
        df["std"] = 0.0
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
        df[id_pos] = range(len(df))
    return df


def plot_zscore(
    compounds_df: pd.DataFrame,
    control_pos_df: pd.DataFrame,
    control_neg_df: pd.DataFrame,
    z_score_limits: tuple = None,
) -> go.Figure:
    id_pos = "id_pos"
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

    plot_compounds_df = get_well_stats(compounds_df, WELL, Z_SCORE)
    range_max = len(plot_compounds_df)
    plot_control_pos_df = get_well_stats(
        control_pos_df, WELL, Z_SCORE, range_max=range_max
    )
    plot_control_neg_df = get_well_stats(
        control_neg_df, WELL, Z_SCORE, range_max=range_max
    )

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
                    [df["max"], df["min"][::-1]], ignore_index=True
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
    else:
        fig.add_trace(
            go.Scatter(
                x=list(),
                y=list(),
                mode="markers",
                marker=dict(color="rgb(31, 119, 180)", size=8),
                name="COMPOUNDS OUTSIDE",
            )
        )

    fig.add_hline(
        y=z_score_limits[0],
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text=f"MIN: {z_score_limits[0]:.2f}",
        annotation_font_color="red",
    )
    fig.add_hline(
        y=z_score_limits[1],
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text=f"MAX: {z_score_limits[1]:.2f}",
        annotation_font_color="red",
    )

    fig.update_xaxes(showticklabels=False)
    fig.update_layout(
        title=f"Z-score plot",
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

    compounds_df = compounds_df.merge(
        plot_compounds_df[[WELL, id_pos]], how="left", on=WELL
    )
    print("COMPOUNDS DF")
    print(compounds_df.head())
    control_pos_df[id_pos] = np.nan
    control_neg_df[id_pos] = np.nan
    result = pd.concat([compounds_df, control_pos_df, control_neg_df])

    return fig, result
