import numpy as np
import pandas as pd


def get_umap(
    df: pd.DataFrame,
    controls: pd.DataFrame,
    target: str,
    scaler: object,
    n_neighbors=10,
    n_components=2,
    min_dist=0.2,
) -> np.ndarray:
    """
    Get UMAP projection for given dataframe.
    :param df: DataFrame with to perform UMAP
    :param target: names of column to be treated as target
    :param scaler: object with which scaling will be performed
    :return: UMAP array
    """
    df_na = df.dropna(inplace=False)
    X = df_na.drop(target, axis=1)
    controls_na = controls.dropna(inplace=False)
    X_ctrl = controls_na.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
        X_ctrl = scaler.fit_transform(X_ctrl)
    umap_transformer = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=min_dist,
        random_state=23,
    )
    X_umap = umap_transformer.fit_transform(X)
    X_ctrl = umap_transformer.transform(X_ctrl)

    return X_umap, X_ctrl


def get_pca(
    df: pd.DataFrame,
    controls: pd.DataFrame,
    target: str,
    scaler: object,
    n_components=2,
) -> np.ndarray:
    """
    Get PCA projection for given dataframe.
    :param df: DataFrame with to perform PCA
    :param target: names of column to be treated as target
    :param scaler: object with which scaling will be performed
    :return: PCA array
    """
    df_na = df.dropna(inplace=False)
    X = df_na.drop(target, axis=1)
    controls_na = controls.dropna(inplace=False)
    X_ctrl = controls_na.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
        X_ctrl = scaler.fit_transform(X_ctrl)
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)
    X_ctrl = pca.transform(X_ctrl)

    return X_pca, X_ctrl


def get_tsne(
    df: pd.DataFrame,
    target: str,
    scaler: object,
    n_components=2,
    learning_rate="auto",
    init="random",
    perplexity=3,
) -> np.ndarray:
    """
    Get t-SNE projection for given dataframe.
    :param df: DataFrame with to perform t-SNE
    :param target: names of column to be treated as target
    :param scaler: object with which scaling will be performed
    :return: t-SNE array
    """
    df_na = df.dropna(inplace=False)
    X = df_na.drop(target, axis=1)
    if scaler:
        X = scaler.fit_transform(X)
    tsne = TSNE(
        n_components=n_components,
        learning_rate=learning_rate,
        init=init,
        perplexity=perplexity,
    )

    X_tsne = tsne.fit_transform(X)

    return X_tsne
