import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_projection_2d(
    df: pd.DataFrame,
    feature: str,
    projection: str = "umap",
    width: int = 800,
    height: int = 600,
) -> go.Figure:
    """
    Plot selected projection and colour points with respect to selected feature.

    :param df: DataFrame to be visualized
    :param feature: name of the column with respect to which the plot will be coloured
    :param projection: name of projection to be visualized
    :param width: plot's width
    :param height: plot's height
    :return: plotly express scatter plot
    """
    projection_x = f"{projection.upper()}_X"
    projection_y = f"{projection.upper()}_Y"
    fig = px.scatter(
        df,
        x=projection_x,
        y=projection_y,
        text="CMPD ID",
        color=df[feature],
        range_color=[0, df[feature].max()],
        labels={
            projection_x: "X",
            projection_y: "Y",
            "CMPD ID": "Compound ID",
        },
        title=f"{projection.upper()} projection with respect to {feature}",
        width=width,
        height=height,
        hover_data={
            "CMPD ID": True,
            projection_x: ":.3f",
            projection_y: ":.3f",
            feature: ":.3f",
        },
    )

    fig.update_yaxes(title_standoff=15, automargin=True)
    fig.update_xaxes(title_standoff=30, automargin=True)
    fig.update_layout(
        modebar=dict(orientation="v"),
        margin=dict(r=35, l=15, b=0),
        title_x=0.5,
        coloraxis_colorbar=dict(orientation="h", thickness=15),
    )
    return fig
