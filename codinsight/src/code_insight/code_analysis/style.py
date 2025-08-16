import ast
import re

import pycodestyle

from code_insight.code_analysis.abstract import AbstractAnalysis, BaseAnalysisResult


class StyleAnalysisResult(BaseAnalysisResult):
    """
    解析結果(スタイル)
    * 命名規則
        * 変数名、関数名の一貫性
    * コメント
        * ソースコード中のコメント率
    * docstring
        * 関数、クラス、モジュールのうち、docstringが書かれている割合
    * PEP8違反
        * ソースコード中のPEP8に違反している割合
    """

    naming_convention: float
    comment_rate: float
    docstring_rate: float
    pep8_violation_rate: float


class Style(AbstractAnalysis[StyleAnalysisResult]):
    """解析クラス(スタイル)"""

    def analyze(self, source_code: str) -> StyleAnalysisResult:
        """コード解析"""
        return StyleAnalysisResult(
            naming_convention=self.get_naming_convention(source_code),
            comment_rate=self.get_comment_rate(source_code),
            docstring_rate=self.get_docstring_rate(source_code),
            pep8_violation_rate=self.get_pep8_violation_rate(source_code),
        )

    def get_naming_convention(self, source_code: str) -> float:
        """命名規則の一貫性を取得"""
        tree = ast.parse(source_code)
        violations = 0
        for node in ast.walk(tree):
            # 関数名チェック
            if isinstance(node, ast.FunctionDef):
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                    violations += 1
            # クラス名チェック
            if isinstance(node, ast.ClassDef):
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    violations += 1

        return violations

    def get_total_lines(self, source_code: str) -> int:
        """行数を取得"""
        return len(source_code.splitlines())

    def get_comment_rate(self, source_code: str) -> float:
        """コメント率を取得"""
        comment_count = sum(
            1 for line in source_code.splitlines() if line.strip().startswith("#")
        )

        if total_lines := self.get_total_lines(source_code):
            return comment_count / total_lines

        return 0

    def get_docstring_rate(self, source_code: str) -> float:
        """docstringの割合を取得"""
        tree = ast.parse(source_code)

        doc_count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    doc_count += 1

        if total_lines := self.get_total_lines(source_code):
            return doc_count / total_lines

        return 0

    def get_pep8_violation_rate(self, source_code: str) -> float:
        """PEP8違反率を取得"""
        checker = pycodestyle.Checker(lines=source_code.splitlines())
        checker.check_all()

        if total_lines := self.get_total_lines(source_code):
            return checker.report.total_errors / total_lines

        return 0
