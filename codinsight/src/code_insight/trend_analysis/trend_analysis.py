from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from code_insight.code_analysis.abstract import BaseAnalysisResult


class TrendAnalysis:
    """
    コード解析結果分析

    Attributes
    ----------
    code_labels : list[str]
        コードラベルのリスト
    code_analysis_list : list[dict[str, float]]
        コード解析結果のリスト
    """

    code_labels: list[str]
    code_analysis_list: list[dict[str, float]]

    def __init__(
        self,
        code_analysis_results: Sequence[Sequence[BaseAnalysisResult]],
        code_labels: list[str] | None = None,
    ) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        code_analysis_results : Sequence[Sequence[BaseAnalysisResult]]
            コード解析結果のシーケンス
        code_labels : list[str] | None, optional
            コードラベルのリスト, by default None
        """
        self.code_labels = code_labels if code_labels else []
        self.code_analysis_list: list[dict[str, float]] = [
            {
                **{
                    k: float(v)
                    for d in [res.model_dump() for res in code_analysis_result]
                    for k, v in d.items()
                }
            }
            for code_analysis_result in code_analysis_results
        ]

    def extract_value(self, keys: list[str] | None = None) -> np.ndarray:
        """
        任意のkeyの値を抽出

        Parameters
        ----------
        keys : list[str] | None, optional
            抽出するキーのリスト, by default None

        Returns
        -------
        np.ndarray
            抽出された値の配列

        Notes
        -----
        keysが空ならすべてのkeyを抽出する
        """
        if not keys:
            return np.array(
                [
                    [value for value in code_analysis.values()]
                    for code_analysis in self.code_analysis_list
                ]
            )

        return np.array(
            [
                [code_analysis[key] for key in keys]
                for code_analysis in self.code_analysis_list
            ]
        )

    def compress(self, keys: list[str] | None = None, dimention: int = 2) -> np.ndarray:
        """
        任意のkeyの値を圧縮

        Parameters
        ----------
        keys : list[str] | None
            圧縮するキーのリスト, by default None
        dimention : int
            圧縮後の次元数, by default 2

        Returns
        -------
        np.ndarray
            圧縮された値の配列
        """
        pca = PCA(n_components=dimention)
        return pca.fit_transform(self.extract_value(keys))

    def cluster_values(
        self, keys: list[str] | None = None, cluster: int = 2
    ) -> np.ndarray:
        """
        任意のkeyの値をクラスタリング

        Parameters
        ----------
        keys : list[str] | None
            クラスタリングするキーのリスト, by default None
        cluster : int
            クラスタ数, by default 2

        Returns
        -------
        np.ndarray
            クラスタリング結果の配列
        """
        kmeans = KMeans(n_clusters=cluster)
        return kmeans.fit_predict(self.extract_value(keys))

    def output_image(
        self,
        output_file: str = "clusters.png",
        keys: list[str] | None = None,
        cluster: int = 2,
        dimention: int = 2,
    ) -> None:
        """
        任意のkeyの値を圧縮して画像として出力

        Parameters
        ----------
        output_file : str
            出力ファイル名, by default "clusters.png"
        keys : list[str] | None
            処理するキーのリスト, by default None
        cluster : int
            クラスタ数, by default 2
        dimention : int
            次元数, by default 2
        """
        X = self.extract_value(keys)

        # KMeansクラスタリング
        kmeans = KMeans(n_clusters=cluster, random_state=42)
        cluster_labels = kmeans.fit_predict(X)

        # 高次元なら2次元に圧縮して可視化 (PCA)
        if X.shape[1] > 2:
            X_vis = PCA(n_components=dimention).fit_transform(X)
        else:
            X_vis = X

        # プロット
        plt.figure(figsize=(8, 6))
        for c in range(cluster):
            idx = cluster_labels == c
            plt.scatter(X_vis[idx, 0], X_vis[idx, 1], label=f"Cluster {c}", alpha=0.6)
            # 各点にラベルを描画
            for i in np.where(idx)[0]:
                plt.text(
                    X_vis[i, 0] + 0.02,
                    X_vis[i, 1] + 0.02,
                    self.code_labels[i],
                    fontsize=8,
                )

        plt.title("Clustering Result")
        plt.legend(title="Clusters")
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        plt.close()
