from code_insight.code_analysis.struct import Struct, StructAnalysisResult


def test_struct_normal() -> None:
    # テスト観点: 構造のコード解析(正常系)

    # Arrange
    source_code = (
        "class MyClass:\n"
        "    def __init__(self):\n"
        "        self.attr = 1\n"
        "    @staticmethod\n"
        "    def static_method():\n"
        "        pass\n"
        "    def public_method(self, a: int) -> int:\n"
        "        return a\n"
        "def function(x, y):\n"
        "    return x + y\n"
    )

    # Act
    result: StructAnalysisResult = Struct().analyze(source_code=source_code)

    # Assert
    assert result.function_count == 4
    assert result.class_count == 1
    assert result.line_count == 10
    assert result.argument_count == 0.0
    assert result.return_type_hint == 0.25
    assert result.staticmethod_rate == 0.25
    assert result.class_method_rate == 0.0
    assert result.abstractmethod_rate == 0.0
    assert result.property_rate == 0.0
    assert result.method_count == 3.0
    assert result.attribute_count == 0.0
    assert result.public_rate == 2 / 3
    assert result.private_rate == 1 / 3
    assert result.dependency == 0.0
    assert result.cohesion == 1.0
    assert result.inheritance_depth == 0.0
    assert result.subclass_count == 0.0


def test_struct_empty() -> None:
    # テスト観点: 構造のコード解析(空文字列)

    # Arrange
    source_code = ""

    # Act
    result: StructAnalysisResult = Struct().analyze(source_code=source_code)

    # Assert
    assert result.function_count == 0
    assert result.class_count == 0
    assert result.line_count == 0
    assert result.argument_count == 0.0
    assert result.return_type_hint == 0.0
    assert result.staticmethod_rate == 0.0
    assert result.class_method_rate == 0.0
    assert result.abstractmethod_rate == 0.0
    assert result.property_rate == 0.0
    assert result.method_count == 0.0
    assert result.attribute_count == 0.0
    assert result.public_rate == 0.0
    assert result.private_rate == 0.0
    assert result.dependency == 0.0
    assert result.cohesion == 1.0
    assert result.inheritance_depth == 0.0
    assert result.subclass_count == 0.0
