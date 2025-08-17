from code_insight.code_analysis.style import Style, StyleAnalysisResult


def test_style_normal() -> None:
    # テスト観点: スタイルのコード解析(正常系)

    # Arrange
    source_code = (
        "\n"
        "def foo():\n"
        "    '''"
        "    docstring"
        "    '''\n"
        "    # comment\n"
        "    pass\n"
        "def Add(a, b):\n"
        "    return a+b\n"
    )

    # Act
    result: StyleAnalysisResult = Style().analyze(source_code=source_code)

    # Assert
    assert result.naming_convention == 1.0
    assert result.comment_rate == 1 / 7
    assert result.docstring_rate == 1 / 7
    assert result.pep8_violation_rate == 2 / 7


def test_style_empty() -> None:
    # テスト観点: スタイルのコード解析(空文字列)

    # Arrange
    source_code = ""

    # Act
    result: StyleAnalysisResult = Style().analyze(source_code=source_code)

    # Assert
    assert result.naming_convention == 0.0
    assert result.comment_rate == 0.0
    assert result.docstring_rate == 0.0
    assert result.pep8_violation_rate == 0.0
