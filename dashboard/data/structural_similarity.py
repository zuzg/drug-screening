from typing import List, Optional, Tuple

import hdbscan
import numpy as np
import pandas as pd
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
        if ecfp is not None:
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


def calculate_umap(descriptors: np.ndarray, n_components: int = 2) -> np.ndarray:
    """
    Calculate UMAP projection

    :param descriptors: descriptors
    :param n_components: number of components to project to
    :return: array with projection
    """
    umap_model = umap.UMAP(
        metric="jaccard",
        n_neighbors=25,
        n_components=n_components,
        low_memory=False,
        min_dist=0.001,
    )
    X_umap = umap_model.fit_transform(descriptors)
    return X_umap


def calculate_pca(descriptors: np.ndarray, n_components: int = 2) -> np.ndarray:
    """
    Calculate PCA projection

    :param descriptors: descriptors
    :param n_components: number of components to project to
    :return: array with projection
    """
    pca_model = PCA(n_components=n_components)
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
    preds = hdbscan_model.fit_predict(x_projection)
    clusters = [f"c{x}" if x != -1 else "outlier" for x in preds]
    return clusters


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
    df["UMAP_X"], df["UMAP_Y"] = X_umap[:, 0], X_umap[:, 1]
    df["cluster_UMAP"] = calculate_clusters(X_umap)

    X_umap_3d = calculate_umap(ecfp_descriptors, n_components=3)
    df["UMAP3D_X"], df["UMAP3D_Y"], df["UMAP3D_Z"] = (
        X_umap_3d[:, 0],
        X_umap_3d[:, 1],
        X_umap_3d[:, 2],
    )
    df["cluster_UMAP3D"] = calculate_clusters(X_umap_3d)

    X_pca = calculate_pca(ecfp_descriptors, 3)
    df["PCA_X"], df["PCA_Y"], df["PCA_Z"] = X_pca[:, 0], X_pca[:, 1], X_pca[:, 2]
    df["cluster_PCA"] = calculate_clusters(X_pca)
    return df
