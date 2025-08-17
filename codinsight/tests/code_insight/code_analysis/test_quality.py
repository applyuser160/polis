from code_insight.code_analysis.quality import Quality, QualityAnalysisResult


def test_quality_empty() -> None:
    # Arrange
    source_code = ""

    # Act
    result: QualityAnalysisResult = Quality().analyze(source_code=source_code)

    # Assert
    assert result.type_hint_coverage == 0.0
    assert result.docstring_coverage == 0.0
    assert result.exception_handling_rate == 0.0
    assert result.avg_function_length == 0.0
    assert result.long_parameter_function_rate == 0.0
    assert result.assert_count == 0
    assert result.todo_comment_rate == 0.0


def test_quality_normal() -> None:
    # Arrange
    source_code = (
        '"""Module doc"""\n'
        "def f(a: int, b: str) -> int:\n"
        '    """doc"""\n'
        "    try:\n"
        "        assert a > 0\n"
        "    except Exception:\n"
        "        pass\n"
        "    return a\n"
        "def g(x, y, z, u, v, w):\n"
        "    return x\n"
        "class C:\n"
        '    """C doc"""\n'
        "    pass\n"
        "# TODO: refactor\n"
    )

    # Act
    result: QualityAnalysisResult = Quality().analyze(source_code=source_code)

    # Assert
    assert result.type_hint_coverage == 0.3
    assert result.docstring_coverage == 0.75
    assert result.exception_handling_rate == 0.5
    assert result.avg_function_length == 4.5
    assert result.long_parameter_function_rate == 0.5
    assert result.assert_count == 1
    non_empty_lines = [line for line in source_code.splitlines() if line.strip()]
    expected_todo = sum(
        1 for line in non_empty_lines if ("TODO" in line or "FIXME" in line)
    ) / len(non_empty_lines)
    assert result.todo_comment_rate == expected_todo
