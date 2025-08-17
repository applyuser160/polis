from enum import StrEnum, auto
from typing import Any, Type

from code_insight.code_analysis.abstract import AbstractAnalysis, BaseAnalysisResult
from code_insight.code_analysis.readability import Readability
from code_insight.code_analysis.struct import Struct
from code_insight.code_analysis.style import Style


class CodeAnalysisType(StrEnum):
    """
    コード解析タイプ
    * スタイル
    * 構造
    * 複雑度
    * 冗長度
    * 可読性
    * 品質
    """

    STYLE = auto()
    STRUCT = auto()
    READABILITY = auto()

    @staticmethod
    def get_code_analysis_class(type: str) -> AbstractAnalysis[Any]:
        """コード解析クラスを取得"""
        if type == CodeAnalysisType.STYLE:
            return Style()
        elif type == CodeAnalysisType.STRUCT:
            return Struct()
        elif type == CodeAnalysisType.READABILITY:
            return Readability()
        else:
            raise ValueError(f"Invalid code analysis type: {type}")


class CodeAnalysis:
    """コード解析"""

    source_code: str

    def __init__(self, source_code: str) -> None:
        """コンストラクタ"""
        self.source_code = source_code

    def analyze(
        self, types: list[CodeAnalysisType]
    ) -> dict[CodeAnalysisType, Type[BaseAnalysisResult]]:
        """コード解析"""
        result: dict[CodeAnalysisType, Type[BaseAnalysisResult]] = {}
        for type in types:
            result[type] = CodeAnalysisType.get_code_analysis_class(type).analyze(
                self.source_code
            )
        return result
