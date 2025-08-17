from code_insight.code_analysis.readability import ReadabilityAnalysisResult
from code_insight.code_analysis.struct import StructAnalysisResult
from code_insight.code_analysis.style import StyleAnalysisResult
from code_insight.core import CodeAnalysis, CodeAnalysisType


def test_core_normal() -> None:
    # テスト観点: コア機能のコード解析(正常系)

    # Arrange
    source_code = (
        "class MyClass:\n"
        "    def __init__(self):\n"
        "        self.attr = 1\n"
        "    def method(self) -> int:\n"
        "        return 1\n"
        "def function():\n"
        "    # comment\n"
        "    pass\n"
    )
    code_analysis = CodeAnalysis(source_code=source_code)

    # Act
    result = code_analysis.analyze(
        [CodeAnalysisType.STYLE, CodeAnalysisType.STRUCT, CodeAnalysisType.READABILITY]
    )

    # Assert
    assert len(result) == 3
    assert CodeAnalysisType.STYLE in result
    assert CodeAnalysisType.STRUCT in result
    assert CodeAnalysisType.READABILITY in result
    assert isinstance(result[CodeAnalysisType.STYLE], StyleAnalysisResult)
    assert isinstance(result[CodeAnalysisType.STRUCT], StructAnalysisResult)
    assert isinstance(result[CodeAnalysisType.READABILITY], ReadabilityAnalysisResult)


def test_core_empty() -> None:
    # テスト観点: コア機能のコード解析(空文字列)

    # Arrange
    source_code = ""
    code_analysis = CodeAnalysis(source_code=source_code)

    # Act
    result = code_analysis.analyze([CodeAnalysisType.STYLE, CodeAnalysisType.STRUCT])

    # Assert
    assert len(result) == 2
    assert CodeAnalysisType.STYLE in result
    assert CodeAnalysisType.STRUCT in result
    assert isinstance(result[CodeAnalysisType.STYLE], StyleAnalysisResult)
    assert isinstance(result[CodeAnalysisType.STRUCT], StructAnalysisResult)
