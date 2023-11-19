import plotly.graph_objects as go
import pandas as pd


def projection_plot_overlay_controls(
    fig: go.Figure,
    controls_df: pd.DataFrame,
    style_dict: dict[str, list[str, int]],
    projection: str = "pca",
    plot_3d: bool = False,
) -> go.Figure:
    """
    Add control values to the plot of selected projection.

    :param fig: projection plot
    :param controls_df: dataframe with control values
    :param style_dict: dictionary with styles (color and font size) for each annotation
    :param projection: name of projection to be visualized
    :param plot_3d: if True, plot 3D projection
    :return: plotly express scatter plot with control values
    """
    fig_controls = go.Figure(fig)
    fig_controls.update_traces(marker={"opacity": 0.6})
    overlay_func = fig_controls.add_scatter
    if plot_3d:
        overlay_func = fig_controls.add_scatter3d
    for name, group in controls_df.groupby("annotation"):
        if name not in style_dict:
            continue
        color, size = style_dict[name]
        extra_arg = dict()
        hovertemplate = (
            "<b> %{text[0]}</b><br>"
            + "<b>%{text[1]}</b><br>"
            + "X: %{x:.4f}<br>Y: %{y:.4f}<br>"
        )
        if plot_3d:
            extra_arg["z"] = group[f"{projection.upper()}_Z"]
            hovertemplate += "Z: %{z:.4f}<br>"
        hovertemplate += "<extra></extra>"
        overlay_func(
            x=group[f"{projection.upper()}_X"],
            y=group[f"{projection.upper()}_Y"],
            mode="markers",
            marker=dict(
                size=size,
                color=color,
                symbol="diamond",
            ),
            name=str.upper(name).replace("_", " "),
            text=group["EOS"].str.split(";"),
            hovertemplate=hovertemplate,
            **extra_arg,
        )

    fig_controls.update_layout(
        legend=dict(
            title="CONTROLS",
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.5)",
        ),
        title_x=0.5,
    )
    return fig_controls
