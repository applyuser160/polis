import os

import numpy as np

from code_insight.code_analysis.abstract import BaseAnalysisResult
from code_insight.code_analysis.struct import StructAnalysisResult
from code_insight.code_analysis.style import StyleAnalysisResult
from code_insight.trend_analysis.trend_analysis import TrendAnalysis


def test_trend_analysis_normal() -> None:
    # テスト観点: トレンド解析(正常系)

    # Arrange
    struct_result1 = StructAnalysisResult(
        function_count=2,
        class_count=1,
        line_count=5,
        argument_count=1.0,
        return_type_hint=0.5,
        staticmethod_rate=0.0,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=1.0,
        attribute_count=1.0,
        public_rate=1.0,
        private_rate=0.0,
        dependency=0.5,
        cohesion=1.0,
        inheritance_depth=0.0,
        subclass_count=0.0,
    )
    style_result1 = StyleAnalysisResult(
        naming_convention=1.0,
        comment_rate=0.2,
        docstring_rate=0.0,
        pep8_violation_rate=0.1,
    )

    struct_result2 = StructAnalysisResult(
        function_count=3,
        class_count=2,
        line_count=8,
        argument_count=1.5,
        return_type_hint=0.7,
        staticmethod_rate=0.1,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=2.0,
        attribute_count=2.0,
        public_rate=0.8,
        private_rate=0.2,
        dependency=0.3,
        cohesion=0.9,
        inheritance_depth=1.0,
        subclass_count=1.0,
    )
    style_result2 = StyleAnalysisResult(
        naming_convention=0.8,
        comment_rate=0.3,
        docstring_rate=0.1,
        pep8_violation_rate=0.2,
    )

    code_analysis_results = [
        [struct_result1, style_result1],
        [struct_result2, style_result2],
    ]

    # Act
    trend_analysis = TrendAnalysis(code_analysis_results)

    # Assert
    assert len(trend_analysis.code_analysis_list) == 2
    assert "function_count" in trend_analysis.code_analysis_list[0]
    assert "naming_convention" in trend_analysis.code_analysis_list[0]


def test_trend_analysis_extract_value() -> None:
    # テスト観点: 値抽出機能

    # Arrange
    struct_result = StructAnalysisResult(
        function_count=2,
        class_count=1,
        line_count=5,
        argument_count=1.0,
        return_type_hint=0.5,
        staticmethod_rate=0.0,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=1.0,
        attribute_count=1.0,
        public_rate=1.0,
        private_rate=0.0,
        dependency=0.5,
        cohesion=1.0,
        inheritance_depth=0.0,
        subclass_count=0.0,
    )
    style_result = StyleAnalysisResult(
        naming_convention=1.0,
        comment_rate=0.2,
        docstring_rate=0.0,
        pep8_violation_rate=0.1,
    )

    code_analysis_results = [[struct_result, style_result]]
    trend_analysis = TrendAnalysis(code_analysis_results)

    # Act
    result = trend_analysis.extract_value(["function_count", "class_count"])

    # Assert
    assert result.shape == (1, 2)
    assert result[0][0] == 2.0
    assert result[0][1] == 1.0


def test_trend_analysis_compress() -> None:
    # テスト観点: 次元圧縮機能

    # Arrange
    struct_result1 = StructAnalysisResult(
        function_count=2,
        class_count=1,
        line_count=5,
        argument_count=1.0,
        return_type_hint=0.5,
        staticmethod_rate=0.0,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=1.0,
        attribute_count=1.0,
        public_rate=1.0,
        private_rate=0.0,
        dependency=0.5,
        cohesion=1.0,
        inheritance_depth=0.0,
        subclass_count=0.0,
    )
    struct_result2 = StructAnalysisResult(
        function_count=3,
        class_count=2,
        line_count=8,
        argument_count=1.5,
        return_type_hint=0.7,
        staticmethod_rate=0.1,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=2.0,
        attribute_count=2.0,
        public_rate=0.8,
        private_rate=0.2,
        dependency=0.3,
        cohesion=0.9,
        inheritance_depth=1.0,
        subclass_count=1.0,
    )

    code_analysis_results = [[struct_result1], [struct_result2]]
    trend_analysis = TrendAnalysis(code_analysis_results)

    # Act
    result = trend_analysis.compress(["function_count", "class_count", "line_count"])

    # Assert
    assert result.shape == (2, 2)


def test_trend_analysis_cluster_values() -> None:
    # テスト観点: クラスタリング機能

    # Arrange
    struct_result1 = StructAnalysisResult(
        function_count=2,
        class_count=1,
        line_count=5,
        argument_count=1.0,
        return_type_hint=0.5,
        staticmethod_rate=0.0,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=1.0,
        attribute_count=1.0,
        public_rate=1.0,
        private_rate=0.0,
        dependency=0.5,
        cohesion=1.0,
        inheritance_depth=0.0,
        subclass_count=0.0,
    )
    struct_result2 = StructAnalysisResult(
        function_count=3,
        class_count=2,
        line_count=8,
        argument_count=1.5,
        return_type_hint=0.7,
        staticmethod_rate=0.1,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=2.0,
        attribute_count=2.0,
        public_rate=0.8,
        private_rate=0.2,
        dependency=0.3,
        cohesion=0.9,
        inheritance_depth=1.0,
        subclass_count=1.0,
    )

    code_analysis_results = [[struct_result1], [struct_result2]]
    trend_analysis = TrendAnalysis(code_analysis_results)

    # Act
    result = trend_analysis.cluster_values(["function_count", "class_count"])

    # Assert
    assert len(result) == 2
    assert all(isinstance(x, (int, np.integer)) for x in result)


def test_trend_analysis_empty() -> None:
    # テスト観点: トレンド解析(空リスト)

    # Arrange
    code_analysis_results: list[list[BaseAnalysisResult]] = []

    # Act
    trend_analysis = TrendAnalysis(code_analysis_results)

    # Assert
    assert len(trend_analysis.code_analysis_list) == 0


def test_trend_analysis_output_image() -> None:
    # テスト観点: グラフ描画

    # Arrange
    struct_result1 = StructAnalysisResult(
        function_count=2,
        class_count=1,
        line_count=5,
        argument_count=1.0,
        return_type_hint=0.5,
        staticmethod_rate=0.0,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=1.0,
        attribute_count=1.0,
        public_rate=1.0,
        private_rate=0.0,
        dependency=0.5,
        cohesion=1.0,
        inheritance_depth=0.0,
        subclass_count=0.0,
    )
    struct_result2 = StructAnalysisResult(
        function_count=3,
        class_count=2,
        line_count=8,
        argument_count=1.5,
        return_type_hint=0.7,
        staticmethod_rate=0.1,
        class_method_rate=0.0,
        abstractmethod_rate=0.0,
        property_rate=0.0,
        method_count=2.0,
        attribute_count=2.0,
        public_rate=0.8,
        private_rate=0.2,
        dependency=0.3,
        cohesion=0.9,
        inheritance_depth=1.0,
        subclass_count=1.0,
    )

    code_analysis_results = [[struct_result1], [struct_result2]]
    trend_analysis = TrendAnalysis(
        code_analysis_results=code_analysis_results,
        code_labels=["struct_result1", "struct_result2"],
    )

    # Act
    trend_analysis.output_image()

    # Assert
    assert os.path.exists("clusters.png")
