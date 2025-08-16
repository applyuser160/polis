from code_insight.code_analysis.abstract import AbstractAnalysis, BaseAnalysisResult


class StructAnalysisResult(BaseAnalysisResult):
    """
    解析結果(構造)
    * 関数/クラス数
    * 依存度
    * 凝集度
    """


class Struct(AbstractAnalysis[StructAnalysisResult]):
    """解析クラス(構造)"""

    def analyze(self, source_code: str) -> StructAnalysisResult:
        """コード解析"""
        return StructAnalysisResult()
