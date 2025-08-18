"""コードスタイル解析モジュール."""
import ast
import re

import pycodestyle

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class StyleAnalysisConfig(BaseAnalysisConfig):
    """
    スタイル解析設定.

    Attributes
    ----------
    function_name_pattern : str
        関数名のパターン, by default r"^[a-z_][a-z0-9_]*$"
    class_name_pattern : str
        クラス名のパターン, by default r"^[A-Z][a-zA-Z0-9]*$"
    """

    function_name_pattern: str = r"^[a-z_][a-z0-9_]*$"
    class_name_pattern: str = r"^[A-Z][a-zA-Z0-9]*$"


class StyleAnalysisResult(BaseAnalysisResult):
    """
    解析結果(スタイル).

    Attributes
    ----------
    naming_convention : float
        命名規則（変数名、関数名の一貫性）
    comment_rate : float
        コメント率（ソースコード中のコメント率）
    docstring_rate : float
        docstring率（関数、クラス、モジュールのうち、docstringが書かれている割合）
    pep8_violation_rate : float
        PEP8違反率（ソースコード中のPEP8に違反している割合）
    """

    naming_convention: float
    comment_rate: float
    docstring_rate: float
    pep8_violation_rate: float


class Style(AbstractAnalysis[StyleAnalysisResult, StyleAnalysisConfig]):
    """
    解析クラス(スタイル).

    Notes
    -----
    コードのスタイルを多角的に解析するクラス
    """

    def __init__(self, config: StyleAnalysisConfig | None = None) -> None:
        """
        コンストラクタ.

        Parameters
        ----------
        config : StyleAnalysisConfig | None, optional
            スタイル解析設定, by default None
        """
        super().__init__(config)

    def get_default_config(self) -> StyleAnalysisConfig:
        """
        デフォルト設定を取得.

        Returns
        -------
        StyleAnalysisConfig
            デフォルトのスタイル解析設定
        """
        return StyleAnalysisConfig()

    def analyze(self, source_code: str) -> StyleAnalysisResult:
        """
        コード解析.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        StyleAnalysisResult
            スタイル解析結果
        """
        tree = ast.parse(source_code)
        if not self.config.enabled:
            return StyleAnalysisResult(
                naming_convention=0.0,
                comment_rate=0.0,
                docstring_rate=0.0,
                pep8_violation_rate=0.0,
            )

        return StyleAnalysisResult(
            naming_convention=self.get_naming_convention(source_code, tree),
            comment_rate=self.get_comment_rate(source_code),
            docstring_rate=self.get_docstring_rate(source_code, tree),
            pep8_violation_rate=self.get_pep8_violation_rate(source_code),
        )

    def get_naming_convention(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        命名規則の一貫性を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            命名規則違反数
        """
        tree = tree or ast.parse(source_code)
        violations = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(self.config.function_name_pattern, node.name):
                    violations += 1
            if isinstance(node, ast.ClassDef):
                if not re.match(self.config.class_name_pattern, node.name):
                    violations += 1

        return violations

    def get_total_lines(self, source_code: str) -> int:
        """
        行数を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        int
            総行数
        """
        return len(source_code.splitlines())

    def get_comment_rate(self, source_code: str) -> float:
        """
        コメント率を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        float
            コメント率
        """
        comment_count = sum(
            1 for line in source_code.splitlines() if line.strip().startswith("#")
        )

        if total_lines := self.get_total_lines(source_code):
            return comment_count / total_lines

        return 0

    def get_docstring_rate(
        self, source_code: str, tree: ast.AST | None = None
    ) -> float:
        """
        docstringの割合を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        float
            docstring率
        """
        tree = tree or ast.parse(source_code)

        doc_count = 0
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.FunctionDef, ast.ClassDef, ast.Module)
            ) and ast.get_docstring(node):
                doc_count += 1

        if total_lines := self.get_total_lines(source_code):
            return doc_count / total_lines

        return 0

    def get_pep8_violation_rate(self, source_code: str) -> float:
        """
        PEP8違反率を取得.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        float
            PEP8違反率
        """
        lines = [line for line in source_code.splitlines() if line.strip()]
        if not lines:
            return 0

        checker = pycodestyle.Checker(lines=lines)
        checker.check_all()

        if total_lines := self.get_total_lines(source_code):
            return checker.report.total_errors / total_lines

        return 0
