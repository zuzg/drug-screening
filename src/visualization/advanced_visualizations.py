import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import pandas as pd
import seaborn as sns
import plotly.express as px

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
        width=width, height=height)
    return fig


def plot_projection_3d(df: pd.DataFrame, feature: str, projection: str = 'umap', width:int=1000, height:int=800) -> px.scatter:
    """
    Plot in 3D selected projection and colour points with respect to selected feature.
    
    :param df: DataFrame to be visualized

    :param feature: name of the column with respect to which the plot will be coloured
    
    :param projection: name of projection to be visualized

    :param width: plot's width

    :param height: plot's height

    """
    fig = px.scatter_3d(
        df,  
        x=f'{str.upper(projection)}_X',  
        y=f'{str.upper(projection)}_Y',
        z=f'{str.upper(projection)}_Z',
        color=df[feature],
        range_color=[0,df[feature].max()],
        labels={
            f'{str.upper(projection)}_X': 'X',
            f'{str.upper(projection)}_Y': 'Y',
            f'{str.upper(projection)}_Z': 'Z',
            'CMPD ID':'Compound ID'
        },
        title=f'{str.upper(projection)} 3D projection with respect to {feature}',
        width=width, height=height)
    fig.update_traces(marker={'size':3})
    return fig

