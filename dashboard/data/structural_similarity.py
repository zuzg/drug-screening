from typing import List, Optional, Tuple

import hdbscan
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import umap
from rdkit import Chem
from rdkit.Chem import AllChem

from sklearn.decomposition import PCA


def _compute_single_ecfp_descriptor(smiles: str) -> Optional[np.ndarray]:
    """
    Calculate ecfp descriptor for single smiles

    :param smiles: smiles
    :return: ecfp descriptor
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
        return np.array(fp)
    return None


def compute_ecfp_descriptors(smiles_list: List[str]) -> Tuple[np.ndarray, int]:
    """
    Calculate ecfp descriptor for list of smiles

    :param smiles: list of smiles
    :return: ecfp descriptors and indices of correct descriptors
    """
    keep_idx = []
    descriptors = []
    for i, smiles in enumerate(smiles_list):
        ecfp = _compute_single_ecfp_descriptor(smiles)
        if ecfp:
            keep_idx.append(i)
            descriptors.append(ecfp)
    return np.vstack(descriptors), keep_idx


def merge_active_new(
    activity: pd.DataFrame, smiles_active: pd.DataFrame, smiles_new: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge dataframes

    :param activity: df with activity calculated
    :param smiles_active: df with smiles of active compounds
    :param smiles_new: new smiles to cluster
    :return: merged df
    """
    merged = smiles_active.merge(activity, on="EOS")
    smiles_new["activity_final"] = "not tested"
    smiles_new = smiles_new.rename(columns={"eos": "EOS"})
    merged = pd.concat([merged, smiles_new])
    merged = merged.drop_duplicates(subset=["EOS"])
    return merged


def calculate_umap(descriptors: np.ndarray) -> np.ndarray:
    """
    Calculate UMAP projection

    :param descriptors: descriptors
    :return: array with projection
    """
    umap_model = umap.UMAP(
        metric="jaccard",
        n_neighbors=25,
        n_components=2,
        low_memory=False,
        min_dist=0.001,
    )
    X_umap = umap_model.fit_transform(descriptors)
    return X_umap


def calculate_pca(descriptors: np.ndarray) -> np.ndarray:
    """
    Calculate PCA projection

    :param descriptors: descriptors
    :return: array with projection
    """
    pca_model = PCA(n_components=2)
    X_pca = pca_model.fit_transform(descriptors)
    return X_pca


def calculate_clusters(x_projection: np.ndarray) -> np.ndarray:
    """
    Calculate hdbscan clusters

    :param x_projection: array with projected data
    :return: array with clusters
    """
    hdbscan_model = hdbscan.HDBSCAN(
        min_cluster_size=20, min_samples=20, cluster_selection_method="eom"
    )

    return hdbscan_model.fit_predict(x_projection)


def prepare_cluster_viz(
    activity: pd.DataFrame, smiles_active: pd.DataFrame, smiles_new: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge dataframes, calculate projections and clusters

    :param activity: df with activity calculated
    :param smiles_active: df with smiles of active compounds
    :param smiles_new: new smiles to cluster
    :return: df with everything calculated
    """
    df = merge_active_new(activity, smiles_active, smiles_new)
    ecfp_descriptors, keep_idx = compute_ecfp_descriptors(df["smiles"])
    df = df.iloc[keep_idx]
    X_umap = calculate_umap(ecfp_descriptors)
    df["UMAP_0"], df["UMAP_1"] = X_umap[:, 0], X_umap[:, 1]
    df["cluster_UMAP"] = calculate_clusters(X_umap)
    X_pca = calculate_pca(ecfp_descriptors)
    df["PCA_0"], df["PCA_1"] = X_pca[:, 0], X_pca[:, 1]
    df["cluster_PCA"] = calculate_clusters(X_pca)
    return df


def plot_clustered_smiles(
    df: pd.DataFrame,
    feature: str = "activity_final",
    projection: str = "PCA",
) -> go.Figure:
    """
    Plot selected projection and colour points with respect to selected feature.

    :param df: DataFrame to be visualized
    :param feature: name of the column with respect to which the plot will be coloured
    :param projection: name of projection to be visualized

    :return: plotly express scatter plot
    """
    projection_x = f"{projection.upper()}_0"
    projection_y = f"{projection.upper()}_1"
    clusters = f"cluster_{projection}"
    fig = px.scatter(
        df,
        x=projection_x,
        y=projection_y,
        color=feature,
        color_discrete_sequence=["rgb(0,128,0)", "yellow", "rgb(31, 119, 180)"],
        symbol=clusters,
        opacity=0.5,
        labels={
            projection_x: "X",
            projection_y: "Y",
            "EOS": "EOS",
            feature: "activity",
        },
        title=f"{projection.upper()} projection of SMILES with respect to activity",
        hover_data={
            "EOS": True,
            projection_x: ":.3f",
            projection_y: ":.3f",
            feature: True,
            clusters: ":.3d",
        },
    )

    fig.update_yaxes(title_standoff=15, automargin=True)
    fig.update_xaxes(title_standoff=30, automargin=True)
    fig.update_layout(
        modebar=dict(orientation="v"),
        margin=dict(r=35, l=15, b=0),
        title_x=0.5,
        template="plotly_white",
    )
    return fig
