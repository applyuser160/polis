import pytest
from code_insight.core import CodeAnalysis, AnalysisConfigs, CodeAnalysisType
from code_insight.code_analysis.quality import QualityAnalysisConfig
from code_insight.code_analysis.redundancy import RedundancyAnalysisConfig
from code_insight.code_analysis.style import StyleAnalysisConfig
from code_insight.multi_analysis import MultiFileAnalyzer


def test_default_config_backward_compatibility():
    """デフォルト設定での後方互換性テスト"""
    source_code = "def test_func(a, b, c, d, e, f): pass"
    
    analysis = CodeAnalysis(source_code)
    result = analysis.analyze([CodeAnalysisType.QUALITY])
    
    assert CodeAnalysisType.QUALITY in result
    quality_result = result[CodeAnalysisType.QUALITY]
    assert quality_result.long_parameter_function_rate > 0


def test_custom_config_injection():
    """カスタム設定注入のテスト"""
    source_code = "def test_func(a, b, c): pass"
    
    configs = AnalysisConfigs(
        quality=QualityAnalysisConfig(long_param_threshold=2)
    )
    analysis = CodeAnalysis(source_code, configs)
    result = analysis.analyze([CodeAnalysisType.QUALITY])
    
    quality_result = result[CodeAnalysisType.QUALITY]
    assert quality_result.long_parameter_function_rate > 0


def test_disabled_analysis():
    """解析無効化のテスト"""
    source_code = "def test_func(): pass"
    
    configs = AnalysisConfigs(
        quality=QualityAnalysisConfig(enabled=False)
    )
    analysis = CodeAnalysis(source_code, configs)
    result = analysis.analyze([CodeAnalysisType.QUALITY])
    
    quality_result = result[CodeAnalysisType.QUALITY]
    assert quality_result.type_hint_coverage == 0.0
    assert quality_result.assert_count == 0


def test_redundancy_config():
    """冗長度解析設定のテスト"""
    source_code = """
def long_function():
    for i in range(100):
        if i % 2 == 0:
            for j in range(50):
                print(i, j)
                if j > 10:
                    break
"""
    
    analysis_default = CodeAnalysis(source_code)
    result_default = analysis_default.analyze([CodeAnalysisType.REDUNDANCY])
    
    configs = AnalysisConfigs(
        redundancy=RedundancyAnalysisConfig(long_function_lines_threshold=5)
    )
    analysis_custom = CodeAnalysis(source_code, configs)
    result_custom = analysis_custom.analyze([CodeAnalysisType.REDUNDANCY])
    
    redundancy_default = result_default[CodeAnalysisType.REDUNDANCY]
    redundancy_custom = result_custom[CodeAnalysisType.REDUNDANCY]
    
    assert redundancy_custom.long_function_rate >= redundancy_default.long_function_rate


def test_style_config():
    """スタイル解析設定のテスト"""
    source_code = "def TestFunc(): pass"
    
    analysis_default = CodeAnalysis(source_code)
    result_default = analysis_default.analyze([CodeAnalysisType.STYLE])
    
    configs = AnalysisConfigs(
        style=StyleAnalysisConfig(function_name_pattern=r"^[A-Z][a-zA-Z0-9]*$")
    )
    analysis_custom = CodeAnalysis(source_code, configs)
    result_custom = analysis_custom.analyze([CodeAnalysisType.STYLE])
    
    style_default = result_default[CodeAnalysisType.STYLE]
    style_custom = result_custom[CodeAnalysisType.STYLE]
    
    assert style_custom.naming_convention <= style_default.naming_convention


def test_multi_file_analyzer_config():
    """複数ファイル解析での設定テスト"""
    configs = AnalysisConfigs(
        quality=QualityAnalysisConfig(long_param_threshold=2),
        redundancy=RedundancyAnalysisConfig(enabled=False)
    )
    
    analyzer = MultiFileAnalyzer(configs=configs)
    
    assert analyzer.configs is not None
    assert analyzer.configs.quality.long_param_threshold == 2
    assert analyzer.configs.redundancy.enabled is False


def test_ignored_function_names_config():
    """無視対象関数名設定のテスト"""
    source_code = """
def main():
    pass

def custom_init():
    pass

def regular_function():
    pass
"""
    
    configs = AnalysisConfigs(
        redundancy=RedundancyAnalysisConfig(
            ignored_function_names={"main", "__init__", "__main__", "custom_init"}
        )
    )
    analysis = CodeAnalysis(source_code, configs)
    result = analysis.analyze([CodeAnalysisType.REDUNDANCY])
    
    redundancy_result = result[CodeAnalysisType.REDUNDANCY]
    assert redundancy_result.unused_code_rate >= 0.0
