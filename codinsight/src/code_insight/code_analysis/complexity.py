import ast

import radon.complexity as cc
import radon.metrics as metrics

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class ComplexityAnalysisConfig(BaseAnalysisConfig):
    """複雑度解析設定"""

    max_nesting_depth_threshold: int = 5
    cognitive_complexity_threshold: float = 10.0


class ComplexityAnalysisResult(BaseAnalysisResult):
    """
    解析結果(複雑度)
    * サイクロマティック複雑度
        * 関数・メソッドの平均サイクロマティック複雑度
    * Halstead複雑度
        * Halstead Volume, Difficulty, Effort
    * ネストの深さ
        * 最大ネスト深度と平均ネスト深度
    * 認知的複雑度
        * 制御構造の複雑さを測定
    * 保守性指数
        * Maintainability Index
    """

    cyclomatic_complexity: float
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    max_nesting_depth: int
    avg_nesting_depth: float
    cognitive_complexity: float
    maintainability_index: float


class Complexity(AbstractAnalysis[ComplexityAnalysisResult, ComplexityAnalysisConfig]):
    """解析クラス(複雑度)"""

    def __init__(self, config: ComplexityAnalysisConfig | None = None) -> None:
        """コンストラクタ"""
        super().__init__(config)

    def get_default_config(self) -> ComplexityAnalysisConfig:
        """デフォルト設定を取得"""
        return ComplexityAnalysisConfig()

    def analyze(self, source_code: str) -> ComplexityAnalysisResult:
        """コード解析"""
        tree = ast.parse(source_code) if source_code.strip() else ast.parse("")
        if not self.config.enabled:
            return ComplexityAnalysisResult(
                cyclomatic_complexity=0.0,
                halstead_volume=0.0,
                halstead_difficulty=0.0,
                halstead_effort=0.0,
                max_nesting_depth=0,
                avg_nesting_depth=0.0,
                cognitive_complexity=0.0,
                maintainability_index=0.0,
            )

        return ComplexityAnalysisResult(
            cyclomatic_complexity=self.get_cyclomatic_complexity(source_code),
            halstead_volume=self.get_halstead_volume(source_code),
            halstead_difficulty=self.get_halstead_difficulty(source_code),
            halstead_effort=self.get_halstead_effort(source_code),
            max_nesting_depth=self.get_max_nesting_depth(source_code, tree),
            avg_nesting_depth=self.get_avg_nesting_depth(source_code, tree),
            cognitive_complexity=self.get_cognitive_complexity(source_code, tree),
            maintainability_index=self.get_maintainability_index(source_code),
        )

    def get_cyclomatic_complexity(self, source_code: str) -> float:
        """サイクロマティック複雑度の平均を取得"""
        if not source_code.strip():
            return 0.0

        try:
            cc_result = cc.cc_visit(source_code)
            if not cc_result:
                return 0.0

            total_complexity = sum(item.complexity for item in cc_result)
            return total_complexity / len(cc_result)
        except Exception:
            return 0.0

    def get_halstead_volume(self, source_code: str) -> float:
        """Halstead Volumeを取得"""
        if not source_code.strip():
            return 0.0

        try:
            h_result = metrics.h_visit(source_code)
            return h_result.total.volume if h_result.total else 0.0
        except Exception:
            return 0.0

    def get_halstead_difficulty(self, source_code: str) -> float:
        """Halstead Difficultyを取得"""
        if not source_code.strip():
            return 0.0

        try:
            h_result = metrics.h_visit(source_code)
            return h_result.total.difficulty if h_result.total else 0.0
        except Exception:
            return 0.0

    def get_halstead_effort(self, source_code: str) -> float:
        """Halstead Effortを取得"""
        if not source_code.strip():
            return 0.0

        try:
            h_result = metrics.h_visit(source_code)
            return h_result.total.effort if h_result.total else 0.0
        except Exception:
            return 0.0

    def get_maintainability_index(self, source_code: str) -> float:
        """保守性指数を取得"""
        if not source_code.strip():
            return 0.0

        try:
            return metrics.mi_visit(source_code, multi=True)
        except Exception:
            return 0.0

    def get_max_nesting_depth(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """最大ネスト深度を取得"""
        if not source_code.strip() and tree is None:
            return 0

        try:
            tree = tree or ast.parse(source_code)
            max_depth = 0

            def calculate_depth(node: ast.AST, current_depth: int = 0) -> int:
                nonlocal max_depth

                nesting_nodes = (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.With,
                    ast.Try,
                    ast.FunctionDef,
                    ast.ClassDef,
                    ast.AsyncFor,
                    ast.AsyncWith,
                )

                if isinstance(node, nesting_nodes):
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)

                for child in ast.iter_child_nodes(node):
                    calculate_depth(child, current_depth)

                return max_depth

            return calculate_depth(tree)
        except Exception:
            return 0

    def get_avg_nesting_depth(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """平均ネスト深度を取得"""
        if not source_code.strip() and tree is None:
            return 0.0

        try:
            tree = tree or ast.parse(source_code)
            depths = []

            def collect_depths(node: ast.AST, current_depth: int = 0) -> None:
                nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try)

                if isinstance(node, nesting_nodes):
                    current_depth += 1
                    depths.append(current_depth)

                for child in ast.iter_child_nodes(node):
                    collect_depths(child, current_depth)

            collect_depths(tree)
            return sum(depths) / len(depths) if depths else 0.0
        except Exception:
            return 0.0

    def get_cognitive_complexity(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """認知的複雑度を取得"""
        if not source_code.strip() and tree is None:
            return 0.0

        try:
            tree = tree or ast.parse(source_code)
            complexity = 0

            def calculate_cognitive_complexity(
                node: ast.AST, nesting_level: int = 0
            ) -> int:
                nonlocal complexity

                if isinstance(node, (ast.If, ast.While, ast.For)):
                    complexity += 1 + nesting_level
                elif isinstance(node, ast.Try):
                    complexity += 1 + nesting_level
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1 + nesting_level
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1

                nesting_increment_nodes = (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                )

                new_nesting_level = nesting_level
                if isinstance(node, nesting_increment_nodes):
                    new_nesting_level += 1

                for child in ast.iter_child_nodes(node):
                    calculate_cognitive_complexity(child, new_nesting_level)

                return complexity

            return float(calculate_cognitive_complexity(tree))
        except Exception:
            return 0.0
