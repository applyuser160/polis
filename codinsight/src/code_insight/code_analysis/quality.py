import ast
import re

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class QualityAnalysisConfig(BaseAnalysisConfig):
    """
    品質解析設定

    Attributes
    ----------
    long_param_threshold : int
        長引数関数の閾値, by default 5
    """

    long_param_threshold: int = 5


class QualityAnalysisResult(BaseAnalysisResult):
    """
    解析結果(品質)

    Attributes
    ----------
    type_hint_coverage : float
        型ヒント網羅率（引数・戻り値に型注釈が付与されている割合）
    docstring_coverage : float
        docstringカバレッジ（モジュール・関数・クラスのdocstringが記載されている割合）
    exception_handling_rate : float
        例外ハンドリング率（try文の数を関数数で割った割合）
    avg_function_length : float
        平均関数行数（関数定義ごとの行数の平均）
    long_parameter_function_rate : float
        長引数関数割合（引数個数が閾値を超える関数の割合）
    assert_count : int
        アサーション数（assert文の総数）
    todo_comment_rate : float
        TODOコメント率（TODO/FIXMEを含む行の割合）
    """

    type_hint_coverage: float
    docstring_coverage: float
    exception_handling_rate: float
    avg_function_length: float
    long_parameter_function_rate: float
    assert_count: int
    todo_comment_rate: float


