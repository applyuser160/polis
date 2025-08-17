import ast
import math
import re
from typing import Optional

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class ReadabilityAnalysisConfig(BaseAnalysisConfig):
    """可読性解析設定"""

    max_line_length_threshold: int = 88
    min_variable_name_length: int = 3
    identifier_complexity_threshold: float = 0.3


class ReadabilityAnalysisResult(BaseAnalysisResult):
    """
    解析結果(可読性)
    * 変数名の長さ
        * 変数名の平均長
        * 変数名の最大長
    * 行の長さ
        * 行の平均長
        * 行の最大長
    * 情報量
        * Halstead Volume
        * Halstead Difficulty
        * Halstead Effort
    * ネスト深度
        * 平均ネスト深度
    * 識別子複雑度
        * 略語使用率や複雑な命名パターンの割合
    """

    variable_name_length: float
    max_variable_name_length: int
    line_length: float
    max_line_length: int
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    nesting_depth: float
    identifier_complexity: float


class Readability(
    AbstractAnalysis[ReadabilityAnalysisResult, ReadabilityAnalysisConfig]
):
    """解析クラス(可読性)"""

    def __init__(self, config: Optional[ReadabilityAnalysisConfig] = None) -> None:
        """コンストラクタ"""
        super().__init__(config)

    def get_default_config(self) -> ReadabilityAnalysisConfig:
        """デフォルト設定を取得"""
        return ReadabilityAnalysisConfig()

    def analyze(self, source_code: str) -> ReadabilityAnalysisResult:
        """コード解析"""
        if not self.config.enabled:
            return ReadabilityAnalysisResult(
                variable_name_length=0.0,
                max_variable_name_length=0,
                line_length=0.0,
                max_line_length=0,
                halstead_volume=0.0,
                halstead_difficulty=0.0,
                halstead_effort=0.0,
                nesting_depth=0.0,
                identifier_complexity=0.0,
            )

        return ReadabilityAnalysisResult(
            variable_name_length=self.get_variable_name_length(source_code),
            max_variable_name_length=self.get_max_variable_name_length(source_code),
            line_length=self.get_line_length(source_code),
            max_line_length=self.get_max_line_length(source_code),
            halstead_volume=self.get_halstead_volume(source_code),
            halstead_difficulty=self.get_halstead_difficulty(source_code),
            halstead_effort=self.get_halstead_effort(source_code),
            nesting_depth=self.get_nesting_depth(source_code),
            identifier_complexity=self.get_identifier_complexity(source_code),
        )

    def parse_source_code(self, source_code: str) -> ast.AST:
        """ソースコードを解析"""
        return ast.parse(source_code)

    def get_variable_names(self, source_code: str) -> list[str]:
        """変数名を抽出"""
        if not source_code.strip():
            return []

        tree = self.parse_source_code(source_code)
        variable_names = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                variable_names.append(node.id)
            elif isinstance(node, ast.arg):
                variable_names.append(node.arg)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                variable_names.append(node.attr)

        return variable_names

    def get_variable_name_length(self, source_code: str) -> float:
        """変数名の平均長を取得"""
        variable_names = self.get_variable_names(source_code)
        if not variable_names:
            return 0.0

        total_length = sum(len(name) for name in variable_names)
        return total_length / len(variable_names)

    def get_max_variable_name_length(self, source_code: str) -> int:
        """変数名の最大長を取得"""
        variable_names = self.get_variable_names(source_code)
        if not variable_names:
            return 0

        return max(len(name) for name in variable_names)

    def get_line_length(self, source_code: str) -> float:
        """行の平均長を取得"""
        lines = source_code.splitlines()
        if not lines:
            return 0.0

        total_length = sum(len(line) for line in lines)
        return total_length / len(lines)

    def get_max_line_length(self, source_code: str) -> int:
        """行の最大長を取得"""
        lines = source_code.splitlines()
        if not lines:
            return 0

        return max(len(line) for line in lines)

    def get_halstead_metrics(self, source_code: str) -> tuple[int, int, int, int]:
        """Halstead メトリクスの基本値を取得"""
        if not source_code.strip():
            return 0, 0, 0, 0

        tree = self.parse_source_code(source_code)

        operators = set()
        operands = set()
        operator_count = 0
        operand_count = 0

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.Add,
                    ast.Sub,
                    ast.Mult,
                    ast.Div,
                    ast.Mod,
                    ast.Pow,
                    ast.LShift,
                    ast.RShift,
                    ast.BitOr,
                    ast.BitXor,
                    ast.BitAnd,
                    ast.FloorDiv,
                ),
            ):
                operators.add(type(node).__name__)
                operator_count += 1
            elif isinstance(
                node,
                (
                    ast.And,
                    ast.Or,
                    ast.Not,
                    ast.Eq,
                    ast.NotEq,
                    ast.Lt,
                    ast.LtE,
                    ast.Gt,
                    ast.GtE,
                    ast.Is,
                    ast.IsNot,
                    ast.In,
                    ast.NotIn,
                ),
            ):
                operators.add(type(node).__name__)
                operator_count += 1
            elif isinstance(
                node,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.FunctionDef,
                    ast.ClassDef,
                    ast.Return,
                    ast.Assign,
                    ast.AugAssign,
                ),
            ):
                operators.add(type(node).__name__)
                operator_count += 1
            elif isinstance(node, ast.Name):
                operands.add(node.id)
                operand_count += 1
            elif isinstance(node, ast.Constant):
                operands.add(str(node.value))
                operand_count += 1

        n1 = len(operators)
        n2 = len(operands)
        N1 = operator_count
        N2 = operand_count

        return n1, n2, N1, N2

    def get_halstead_volume(self, source_code: str) -> float:
        """Halstead Volume を計算"""
        n1, n2, N1, N2 = self.get_halstead_metrics(source_code)

        if n1 + n2 == 0:
            return 0.0

        N = N1 + N2
        n = n1 + n2

        return N * math.log2(n) if n > 0 else 0.0

    def get_halstead_difficulty(self, source_code: str) -> float:
        """Halstead Difficulty を計算"""
        n1, n2, N1, N2 = self.get_halstead_metrics(source_code)

        if n2 == 0:
            return 0.0

        return (n1 / 2) * (N2 / n2)

    def get_halstead_effort(self, source_code: str) -> float:
        """Halstead Effort を計算"""
        volume = self.get_halstead_volume(source_code)
        difficulty = self.get_halstead_difficulty(source_code)

        return volume * difficulty

    def get_nesting_depth(self, source_code: str) -> float:
        """平均ネスト深度を取得"""
        if not source_code.strip():
            return 0.0

        tree = self.parse_source_code(source_code)
        depths = []

        def calculate_depth(node: ast.AST, current_depth: int = 0) -> None:
            if isinstance(
                node,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.FunctionDef,
                    ast.ClassDef,
                ),
            ):
                depths.append(current_depth)
                current_depth += 1

            for child in ast.iter_child_nodes(node):
                calculate_depth(child, current_depth)

        calculate_depth(tree)

        if not depths:
            return 0.0

        return sum(depths) / len(depths)

    def get_identifier_complexity(self, source_code: str) -> float:
        """識別子複雑度を取得"""
        variable_names = self.get_variable_names(source_code)
        if not variable_names:
            return 0.0

        complex_count = 0

        for name in variable_names:
            if len(name) <= self.config.min_variable_name_length - 1:
                complex_count += 1
            elif re.search(r"[A-Z]{2,}", name):
                complex_count += 1
            elif len(re.findall(r"[aeiouAEIOU]", name)) / len(name) < 0.2:
                complex_count += 1

        return complex_count / len(variable_names)
