from typing import Sequence

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from code_insight.code_analysis.abstract import BaseAnalysisResult


class TrendAnalysis:
    """コード解析結果分析"""

    code_analysis: list[dict[str, float]]

    def __init__(
        self, code_analysis_results: Sequence[Sequence[BaseAnalysisResult]]
    ) -> None:
        """コンストラクタ"""
        self.code_analysis: list[dict[str, float]] = [
            {
                **{
                    k: float(v)
                    for d in [res.model_dump() for res in code_analysis_result]
                    for k, v in d.items()
                }
            }
            for code_analysis_result in code_analysis_results
        ]

    def extract_value(self, keys: list[str]) -> np.ndarray:
        """任意のkeyの値を抽出"""
        return np.array([[d[key] for key in keys] for d in self.code_analysis])

    def compress(self, keys: list[str], dimention: int = 2) -> np.ndarray:
        """任意のkeyの値を圧縮"""
        pca = PCA(n_components=dimention)
        return pca.fit_transform(self.extract_value(keys))

    def cluster_values(self, keys: list[str], cluster: int = 2) -> np.ndarray:
        """任意のkeyの値をクラスタリング"""
        kmeans = KMeans(n_clusters=cluster)
        return kmeans.fit_predict(self.extract_value(keys))
