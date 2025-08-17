from code_insight.code_analysis.readability import ReadabilityAnalysisResult
from code_insight.core import CodeAnalysis, CodeAnalysisType


def test_core_readability_only() -> None:
    # Arrange
    source_code = (
        "def calculate_something_complex(parameter_with_long_name):\n"
        "    if parameter_with_long_name > 0:\n"
        "        return parameter_with_long_name * 2\n"
        "    return 0\n"
    )
    code_analysis = CodeAnalysis(source_code=source_code)

    # Act
    result = code_analysis.analyze([CodeAnalysisType.READABILITY])

    # Assert
    assert len(result) == 1
    assert CodeAnalysisType.READABILITY in result
    assert isinstance(result[CodeAnalysisType.READABILITY], ReadabilityAnalysisResult)


def test_core_all_analysis_types() -> None:
    # Arrange
    source_code = (
        "class MyClass:\n"
        "    def __init__(self):\n"
        "        self.very_long_variable_name = 1\n"
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
