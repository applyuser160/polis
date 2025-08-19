from code_insight.code_analysis.readability import (
    Readability,
    ReadabilityAnalysisResult,
)


def test_readability_normal() -> None:
    # Arrange
    source_code = (
        "class MyClass:\n"
        "    def __init__(self):\n"
        "        self.very_long_variable_name = 1\n"
        "        self.x = 2\n"
        "    def calculate_something_complex(\n"
        "        self, parameter_with_long_name: int) -> int:\n"
        "        if parameter_with_long_name > 0:\n"
        "            if parameter_with_long_name > 10:\n"
        "                return parameter_with_long_name * 2\n"
        "        return 0\n"
        "def short_func():\n"
        "    pass\n"
    )

    # Act
    result: ReadabilityAnalysisResult = Readability().analyze(source_code=source_code)

    # Assert
    assert result.variable_name_length > 0
    assert result.max_variable_name_length > 0
    assert result.line_length > 0
    assert result.max_line_length > 0
    assert result.halstead_volume > 0
    assert result.halstead_difficulty > 0
    assert result.halstead_effort > 0
    assert result.nesting_depth > 0
    assert result.identifier_complexity >= 0


def test_readability_empty() -> None:
    # Arrange
    source_code = ""

    # Act
    result: ReadabilityAnalysisResult = Readability().analyze(source_code=source_code)

    # Assert
    assert result.variable_name_length == 0.0
    assert result.max_variable_name_length == 0
    assert result.line_length == 0.0
    assert result.max_line_length == 0
    assert result.halstead_volume == 0.0
    assert result.halstead_difficulty == 0.0
    assert result.halstead_effort == 0.0
    assert result.nesting_depth == 0.0
    assert result.identifier_complexity == 0.0


def test_readability_simple_code() -> None:
    # Arrange
    source_code = (
        "def add(a, b):\n    return a + b\nx = 5\ny = 10\nresult = add(x, y)\n"
    )

    # Act
    result: ReadabilityAnalysisResult = Readability().analyze(source_code=source_code)

    # Assert
    assert result.variable_name_length > 0
    assert result.max_variable_name_length >= 1
    assert result.line_length > 0
    assert result.max_line_length > 0
    assert result.halstead_volume >= 0
    assert result.halstead_difficulty >= 0
    assert result.halstead_effort >= 0
    assert result.nesting_depth >= 0
    assert result.identifier_complexity >= 0
