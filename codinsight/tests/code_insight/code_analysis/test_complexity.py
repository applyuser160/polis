from code_insight.code_analysis.complexity import Complexity, ComplexityAnalysisResult


def test_complexity_normal() -> None:

    # Arrange
    source_code = (
        "def factorial(n):\n"
        "    if n < 2:\n"
        "        return 1\n"
        "    return n * factorial(n - 1)\n"
        "\n"
        "class Example:\n"
        "    def method(self):\n"
        "        for i in range(10):\n"
        "            if i % 2:\n"
        "                print(i)\n"
    )

    # Act
    result: ComplexityAnalysisResult = Complexity().analyze(source_code=source_code)

    # Assert
    assert result.cyclomatic_complexity > 0
    assert result.halstead_volume > 0
    assert result.halstead_difficulty > 0
    assert result.halstead_effort > 0
    assert result.max_nesting_depth >= 2
    assert result.avg_nesting_depth > 0
    assert result.cognitive_complexity > 0
    assert result.maintainability_index > 0


def test_complexity_empty() -> None:

    # Arrange
    source_code = ""

    # Act
    result: ComplexityAnalysisResult = Complexity().analyze(source_code=source_code)

    # Assert
    assert result.cyclomatic_complexity == 0.0
    assert result.halstead_volume == 0.0
    assert result.halstead_difficulty == 0.0
    assert result.halstead_effort == 0.0
    assert result.max_nesting_depth == 0
    assert result.avg_nesting_depth == 0.0
    assert result.cognitive_complexity == 0.0
    assert result.maintainability_index == 0.0


def test_complexity_simple_function() -> None:

    # Arrange
    source_code = (
        "def simple_function(x):\n"
        "    return x * 2\n"
    )

    # Act
    result: ComplexityAnalysisResult = Complexity().analyze(source_code=source_code)

    # Assert
    assert result.cyclomatic_complexity >= 1.0
    assert result.halstead_volume > 0
    assert result.max_nesting_depth == 1
    assert result.cognitive_complexity >= 0.0
    assert result.maintainability_index > 0


def test_complexity_nested_structure() -> None:

    # Arrange
    source_code = (
        "def complex_function(data):\n"
        "    for item in data:\n"
        "        if item > 0:\n"
        "            for i in range(item):\n"
        "                if i % 2 == 0:\n"
        "                    print(i)\n"
    )

    # Act
    result: ComplexityAnalysisResult = Complexity().analyze(source_code=source_code)

    # Assert
    assert result.cyclomatic_complexity > 1.0
    assert result.max_nesting_depth >= 4
    assert result.avg_nesting_depth > 1.0
    assert result.cognitive_complexity > 1.0
