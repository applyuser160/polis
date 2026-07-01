
from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)

try:
    from codetovec import CodeToVec
except ImportError:
    pass


class VectorAnalysisConfig(BaseAnalysisConfig):
    """
    ベクトル解析の設定

    Attributes
    ----------
    remove_comments : bool
        コメントを削除するかどうか, by default False
    remove_docstrings : bool
        Docstringを削除するかどうか, by default False
    remove_blank_lines : bool
        空行を削除するかどうか, by default False
    """

    remove_comments: bool = False
    remove_docstrings: bool = False
    remove_blank_lines: bool = False


class VectorAnalysisResult(BaseAnalysisResult):
    """
    ベクトル解析結果

    Attributes
    ----------
    vector : list[float]
        抽出されたベクトル表現
    """

    vector: list[float]


class Vector(AbstractAnalysis[VectorAnalysisResult, VectorAnalysisConfig]):
    """
    ベクトル解析クラス
    """

    def get_default_config(self) -> VectorAnalysisConfig:
        """
        デフォルト設定を取得

        Returns
        -------
        VectorAnalysisConfig
            デフォルトのベクトル解析設定
        """
        return VectorAnalysisConfig()

    def analyze(self, source_code: str) -> VectorAnalysisResult:
        """
        ソースコードからベクトルを抽出する

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        VectorAnalysisResult
            抽出されたベクトル表現
        """
        codetovec = CodeToVec()
        vector = codetovec.execute(
            text=source_code,
            remove_comments=self.config.remove_comments,
            remove_docstrings=self.config.remove_docstrings,
            remove_blank_lines=self.config.remove_blank_lines,
        )
        return VectorAnalysisResult(vector=vector)
