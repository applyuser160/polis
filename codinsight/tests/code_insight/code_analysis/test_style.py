from code_insight.code_analysis.style import Style, StyleAnalysisResult


def test_style() -> None:
    # テスト観点: スタイルのコード解析(正常系)
    source_code = (
        "def foo():\n"
        "    '''"
        "    docstring"
        "    '''\n"
        "    # comment\n"
        "    pass\n"
    )
    result: StyleAnalysisResult = Style().analyze(source_code=source_code)
    assert result.naming_convention == 0.0
    assert result.comment_rate == 0.25
    assert result.docstring_rate == 0.25
    assert result.pep8_violation_rate == 0.25


def test_get_style_naming_convention() -> None:
    # テスト観点: スタイルのコード解析(命名規則の一貫性)
    source_code = "def Add(a, b):\n" "    return a+b\n"
    result: StyleAnalysisResult = Style().analyze(source_code=source_code)
    assert result.naming_convention == 1.0


def test_get_style_comment_rate() -> None:
    # テスト観点: スタイルのコード解析(コメント率)
    source_code = "# comment\n" "a = 1\n"
    result: StyleAnalysisResult = Style().analyze(source_code=source_code)
    assert result.comment_rate == 0.5


def test_get_style_docstring_rate() -> None:
    # テスト観点: スタイルのコード解析(docstringの割合)
    source_code = "def foo():\n" "    '''" "    docstring" "    '''\n" "    pass\n"
    result: StyleAnalysisResult = Style().analyze(source_code=source_code)
    assert result.docstring_rate == 1 / 3


def test_get_style_pep8_violation_rate() -> None:
    # テスト観点: スタイルのコード解析(PEP8違反率)
    source_code = "def foo():\n" "    a = 1\n" "    b = 2\n"
    result: StyleAnalysisResult = Style().analyze(source_code=source_code)
    assert result.pep8_violation_rate == 1 / 3
