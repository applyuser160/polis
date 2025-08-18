import ast
from typing import Set

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class AlgorithmAnalysisConfig(BaseAnalysisConfig):
    """
    アルゴリズム解析設定
    * 最大ネスト深度閾値
    * サイクロマティック複雑度閾値
    """

    max_nesting_depth_threshold: int = 4
    cyclomatic_complexity_threshold: float = 5.0


class AlgorithmAnalysisResult(BaseAnalysisResult):
    """
    解析結果(アルゴリズム)
    * 制御構文
        * if文の数
        * for文の数
        * while文の数
        * try-except文の数
    * 再帰構造
        * 再帰関数の割合
    * FP的要素
        * lambda式の数
        * リスト内包表記の数
        * map/filter/reduce呼び出しの数
    * ネスト深度
        * 制御構文の最大ネスト深度
    """

    if_count: int
    for_count: int
    while_count: int
    try_count: int
    recursion_rate: float
    lambda_count: int
    comprehension_count: int
    functional_call_count: int
    max_nesting_depth: int


class Algorithm(AbstractAnalysis[AlgorithmAnalysisResult, AlgorithmAnalysisConfig]):
    """解析クラス(アルゴリズム)"""

    def __init__(self, config: AlgorithmAnalysisConfig | None = None) -> None:
        """コンストラクタ"""
        super().__init__(config)

    def get_default_config(self) -> AlgorithmAnalysisConfig:
        """デフォルト設定を取得"""
        return AlgorithmAnalysisConfig()

    def analyze(self, source_code: str) -> AlgorithmAnalysisResult:
        """コード解析"""
        if not self.config.enabled:
            return AlgorithmAnalysisResult(
                if_count=0,
                for_count=0,
                while_count=0,
                try_count=0,
                recursion_rate=0.0,
                lambda_count=0,
                comprehension_count=0,
                functional_call_count=0,
                max_nesting_depth=0,
            )

        tree = self.parse_source_code(source_code)

        return AlgorithmAnalysisResult(
            if_count=self.get_if_count(source_code, tree),
            for_count=self.get_for_count(source_code, tree),
            while_count=self.get_while_count(source_code, tree),
            try_count=self.get_try_count(source_code, tree),
            recursion_rate=self.get_recursion_rate(source_code, tree),
            lambda_count=self.get_lambda_count(source_code, tree),
            comprehension_count=self.get_comprehension_count(source_code, tree),
            functional_call_count=self.get_functional_call_count(source_code, tree),
            max_nesting_depth=self.get_max_nesting_depth(source_code, tree),
        )

    def parse_source_code(self, source_code: str) -> ast.AST:
        """ソースコードを解析"""
        return ast.parse(source_code)

    def get_if_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """if文の数を取得"""
        tree = tree or self.parse_source_code(source_code)
        return sum(isinstance(node, ast.If) for node in ast.walk(tree))

    def get_for_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """for文の数を取得"""
        tree = tree or self.parse_source_code(source_code)
        return sum(isinstance(node, (ast.For, ast.AsyncFor)) for node in ast.walk(tree))

    def get_while_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """while文の数を取得"""
        tree = tree or self.parse_source_code(source_code)
        return sum(isinstance(node, ast.While) for node in ast.walk(tree))

    def get_try_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """try-except文の数を取得"""
        tree = tree or self.parse_source_code(source_code)
        return sum(isinstance(node, ast.Try) for node in ast.walk(tree))

    def get_recursion_rate(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """再帰関数の割合を取得"""
        tree = tree or self.parse_source_code(source_code)
        function_names: Set[str] = set()
        recursive_functions: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_names.add(node.name)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for call_node in ast.walk(node):
                    if (
                        isinstance(call_node, ast.Call)
                        and isinstance(call_node.func, ast.Name)
                        and call_node.func.id == node.name
                    ):
                        recursive_functions.add(node.name)

        if function_names:
            return len(recursive_functions) / len(function_names)
        return 0.0

    def get_lambda_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """lambda式の数を取得"""
        tree = tree or self.parse_source_code(source_code)
        return sum(isinstance(node, ast.Lambda) for node in ast.walk(tree))

    def get_comprehension_count(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """内包表記の数を取得"""
        tree = tree or self.parse_source_code(source_code)
        return sum(
            isinstance(
                node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
            )
            for node in ast.walk(tree)
        )

    def get_functional_call_count(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """map/filter/reduce呼び出しの数を取得"""
        tree = tree or self.parse_source_code(source_code)
        functional_names = {"map", "filter", "reduce"}
        count = 0

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in functional_names
            ):
                count += 1

        return count

    def get_cyclomatic_complexity(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """循環的複雑度の平均を取得"""
        tree = tree or self.parse_source_code(source_code)
        complexities = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_function_complexity(node)
                complexities.append(complexity)

        return sum(complexities) / len(complexities) if complexities else 0.0

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """関数の循環的複雑度を計算"""
        complexity = 1

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def get_max_nesting_depth(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """制御構文の最大ネスト深度を取得"""
        tree = tree or self.parse_source_code(source_code)
        max_depth = 0

        def calculate_depth(node: ast.AST, current_depth: int = 0) -> None:
            nonlocal max_depth

            if isinstance(
                node,
                (
                    ast.If,
                    ast.For,
                    ast.AsyncFor,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.AsyncWith,
                ),
            ):
                current_depth += 1
                max_depth = max(max_depth, current_depth)

            for child in ast.iter_child_nodes(node):
                calculate_depth(child, current_depth)

        calculate_depth(tree)
        return max_depth
