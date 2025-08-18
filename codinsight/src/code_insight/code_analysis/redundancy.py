import ast
import hashlib
from collections import defaultdict
from typing import Dict, List, Set

from radon.complexity import cc_visit

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class RedundancyAnalysisConfig(BaseAnalysisConfig):
    """冗長度解析設定"""

    long_function_lines_threshold: int = 50
    long_function_complexity_threshold: int = 10
    ignored_function_names: set[str] = {"main", "__init__", "__main__"}


class RedundancyAnalysisResult(BaseAnalysisResult):
    """
    解析結果(冗長度)
    * 重複コード割合
        * 構造的に類似した関数の割合
    * 未使用コード割合
        * 定義されているが呼び出されていない関数・クラスの割合
    * 長大関数割合
        * 50行以上または循環的複雑度10以上の関数の割合
    """

    duplicate_code_rate: float
    unused_code_rate: float
    long_function_rate: float


class Redundancy(AbstractAnalysis[RedundancyAnalysisResult, RedundancyAnalysisConfig]):
    """解析クラス(冗長度)"""

    def __init__(self, config: RedundancyAnalysisConfig | None = None) -> None:
        """コンストラクタ"""
        super().__init__(config)

    def get_default_config(self) -> RedundancyAnalysisConfig:
        """デフォルト設定を取得"""
        return RedundancyAnalysisConfig()

    def analyze(self, source_code: str) -> RedundancyAnalysisResult:
        """コード解析"""
        if not self.config.enabled:
            return RedundancyAnalysisResult(
                duplicate_code_rate=0.0,
                unused_code_rate=0.0,
                long_function_rate=0.0,
            )

        tree = self.parse_source_code(source_code)
        return RedundancyAnalysisResult(
            duplicate_code_rate=self.get_duplicate_code_rate(source_code, tree),
            unused_code_rate=self.get_unused_code_rate(source_code, tree),
            long_function_rate=self.get_long_function_rate(source_code, tree),
        )

    def parse_source_code(self, source_code: str) -> ast.AST:
        """ソースコードを解析"""
        return ast.parse(source_code)

    def get_duplicate_code_rate(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """重複コード割合を取得"""
        if not source_code.strip():
            return 0.0

        tree = tree or self.parse_source_code(source_code)
        function_hashes: Dict[str, List[str]] = defaultdict(list)
        total_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                func_hash = self._get_function_structure_hash(node)
                function_hashes[func_hash].append(node.name)

        if total_functions == 0:
            return 0.0

        duplicate_functions = sum(
            len(functions) - 1
            for functions in function_hashes.values()
            if len(functions) > 1
        )

        return duplicate_functions / total_functions

    def get_unused_code_rate(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """未使用コード割合を取得"""
        if not source_code.strip():
            return 0.0

        tree = tree or self.parse_source_code(source_code)
        defined_names: Set[str] = set()
        called_names: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name not in self.config.ignored_function_names:
                    defined_names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                defined_names.add(node.name)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_names.add(node.func.attr)

        if not defined_names:
            return 0.0

        unused_names = defined_names - called_names
        return len(unused_names) / len(defined_names)

    def get_long_function_rate(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """長大関数割合を取得"""
        if not source_code.strip():
            return 0.0

        tree = tree or self.parse_source_code(source_code)
        long_functions = 0
        total_functions = 0

        try:
            complexity_results = cc_visit(source_code)
            complexity_map = {
                result.name: result.complexity for result in complexity_results
            }
        except Exception:
            complexity_map = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1

                func_lines = self._count_function_lines(node, source_code)
                func_complexity = complexity_map.get(node.name, 1)

                if (
                    func_lines >= self.config.long_function_lines_threshold
                    or func_complexity >= self.config.long_function_complexity_threshold
                ):
                    long_functions += 1

        if total_functions == 0:
            return 0.0

        return long_functions / total_functions

    def _get_function_structure_hash(self, func_node: ast.FunctionDef) -> str:
        """関数の構造的ハッシュを取得"""
        structure_elements = []

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                structure_elements.append(type(node).__name__)
            elif isinstance(node, ast.Return):
                if isinstance(node.value, ast.Constant):
                    node_value = node.value.value
                    if isinstance(node_value, bytes):
                        node_value = node_value.decode()
                    structure_elements.append(
                        f"return_const_{type(node.value.value).__name__}_"
                        f"{node_value}"
                    )
                elif isinstance(node.value, ast.BinOp):
                    structure_elements.append(
                        f"return_binop_{type(node.value.op).__name__}"
                    )
                else:
                    structure_elements.append("return_other")
            elif isinstance(node, ast.Assign):
                structure_elements.append("assign")
            elif isinstance(node, ast.BinOp):
                structure_elements.append(f"binop_{type(node.op).__name__}")

        arg_count = len(func_node.args.args)
        structure_elements.append(f"args_{arg_count}")

        if len(structure_elements) < 3:
            structure_elements.append(f"simple_{len(func_node.body)}")

        structure_str = "_".join(structure_elements)
        return hashlib.md5(structure_str.encode(), usedforsecurity=False).hexdigest()

    def _count_function_lines(
        self, func_node: ast.FunctionDef, source_code: str
    ) -> int:
        """関数の行数をカウント"""
        if hasattr(func_node, "end_lineno") and func_node.end_lineno:
            return func_node.end_lineno - func_node.lineno + 1

        lines = source_code.splitlines()
        if func_node.lineno <= len(lines):
            func_start = func_node.lineno - 1
            for i in range(func_start + 1, len(lines)):
                line = lines[i].strip()
                if line and not line.startswith(" ") and not line.startswith("\t"):
                    return i - func_start
            return len(lines) - func_start

        return 1
