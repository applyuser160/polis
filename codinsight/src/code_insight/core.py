from enum import StrEnum, auto
from typing import Any, Type

from pydantic import BaseModel

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)
from code_insight.code_analysis.algorithm import Algorithm, AlgorithmAnalysisConfig
from code_insight.code_analysis.complexity import Complexity, ComplexityAnalysisConfig
from code_insight.code_analysis.quality import Quality, QualityAnalysisConfig
from code_insight.code_analysis.readability import (
    Readability,
    ReadabilityAnalysisConfig,
)
from code_insight.code_analysis.redundancy import Redundancy, RedundancyAnalysisConfig
from code_insight.code_analysis.struct import Struct, StructAnalysisConfig
from code_insight.code_analysis.style import Style, StyleAnalysisConfig


class AnalysisConfigs(BaseModel):
    """
    全解析エンジンの設定

    Attributes
    ----------
    style : StyleAnalysisConfig | None
        スタイル解析設定, by default None
    struct : StructAnalysisConfig | None
        構造解析設定, by default None
    readability : ReadabilityAnalysisConfig | None
        可読性解析設定, by default None
    redundancy : RedundancyAnalysisConfig | None
        冗長度解析設定, by default None
    algorithm : AlgorithmAnalysisConfig | None
        アルゴリズム解析設定, by default None
    complexity : ComplexityAnalysisConfig | None
        複雑度解析設定, by default None
    quality : QualityAnalysisConfig | None
        品質解析設定, by default None
    """

    style: StyleAnalysisConfig | None = None
    struct: StructAnalysisConfig | None = None
    readability: ReadabilityAnalysisConfig | None = None
    redundancy: RedundancyAnalysisConfig | None = None
    algorithm: AlgorithmAnalysisConfig | None = None
    complexity: ComplexityAnalysisConfig | None = None
    quality: QualityAnalysisConfig | None = None


class CodeAnalysisType(StrEnum):
    """
    コード解析タイプ

    Attributes
    ----------
    STYLE : str
        スタイル解析
    STRUCT : str
        構造解析
    READABILITY : str
        可読性解析
    REDUNDANCY : str
        冗長度解析
    ALGORITHM : str
        アルゴリズム解析
    COMPLEXITY : str
        複雑度解析
    QUALITY : str
        品質解析
    """

    STYLE = auto()
    STRUCT = auto()
    READABILITY = auto()
    REDUNDANCY = auto()
    ALGORITHM = auto()
    COMPLEXITY = auto()
    QUALITY = auto()

    @staticmethod
    def get_code_analysis_class(
        type: str, config: BaseAnalysisConfig | None = None
    ) -> AbstractAnalysis[Any, Any]:
        """
        コード解析クラスを取得

        Parameters
        ----------
        type : str
            解析タイプ
        config : BaseAnalysisConfig | None, optional
            解析設定, by default None

        Returns
        -------
        AbstractAnalysis[Any, Any]
            解析クラスのインスタンス

        Raises
        ------
        ValueError
            無効な解析タイプが指定された場合
        """
        if type == CodeAnalysisType.STYLE:
            return Style(config)  # type: ignore
        elif type == CodeAnalysisType.STRUCT:
            return Struct(config)  # type: ignore
        elif type == CodeAnalysisType.READABILITY:
            return Readability(config)  # type: ignore
        elif type == CodeAnalysisType.REDUNDANCY:
            return Redundancy(config)  # type: ignore
        elif type == CodeAnalysisType.ALGORITHM:
            return Algorithm(config)  # type: ignore
        elif type == CodeAnalysisType.COMPLEXITY:
            return Complexity(config)  # type: ignore
        elif type == CodeAnalysisType.QUALITY:
            return Quality(config)  # type: ignore
        else:
            raise ValueError(f"Invalid code analysis type: {type}")


class CodeAnalysis:
    """
    コード解析

    Attributes
    ----------
    source_code : str
        解析対象のソースコード
    configs : AnalysisConfigs | None
        解析設定
    """

    source_code: str
    configs: AnalysisConfigs | None

    def __init__(
        self, source_code: str, configs: AnalysisConfigs | None = None
    ) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        configs : AnalysisConfigs | None, optional
            解析設定, by default None
        """
        self.source_code = source_code
        self.configs = configs

    def analyze(
        self, types: list[CodeAnalysisType]
    ) -> dict[CodeAnalysisType, Type[BaseAnalysisResult]]:
        """
        コード解析

        Parameters
        ----------
        types : list[CodeAnalysisType]
            実行する解析タイプのリスト

        Returns
        -------
        dict[CodeAnalysisType, Type[BaseAnalysisResult]]
            解析結果の辞書
        """
        result: dict[CodeAnalysisType, Type[BaseAnalysisResult]] = {}
        for type in types:
            config = self._get_config_for_type(type)
            result[type] = CodeAnalysisType.get_code_analysis_class(
                type, config
            ).analyze(self.source_code)
        return result

    def _get_config_for_type(
        self, analysis_type: CodeAnalysisType
    ) -> BaseAnalysisConfig | None:
        """
        解析タイプに対応する設定を取得

        Parameters
        ----------
        analysis_type : CodeAnalysisType
            解析タイプ

        Returns
        -------
        BaseAnalysisConfig | None
            対応する解析設定
        """
        if not self.configs:
            return None

        config_map = {
            CodeAnalysisType.STYLE: self.configs.style,
            CodeAnalysisType.STRUCT: self.configs.struct,
            CodeAnalysisType.READABILITY: self.configs.readability,
            CodeAnalysisType.REDUNDANCY: self.configs.redundancy,
            CodeAnalysisType.ALGORITHM: self.configs.algorithm,
            CodeAnalysisType.COMPLEXITY: self.configs.complexity,
            CodeAnalysisType.QUALITY: self.configs.quality,
        }
        return config_map.get(analysis_type)
