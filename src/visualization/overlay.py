import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def projection_plot_overlay_controls(
    fig: go.Figure,
    controls: dict[pd.DataFrame],
    projection: str = "umap",
    cvd: bool = False,
) -> go.Figure:
    """
    Add control values to the plot of selected projection.

    :param fig: projection plot
    :param controls: dictionary containing data frames with projected control values (positive and negative respectively)
    :param projection: name of projection to be visualized
    :param cvd: whether the plot is for CVD or not
    :return: plotly express scatter plot with control values
    """
    fig_controls = go.Figure(fig)
    fig_controls.update_traces(marker={"opacity": 0.6})

    if cvd:
        control_styles = {
            "all_pos": ["#018571", 12],
            "all_but_one_pos": ["#80cdc1", 10],
            "all_but_one_neg": ["#dfc27d", 10],
            "all_neg": ["#a6611a", 12],
        }
    else:
        control_styles = {
            "all_pos": ["#488f31", 12],
            "all_but_one_pos": ["#8aac49", 10],
            "all_but_one_neg": ["#eb7a52", 10],
            "all_neg": ["#de425b", 12],
        }

    for key in control_styles.keys():
        fig_controls.add_scatter(
            x=controls[key][f"{projection.upper()}_X"],
            y=controls[key][f"{projection.upper()}_Y"],
            mode="markers",
            marker=dict(
                size=control_styles[key][1],
                color=control_styles[key][0],
                symbol="star-diamond",
            ),
            name=str.upper(key).replace("_", " "),
            text=controls[key]["CMPD ID"].str.split(";"),
            hovertemplate="<b>%{text[0]}</b><br>"
            + "<b>%{text[1]}</b><br>"
            + "X: %{x:.4f}<br>Y: %{y:.4f}<br>"
            + "<extra></extra>",
        )
    fig_controls.update_layout(
        legend=dict(
            title="   CONTROLS",
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
