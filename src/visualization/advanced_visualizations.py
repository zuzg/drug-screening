import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def histogram_control_value(df: pd.DataFrame, feature: str, control_pos: str, control_neg: str) -> sns.displot:
    """
    Plot histogram for one dataset with positive and negative control values.

    :param df: DataFrame to be visualized

    :param feature: name of column to be visualized

    :param control_pos: name of positive control feature

    :param control_neg: name of negative control feature

    :return: distribution plot for the passed feature and control values
    """
    histogram = sns.histplot(df, x=df[feature], kde=True)
    histogram.vlines(df[control_neg], 0, 1300, colors='red',
                     linestyles='dotted', label="negative")
    histogram.vlines(df[control_pos], 0, 1300, colors='green',
                     linestyles='dotted', label='positive')
    histogram.set(title=f"Histogram for {feature} with control values")

    return histogram


def scatter_2d(df: pd.DataFrame, feature_x: str, feature_y: str) -> sns.scatterplot:
    """
    Plot histogram for two datasets.

    :param df: DataFrame to be visualized

    :param feature_x: name of feature for x-axis

    :param feature_y: name of feature for y-axis

    :return: scatter plot for the passed data
    """
    scatter = sns.scatterplot(
        df, x=feature_x, y=feature_y, hue='Barcode_prefix')
    scatter.set(title=f"Scatter plot for {feature_x} and {feature_y}")

    return scatter


def plot_umap(X_umap: np.ndarray, y: np.ndarray) -> None:
    """
    Show scatter plot for the UMAP data

    :param X_umap: DataFrame to be visualized

    :param y: name of feature for x-axis

    :return: scatter plot for UMAP
    """
    plt.scatter(
        X_umap[:, 0],
        X_umap[:, 1],
        c=y, cmap='Spectral', s=5)
    plt.gca().set_aspect('equal', 'datalim')
    plt.title('UMAP projection of assays', fontsize=16)
    plt.show()


def plot_projections(X_umap: np.ndarray, df: pd.DataFrame) -> None:
    """
    Show scatter plots for the UMAP data, colored by activation/inibition in each assay

    :param X_umap: DataFrame to be visualized

    :param y: name of feature for x-axis

    :return: scatter plot for UMAPs
    """
    fig, axs = plt.subplots(nrows=3, ncols=3, figsize=(18, 16))
    fig.suptitle('UMAP projection of assays', fontsize=16)

    for col, i, ax in zip(df.columns[1:], range(9), axs.ravel()):
        ax.scatter(
            X_umap[:, 0],
            X_umap[:, 1],
            c=df[col], cmap='coolwarm', s=5)
        ax.set_title(col)
        norm = plt.Normalize(df[col].min(), df[col].max())
        sm = ScalarMappable(norm=norm, cmap='coolwarm')
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax)
    plt.show()

def plot_projection_2d(df: pd.DataFrame, feature: str, projection: str = 'umap', width:int=800, height:int=600) -> px.scatter:
    """
    Plot selected projection and colour points with respect to selected feature.
    
    :param df: DataFrame to be visualized

    :param feature: name of the column with respect to which the plot will be coloured
    
    :param projection: name of projection to be visualized

    :param width: plot's width

    :param height: plot's height

    """
    fig = px.scatter(
        df,  
        x=f'{str.upper(projection)}_X',  
        y=f'{str.upper(projection)}_Y',
        text='CMPD ID',
        color=df[feature],
        range_color=[0,df[feature].max()],
        labels={
            f'{str.upper(projection)}_X': 'X',
            f'{str.upper(projection)}_Y': 'Y',
            'CMPD ID':'Compound ID'
        },
        title=f'{str.upper(projection)} projection with respect to {feature}',
        width=width, height=height,
        hover_data={'CMPD ID':True,
                    f'{str.upper(projection)}_X':':.3f',
                    f'{str.upper(projection)}_Y':':.3f',
                    feature:':.3f'})


    fig.update_yaxes(
        title_standoff = 15,
        automargin=True)
    fig.update_xaxes(
        title_standoff = 30,
        automargin=True)
    fig.update_layout(
        modebar=dict(orientation="v"),
        margin=dict(r=35, l=15, b=0),
        title_x=0.5, 
        coloraxis_colorbar=dict(
            orientation='h', 
            thickness=15)
    )
    return fig


def projection_2d_add_controls(fig: px.scatter, controls: dict[pd.DataFrame], projection: str = 'umap', cvd: bool = False) -> px.scatter:
    """
    Add control values to the plot of selected projection.
    
    :param fig: projection plot

    :param controls: dictionary containing data frames with projected control values (positive and negative respectively)
    
    :param projection: name of projection to be visualized

    """
    fig_controls = go.Figure(fig)
    fig_controls.update_traces(marker={"opacity": 0.6})

    if cvd:
        control_styles = {
            'all_pos': ['#018571',12],
            'all_but_one_pos': ['#80cdc1',10],  
            'all_but_one_neg': ['#dfc27d',10],
            'all_neg': ['#a6611a',12], 
        }
    else:
        control_styles = {
            'all_pos': ['#488f31',12],
            'all_but_one_pos': ['#8aac49',10],  
            'all_but_one_neg': ['#eb7a52',10],
            'all_neg': ['#de425b',12], 
        }
    
    for key in control_styles.keys():
        fig_controls.add_scatter(
                    x=controls[key][f'{str.upper(projection)}_X'],
                    y=controls[key][f'{str.upper(projection)}_Y'], 
                    mode='markers',
                    marker=dict(size=control_styles[key][1], color=control_styles[key][0], symbol='star-diamond'),
                    name= str.upper(key).replace('_',' '),
                    text = controls[key]['CMPD ID'].str.split(';'),
                    hovertemplate="<b>%{text[0]}</b><br>" +
                    "<b>%{text[1]}</b><br>" +
                    "X: %{x:.4f}<br>Y: %{y:.4f}<br>"+
                    "<extra></extra>")
    fig_controls.update_layout(
        legend=dict(
        title="   CONTROLS",
        yanchor="bottom",
        y=0.01,
        xanchor="left",
        x=0.01,
        font=dict(size=10),
        bgcolor='rgba(255,255,255,0.5)'),
        title_x=0.5)
    return fig_controls