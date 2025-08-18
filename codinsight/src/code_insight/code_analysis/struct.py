import ast
import itertools
from collections import defaultdict
from enum import StrEnum

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class StructAnalysisConfig(BaseAnalysisConfig):
    """構造解析設定"""

    max_inheritance_depth: int = 5
    max_class_methods: int = 20


class DecoratorType(StrEnum):
    """
    デコレータタイプ
    * staticmethod
    * classmethod
    * abstractmethod
    * property
    """

    STATIC_METHOD = "staticmethod"
    CLASS_METHOD = "classmethod"
    ABSTRACT_METHOD = "abstractmethod"
    PROPERTY = "property"


class StructAnalysisResult(BaseAnalysisResult):
    """
    解析結果(構造)
    * 関数数
    * クラス数
    * 行数
    * 引数の平均数
        * 1関数あたりの平均引数数
    * 戻り値の型ヒント割合
    * staticmethod割合
    * classmethod割合
    * abstractmethod割合
    * property割合
    * メソッド数
        * クラス内の平均メソッド数
    * 属性数
        * クラス内の平均属性数
    * メソッド比率(public/private)
        * クラス内のメソッド比率
    * 依存度
    * 凝集度
    * クラス継承関係の深さの平均
    * 子クラス数の平均
    """

    function_count: int
    class_count: int
    line_count: int
    argument_count: float
    return_type_hint: float
    staticmethod_rate: float
    class_method_rate: float
    abstractmethod_rate: float
    property_rate: float
    method_count: float
    attribute_count: float
    public_rate: float
    private_rate: float
    dependency: float
    cohesion: float
    inheritance_depth: float
    subclass_count: float


