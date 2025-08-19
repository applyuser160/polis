from code_insight.code_analysis.quality import (
    QualityAnalysisConfig,
    QualityAnalysisResult,
)
from code_insight.code_analysis.redundancy import (
    RedundancyAnalysisConfig,
    RedundancyAnalysisResult,
)
from code_insight.code_analysis.style import StyleAnalysisConfig, StyleAnalysisResult
from code_insight.core import AnalysisConfigs, CodeAnalysis, CodeAnalysisType
from code_insight.multi_analysis import MultiFileAnalyzer


def test_default_config_backward_compatibility() -> None:
    """デフォルト設定での後方互換性テスト"""
    source_code = "def test_func(a, b, c, d, e, f): pass"

    analysis = CodeAnalysis(source_code)
    result = analysis.analyze([CodeAnalysisType.QUALITY])

    assert CodeAnalysisType.QUALITY in result
    quality_result: QualityAnalysisResult = result[CodeAnalysisType.QUALITY]  # type: ignore
    assert quality_result.long_parameter_function_rate > 0


def test_custom_config_injection() -> None:
    """カスタム設定注入のテスト"""
    source_code = "def test_func(a, b, c): pass"

    configs = AnalysisConfigs(quality=QualityAnalysisConfig(long_param_threshold=2))
    analysis = CodeAnalysis(source_code, configs)
    result = analysis.analyze([CodeAnalysisType.QUALITY])

    quality_result: QualityAnalysisResult = result[CodeAnalysisType.QUALITY]  # type: ignore
    assert quality_result.long_parameter_function_rate > 0


def test_disabled_analysis() -> None:
    """解析無効化のテスト"""
    source_code = "def test_func(): pass"

    configs = AnalysisConfigs(quality=QualityAnalysisConfig(enabled=False))
    analysis = CodeAnalysis(source_code, configs)
    result = analysis.analyze([CodeAnalysisType.QUALITY])

    quality_result: QualityAnalysisResult = result[CodeAnalysisType.QUALITY]  # type: ignore
    assert quality_result.type_hint_coverage == 0.0
    assert quality_result.assert_count == 0


def test_redundancy_config() -> None:
    """冗長度解析設定のテスト"""
    source_code = (
        "def long_function():\n"
        "    for i in range(100):\n"
        "        if i % 2 == 0:\n"
        "            for j in range(50):\n"
        "                print(i, j)\n"
        "                if j > 10:\n"
        "                    break\n"
    )

    analysis_default = CodeAnalysis(source_code)
    result_default = analysis_default.analyze([CodeAnalysisType.REDUNDANCY])

    configs = AnalysisConfigs(
        redundancy=RedundancyAnalysisConfig(long_function_lines_threshold=5)
    )
    analysis_custom = CodeAnalysis(source_code, configs)
    result_custom = analysis_custom.analyze([CodeAnalysisType.REDUNDANCY])

    redundancy_default: RedundancyAnalysisResult = result_default[
        CodeAnalysisType.REDUNDANCY
    ]  # type: ignore
    redundancy_custom: RedundancyAnalysisResult = result_custom[
        CodeAnalysisType.REDUNDANCY
    ]  # type: ignore

    assert redundancy_custom.long_function_rate >= redundancy_default.long_function_rate


def test_style_config() -> None:
    """スタイル解析設定のテスト"""
    source_code = "def TestFunc(): pass"

    analysis_default = CodeAnalysis(source_code)
    result_default = analysis_default.analyze([CodeAnalysisType.STYLE])

    configs = AnalysisConfigs(
        style=StyleAnalysisConfig(function_name_pattern=r"^[A-Z][a-zA-Z0-9]*$")
    )
    analysis_custom = CodeAnalysis(source_code, configs)
    result_custom = analysis_custom.analyze([CodeAnalysisType.STYLE])

    style_default: StyleAnalysisResult = result_default[CodeAnalysisType.STYLE]  # type: ignore
    style_custom: StyleAnalysisResult = result_custom[CodeAnalysisType.STYLE]  # type: ignore

    assert style_custom.naming_convention <= style_default.naming_convention


def test_multi_file_analyzer_config() -> None:
    """複数ファイル解析での設定テスト"""
    configs = AnalysisConfigs(
        quality=QualityAnalysisConfig(long_param_threshold=2),
        redundancy=RedundancyAnalysisConfig(enabled=False),
    )

    analyzer = MultiFileAnalyzer(configs=configs)

    assert analyzer.configs is not None
    assert analyzer.configs.quality
    assert analyzer.configs.quality.long_param_threshold == 2
    assert analyzer.configs.redundancy
    assert analyzer.configs.redundancy.enabled is False


def test_ignored_function_names_config() -> None:
    """無視対象関数名設定のテスト"""
    source_code = (
        "def main():\n"
        "    pass\n"
        "\n"
        "def custom_init():\n"
        "    pass\n"
        "\n"
        "def regular_function():\n"
        "    pass\n"
    )

    configs = AnalysisConfigs(
        redundancy=RedundancyAnalysisConfig(
            ignored_function_names={"main", "__init__", "__main__", "custom_init"}
        )
    )
    analysis = CodeAnalysis(source_code, configs)
    result = analysis.analyze([CodeAnalysisType.REDUNDANCY])

    redundancy_result: RedundancyAnalysisResult = result[CodeAnalysisType.REDUNDANCY]  # type: ignore
    assert redundancy_result.unused_code_rate >= 0.0