class Quality(AbstractAnalysis[QualityAnalysisResult, QualityAnalysisConfig]):
    """
    解析クラス(品質)

    Notes
    -----
    コードの品質を多角的に解析するクラス
    """

    def __init__(self, config: QualityAnalysisConfig | None = None) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        config : QualityAnalysisConfig | None, optional
            品質解析設定, by default None
        """
        super().__init__(config)

    def get_default_config(self) -> QualityAnalysisConfig:
        """
        デフォルト設定を取得

        Returns
        -------
        QualityAnalysisConfig
            デフォルトの品質解析設定
        """
        return QualityAnalysisConfig()

    def analyze(self, source_code: str) -> QualityAnalysisResult:
        """
        コード解析

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        QualityAnalysisResult
            品質解析結果
        """
        tree = self.parse_source_code(source_code)
        if not self.config.enabled:
            return QualityAnalysisResult(
                type_hint_coverage=0.0,
                docstring_coverage=0.0,
                exception_handling_rate=0.0,
                avg_function_length=0.0,
                long_parameter_function_rate=0.0,
                assert_count=0,
                todo_comment_rate=0.0,
            )

        return QualityAnalysisResult(
            type_hint_coverage=self.get_type_hint_coverage(source_code, tree),
            docstring_coverage=self.get_docstring_coverage(source_code, tree),
            exception_handling_rate=self.get_exception_handling_rate(source_code, tree),
            avg_function_length=self.get_avg_function_length(source_code, tree),
            long_parameter_function_rate=self.get_long_parameter_function_rate(
                source_code, tree
            ),
            assert_count=self.get_assert_count(source_code, tree),
            todo_comment_rate=self.get_todo_comment_rate(source_code),
        )

    def parse_source_code(self, source_code: str) -> ast.AST:
        """
        ソースコードを解析

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        ast.AST
            解析済みのAST
        """
        return ast.parse(source_code or "")

    def get_functions(self, tree: ast.AST) -> list[ast.FunctionDef]:
        """
        関数定義を取得

        Parameters
        ----------
        tree : ast.AST
            解析済みのAST

        Returns
        -------
        list[ast.FunctionDef]
            関数定義のリスト
        """
        return [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

    def get_type_hint_coverage(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        型ヒント網羅率を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            型ヒント網羅率
        """
        if not source_code.strip() and tree is None:
            return 0.0

        tree = tree or self.parse_source_code(source_code)
        funcs = self.get_functions(tree)
        if not funcs:
            return 0.0

        annotated = 0
        total = 0

        for fn in funcs:
            posonly = getattr(fn.args, "posonlyargs", [])
            args = list(posonly) + list(fn.args.args)
            kwonly = list(fn.args.kwonlyargs)

            total_params = len(args) + len(kwonly)
            if fn.args.vararg is not None:
                total_params += 1
            if fn.args.kwarg is not None:
                total_params += 1

            annotated_params = sum(1 for a in args if a.annotation is not None) + sum(
                1 for a in kwonly if a.annotation is not None
            )
            if fn.args.vararg is not None and fn.args.vararg.annotation is not None:
                annotated_params += 1
            if fn.args.kwarg is not None and fn.args.kwarg.annotation is not None:
                annotated_params += 1

            total += total_params + 1
            annotated += annotated_params + (1 if fn.returns is not None else 0)

        if total == 0:
            return 0.0
        return annotated / total

    def get_docstring_coverage(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        docstringカバレッジを取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            docstringカバレッジ
        """
        if not source_code.strip() and tree is None:
            return 0.0

        tree = tree or self.parse_source_code(source_code)
        targets = [tree]
        targets.extend(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
        targets.extend(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))

        total = len(targets)
        if total == 0:
            return 0.0

        with_doc = sum(True for t in targets if ast.get_docstring(t))  # type: ignore
        return with_doc / total

    def get_exception_handling_rate(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        例外ハンドリング率を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            例外ハンドリング率
        """
        if not source_code.strip() and tree is None:
            return 0.0
        tree = tree or self.parse_source_code(source_code)
        try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
        func_count = len(self.get_functions(tree))
        if func_count == 0:
            return 0.0
        return try_count / func_count

    def _count_function_lines(
        self, func_node: ast.FunctionDef, source_code: str
    ) -> int:
        """
        関数の行数をカウント

        Parameters
        ----------
        func_node : ast.FunctionDef
            関数定義ノード
        source_code : str
            ソースコード

        Returns
        -------
        int
            関数の行数
        """
        if hasattr(func_node, "end_lineno") and func_node.end_lineno:
            return int(func_node.end_lineno) - int(func_node.lineno) + 1

        lines = source_code.splitlines()
        if func_node.lineno <= len(lines):
            start = func_node.lineno - 1
            for i in range(start + 1, len(lines)):
                line = lines[i].rstrip("\n")
                if line and not line.startswith(" ") and not line.startswith("\t"):
                    return i - start
            return len(lines) - start
        return 1

    def get_avg_function_length(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        平均関数行数を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            平均関数行数
        """
        if not source_code.strip() and tree is None:
            return 0.0
        tree = tree or self.parse_source_code(source_code)
        funcs = self.get_functions(tree)
        if not funcs:
            return 0.0
        total = sum(self._count_function_lines(fn, source_code) for fn in funcs)
        return total / len(funcs)

    def get_long_parameter_function_rate(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        長引数関数割合を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            長引数関数割合
        """
        if not source_code.strip() and tree is None:
            return 0.0
        tree = tree or self.parse_source_code(source_code)
        funcs = self.get_functions(tree)
        if not funcs:
            return 0.0

        def param_count(fn: ast.FunctionDef) -> int:
            posonly = getattr(fn.args, "posonlyargs", [])
            count = len(posonly) + len(fn.args.args) + len(fn.args.kwonlyargs)
            if fn.args.vararg is not None:
                count += 1
            if fn.args.kwarg is not None:
                count += 1
            return count

        long_count = sum(
            1 for f in funcs if param_count(f) > self.config.long_param_threshold
        )
        return long_count / len(funcs)

    def get_assert_count(self, source_code: str, tree: ast.AST | None = None) -> int:
        """
        アサーション数を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        int
            アサーション数
        """
        if not source_code.strip() and tree is None:
            return 0
        tree = tree or self.parse_source_code(source_code)
        return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))

    def get_todo_comment_rate(self, source_code: str) -> float:
        """
        TODOコメント率を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        float
            TODOコメント率
        """
        lines = source_code.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return 0.0
        todo_re = re.compile(r"\b(TODO|FIXME)\b", re.IGNORECASE)
        todo_lines = sum(1 for line in non_empty_lines if todo_re.search(line))
        return todo_lines / len(non_empty_lines)