class Struct(AbstractAnalysis[StructAnalysisResult, StructAnalysisConfig]):
    """解析クラス(構造)"""

    def __init__(self, config: StructAnalysisConfig | None = None) -> None:
        """コンストラクタ"""
        super().__init__(config)

    def get_default_config(self) -> StructAnalysisConfig:
        """デフォルト設定を取得"""
        return StructAnalysisConfig()

    def analyze(self, source_code: str) -> StructAnalysisResult:
        """コード解析"""
        if not self.config.enabled:
            return StructAnalysisResult(
                function_count=0,
                class_count=0,
                line_count=0,
                argument_count=0.0,
                return_type_hint=0.0,
                staticmethod_rate=0.0,
                class_method_rate=0.0,
                abstractmethod_rate=0.0,
                property_rate=0.0,
                method_count=0.0,
                attribute_count=0.0,
                public_rate=0.0,
                private_rate=0.0,
                dependency=0.0,
                cohesion=0.0,
                inheritance_depth=0.0,
                subclass_count=0.0,
            )

        (
            method_count,
            attribute_count,
            public_rate,
            private_rate,
        ) = self.get_class_information(source_code=source_code)
        inheritance_depth, subclass_count = self.get_inheritance_information(
            source_code=source_code
        )
        return StructAnalysisResult(
            function_count=self.get_function_count(source_code),
            class_count=self.get_class_count(source_code),
            line_count=self.get_line_count(source_code),
            argument_count=self.get_argument_count(source_code),
            return_type_hint=self.get_return_type_hint(source_code),
            staticmethod_rate=self.get_decorator_rate(
                source_code, DecoratorType.STATIC_METHOD
            ),
            class_method_rate=self.get_decorator_rate(
                source_code, DecoratorType.CLASS_METHOD
            ),
            abstractmethod_rate=self.get_decorator_rate(
                source_code, DecoratorType.ABSTRACT_METHOD
            ),
            property_rate=self.get_decorator_rate(source_code, DecoratorType.PROPERTY),
            method_count=method_count,
            attribute_count=attribute_count,
            public_rate=public_rate,
            private_rate=private_rate,
            dependency=self.get_dependency(source_code),
            cohesion=self.get_cohesion(source_code),
            inheritance_depth=inheritance_depth,
            subclass_count=subclass_count,
        )

    def parse_source_code(self, source_code: str) -> ast.AST:
        """ソースコードを解析"""
        return ast.parse(source_code)

    def get_function_count(self, source_code: str) -> int:
        """関数数を取得"""
        tree: ast.AST = self.parse_source_code(source_code)
        return sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

    def get_class_count(self, source_code: str) -> int:
        """クラス数を取得"""
        tree: ast.AST = self.parse_source_code(source_code)
        return sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

    def get_line_count(self, source_code: str) -> int:
        """行数を取得"""
        return len(source_code.splitlines())

    def get_argument_count(self, source_code: str) -> float:
        """引数の数を取得"""
        tree: ast.AST = self.parse_source_code(source_code)
        total_argument_count = sum(
            isinstance(node, ast.arg)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        )

        if total_lines := self.get_line_count(source_code):
            return total_argument_count / total_lines

        return 0

    def get_return_type_hint(self, source_code: str) -> float:
        """戻り値の型ヒント割合を取得"""
        tree: ast.AST = self.parse_source_code(source_code)
        return_hint_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.returns is not None
        )

        if function_count := self.get_function_count(source_code):
            return return_hint_count / function_count

        return 0

    def get_decorator_rate(
        self, source_code: str, decorator_type: DecoratorType
    ) -> float:
        """デコレータ数を取得"""
        tree: ast.AST = self.parse_source_code(source_code)
        decorator_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and any(
                isinstance(decorator, ast.Name) and decorator.id == decorator_type
                for decorator in node.decorator_list
            )
        )

        if function_count := self.get_function_count(source_code):
            return decorator_count / function_count

        return 0

    def get_class_information(
        self, source_code: str
    ) -> tuple[float, float, float, float]:
        """
        クラス情報を取得
        * クラス内のメソッド数・要素数・public/private比率を取得
        """
        tree: ast.AST = self.parse_source_code(source_code)
        method_count = 0
        attribute_count = 0
        public_count = 0
        private_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.FunctionDef):
                        method_count += 1
                        if child.name.startswith("__") and child.name.endswith("__"):
                            private_count += 1
                        else:
                            public_count += 1
                    elif isinstance(child, ast.Assign):
                        attribute_count += 1

        if method_count:
            class_count = self.get_class_count(source_code)
            return (
                method_count / class_count,
                attribute_count / class_count,
                public_count / method_count,
                private_count / method_count,
            )

        return 0, 0, 0, 0

    def get_dependency(self, source_code: str) -> float:
        """依存度を平均呼び出し数で算出"""
        tree = ast.parse(source_code)
        graph = defaultdict(set)

        class Visitor(ast.NodeVisitor):
            def __init__(self, func_name: str) -> None:
                self.func_name = func_name

            def visit_Call(self, node: ast.Call) -> None:
                if isinstance(node.func, ast.Name):
                    if node.func.id != self.func_name:  # 自己呼び出しは除外
                        graph[self.func_name].add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr != self.func_name:
                        graph[self.func_name].add(node.func.attr)
                self.generic_visit(node)

        # 関数/メソッドすべてにVisitorを適用
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                Visitor(node.name).visit(node)
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        Visitor(f"{node.name}.{item.name}").visit(item)

        total_calls = sum(len(callees) for callees in graph.values())
        num_funcs = max(1, len(graph))  # 0割防止

        return total_calls / num_funcs

    def get_cohesion(self, source_code: str) -> float:
        """凝集度をLCOMベースで算出"""
        tree: ast.AST = self.parse_source_code(source_code)

        # 各メソッドが参照する属性
        attr_usage = defaultdict(set)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for sub in ast.walk(node):
                    if (
                        isinstance(sub, ast.Attribute)
                        and isinstance(sub.value, ast.Name)
                        and sub.value.id == "self"
                    ):
                        attr_usage[node.name].add(sub.attr)
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for sub in ast.walk(item):
                            if (
                                isinstance(sub, ast.Attribute)
                                and isinstance(sub.value, ast.Name)
                                and sub.value.id == "self"
                            ):
                                attr_usage[f"{node.name}.{item.name}"].add(sub.attr)

        methods = list(attr_usage.keys())
        if len(methods) < 2:
            return 1.0  # メソッドが少なければ凝集度は高いとみなす

        shared = 0
        total = 0
        for m1, m2 in itertools.combinations(methods, 2):
            total += 1
            if attr_usage[m1] & attr_usage[m2]:
                shared += 1

        return shared / total if total > 0 else 1.0

    def get_inheritance_information(self, source_code: str) -> tuple[float, float]:
        """
        クラス継承関係情報を取得
        * クラス継承関係の深さ
        * 子クラス数
        """
        tree: ast.AST = self.parse_source_code(source_code)
        inheritance: dict[str, list[str]] = {}
        children = defaultdict(list)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
                inheritance[node.name] = bases
                for base in bases:
                    children[base].append(node.name)

        def calculate_depth(class_name: str) -> int:
            if not inheritance.get(class_name):
                return 0
            return 1 + max(
                (calculate_depth(base) for base in inheritance[class_name]), default=0
            )

        if not inheritance:
            return 0, 0

        depth = sum(calculate_depth(class_name) for class_name in inheritance) / len(
            inheritance
        )
        chidren_count = sum(
            len(children[class_name]) for class_name in inheritance
        ) / len(inheritance)

        return depth, chidren_count
