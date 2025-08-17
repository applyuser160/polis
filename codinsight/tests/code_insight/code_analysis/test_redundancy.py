from code_insight.code_analysis.redundancy import Redundancy, RedundancyAnalysisResult


def test_redundancy_normal() -> None:
    # Arrange
    source_code = (
        "def duplicate_function_1(x):\n"
        "    if x > 0:\n"
        "        return x * 2\n"
        "    else:\n"
        "        return 0\n"
        "\n"
        "def duplicate_function_2(y):\n"
        "    if y > 0:\n"
        "        return y * 2\n"
        "    else:\n"
        "        return 0\n"
        "\n"
        "def unused_function():\n"
        "    pass\n"
        "\n"
        "def long_function(a, b, c, d, e, f, g, h, i, j):\n"
        "    result = 0\n"
        "    if a > 0:\n"
        "        if b > 0:\n"
        "            if c > 0:\n"
        "                if d > 0:\n"
        "                    if e > 0:\n"
        "                        if f > 0:\n"
        "                            if g > 0:\n"
        "                                if h > 0:\n"
        "                                    if i > 0:\n"
        "                                        if j > 0:\n"
        "                                            result = (\n"
        "                                                a + b + c + d + \\\n"
        "                                                e + f + g + h + i + j\n"
        "                                            )\n"
        "                                        else:\n"
        "                                            result = a + b + c + \\\n"
        "                                                d + e + f + g + h + i\n"
        "                                    else:\n"
        "                                        result = a + b + c + \\\n"
        "                                            d + e + f + g + h\n"
        "                                else:\n"
        "                                    result = a + b + c + d + e + f + g\n"
        "                            else:\n"
        "                                result = a + b + c + d + e + f\n"
        "                        else:\n"
        "                            result = a + b + c + d + e\n"
        "                    else:\n"
        "                        result = a + b + c + d\n"
        "                else:\n"
        "                    result = a + b + c\n"
        "            else:\n"
        "                result = a + b\n"
        "        else:\n"
        "            result = a\n"
        "    return result\n"
        "\n"
        "def used_function():\n"
        "    return 42\n"
        "\n"
        "def main():\n"
        "    duplicate_function_1(5)\n"
        "    duplicate_function_2(10)\n"
        "    used_function()\n"
        "    return long_function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)\n"
    )

    # Act
    result: RedundancyAnalysisResult = Redundancy().analyze(source_code=source_code)

    # Assert
    assert result.duplicate_code_rate > 0.0
    assert result.unused_code_rate > 0.0
    assert result.long_function_rate > 0.0
    assert result.cyclomatic_complexity > 1.0
    assert result.maintainability_index >= 0.0


def test_redundancy_empty() -> None:
    # Arrange
    source_code = ""

    # Act
    result: RedundancyAnalysisResult = Redundancy().analyze(source_code=source_code)

    # Assert
    assert result.duplicate_code_rate == 0.0
    assert result.unused_code_rate == 0.0
    assert result.long_function_rate == 0.0
    assert result.cyclomatic_complexity == 0.0
    assert result.maintainability_index == 0.0


def test_redundancy_no_duplicates() -> None:
    # Arrange
    source_code = (
        "def function_a():\n"
        "    return 1\n"
        "\n"
        "def function_b():\n"
        "    return 2\n"
        "\n"
        "def main():\n"
        "    function_a()\n"
        "    function_b()\n"
    )

    # Act
    result: RedundancyAnalysisResult = Redundancy().analyze(source_code=source_code)

    # Assert
    assert result.duplicate_code_rate == 0.0
    assert result.unused_code_rate == 0.0


def test_redundancy_all_unused() -> None:
    # Arrange
    source_code = (
        "def unused_function_1():\n"
        "    return 1\n"
        "\n"
        "def unused_function_2():\n"
        "    return 2\n"
    )

    # Act
    result: RedundancyAnalysisResult = Redundancy().analyze(source_code=source_code)

    # Assert
    assert result.unused_code_rate == 1.0
