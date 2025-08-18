"""コード構造解析モジュール."""
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
    """
    構造解析設定.

    Attributes
    ----------
    max_inheritance_depth : int
        最大継承深度, by default 5
    max_class_methods : int
        最大クラスメソッド数, by default 20
    """

    max_inheritance_depth: int = 5
    max_class_methods: int = 20


class DecoratorType(StrEnum):
    """
    デコレータタイプ.

    Attributes
    ----------
    STATIC_METHOD : str
        staticmethodデコレータ
    CLASS_METHOD : str
        classmethodデコレータ
    ABSTRACT_METHOD : str
        abstractmethodデコレータ
    PROPERTY : str
        propertyデコレータ
    """

    STATIC_METHOD = "staticmethod"
    CLASS_METHOD = "classmethod"
    ABSTRACT_METHOD = "abstractmethod"
    PROPERTY = "property"


class StructAnalysisResult(BaseAnalysisResult):
    """
    解析結果(構造).

    Attributes
    ----------
    function_count : int
        関数数
    class_count : int
        クラス数
    line_count : int
        行数
    argument_count : float
        引数の平均数（1関数あたりの平均引数数）
    return_type_hint : float
        戻り値の型ヒント割合
    staticmethod_rate : float
        staticmethod割合
    class_method_rate : float
        classmethod割合
    abstractmethod_rate : float
        abstractmethod割合
    property_rate : float
        property割合
    method_count : float
        メソッド数（クラス内の平均メソッド数）
    attribute_count : float
        属性数（クラス内の平均属性数）
    public_rate : float
        publicメソッド比率
    private_rate : float
        privateメソッド比率
    dependency : float
        依存度
    cohesion : float
        凝集度
    inheritance_depth : float
        クラス継承関係の深さの平均
    subclass_count : float
        子クラス数の平均
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
    """
    解析クラス(構造).

    Notes
    -----
    コードの構造を多角的に解析するクラス
    """

    def __init__(self, config: StructAnalysisConfig | None = None) -> None:
        """
        コンストラクタ.

        Parameters
        ----------
        config : StructAnalysisConfig | None, optional
            構造解析設定, by default None
        """
        super().__init__(config)

    def get_default_config(self) -> StructAnalysisConfig:
        """
        デフォルト設定を取得.

        Returns
        -------
        StructAnalysisConfig
            デフォルトの構造解析設定
        """
        return StructAnalysisConfig()

    def analyze(self, source_code: str) -> StructAnalysisResult:
        """
        コード解析.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        StructAnalysisResult
            構造解析結果
        """
        tree: ast.AST = self.parse_source_code(source_code)
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
        ) = self.get_class_information(source_code=source_code, tree=tree)
        inheritance_depth, subclass_count = self.get_inheritance_information(
            source_code=source_code, tree=tree
        )
        return StructAnalysisResult(
            function_count=self.get_function_count(source_code, tree),
            class_count=self.get_class_count(source_code, tree),
            line_count=self.get_line_count(source_code),
            argument_count=self.get_argument_count(source_code, tree),
            return_type_hint=self.get_return_type_hint(source_code, tree),
            staticmethod_rate=self.get_decorator_rate(
                source_code, DecoratorType.STATIC_METHOD, tree
            ),
            class_method_rate=self.get_decorator_rate(
                source_code, DecoratorType.CLASS_METHOD, tree
            ),
            abstractmethod_rate=self.get_decorator_rate(
                source_code, DecoratorType.ABSTRACT_METHOD, tree
            ),
            property_rate=self.get_decorator_rate(
                source_code, DecoratorType.PROPERTY, tree
            ),
            method_count=method_count,
            attribute_count=attribute_count,
            public_rate=public_rate,
            private_rate=private_rate,
            dependency=self.get_dependency(source_code, tree),
            cohesion=self.get_cohesion(source_code, tree),
            inheritance_depth=inheritance_depth,
            subclass_count=subclass_count,
        )

    def parse_source_code(self, source_code: str) -> ast.AST:
        """
        ソースコードを解析.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        ast.AST
            解析済みのAST
        """
        return ast.parse(source_code)

    def get_function_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """
        関数数を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        int
            関数数
        """
        tree = tree or self.parse_source_code(source_code)
        return sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

    def get_class_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """
        クラス数を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        int
            クラス数
        """
        tree = tree or self.parse_source_code(source_code)
        return sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

    def get_line_count(self, source_code: str) -> int:
        """
        行数を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        int
            行数
        """
        return len(source_code.splitlines())

    def get_argument_count(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        引数の数を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            引数の平均数
        """
        tree = tree or self.parse_source_code(source_code)
        total_argument_count = sum(
            isinstance(node, ast.arg)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        )

        if total_lines := self.get_line_count(source_code):
            return total_argument_count / total_lines

        return 0

    def get_return_type_hint(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        戻り値の型ヒント割合を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            戻り値の型ヒント割合
        """
        tree = tree or self.parse_source_code(source_code)
        return_hint_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.returns is not None
        )

        if function_count := self.get_function_count(source_code, tree):
            return return_hint_count / function_count

        return 0

    def get_decorator_rate(
        self,
        source_code: str,
        decorator_type: DecoratorType,
        tree: ast.AST | None = None,
    ) -> float:
        """
        デコレータ数を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        decorator_type : DecoratorType
            デコレータタイプ
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            デコレータ使用率
        """
        tree = tree or self.parse_source_code(source_code)
        decorator_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and any(
                isinstance(decorator, ast.Name) and decorator.id == decorator_type
                for decorator in node.decorator_list
            )
        )

        if function_count := self.get_function_count(source_code, tree):
            return decorator_count / function_count

        return 0

    def get_class_information(
        self, source_code: str, tree: ast.AST | None = None
    ) -> tuple[float, float, float, float]:
        """
        クラス情報を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        tuple[float, float, float, float]
            (メソッド数, 属性数, public比率, private比率)

        Notes
        -----
        クラス内のメソッド数・要素数・public/private比率を取得
        """
        tree = tree or self.parse_source_code(source_code)
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
            class_count = self.get_class_count(source_code, tree)
            return (
                method_count / class_count,
                attribute_count / class_count,
                public_count / method_count,
                private_count / method_count,
            )

        return 0, 0, 0, 0

    def get_dependency(self, source_code: str, tree: ast.AST | None = None) -> float:
        """
        依存度を平均呼び出し数で算出.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            依存度
        """
        tree = tree or ast.parse(source_code)
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

    def get_cohesion(self, source_code: str, tree: ast.AST | None = None) -> float:
        """
        凝集度をLCOMベースで算出.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            凝集度
        """
        tree = tree or self.parse_source_code(source_code)

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

    def get_inheritance_information(
        self, source_code: str, tree: ast.AST | None = None
    ) -> tuple[float, float]:
        """
        クラス継承関係情報を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        tuple[float, float]
            (継承深度, 子クラス数)

        Notes
        -----
        クラス継承関係の深さと子クラス数を取得
        """
        tree = tree or self.parse_source_code(source_code)
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
