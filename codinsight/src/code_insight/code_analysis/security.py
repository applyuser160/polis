import ast
import re
from typing import List, Set

from code_insight.code_analysis.abstract import (
    AbstractAnalysis,
    BaseAnalysisConfig,
    BaseAnalysisResult,
)


class SecurityAnalysisConfig(BaseAnalysisConfig):
    """
    セキュリティ解析設定

    Attributes
    ----------
    check_hardcoded_secrets : bool
        ハードコードされた秘密情報をチェックするか, by default True
    check_dangerous_functions : bool
        危険な関数の使用をチェックするか, by default True
    check_sql_injection : bool
        SQLインジェクション脆弱性をチェックするか, by default True
    secret_patterns : List[str]
        秘密情報検出パターン, by default 標準パターン
    """

    check_hardcoded_secrets: bool = True
    check_dangerous_functions: bool = True
    check_sql_injection: bool = True
    secret_patterns: List[str] = [
        r"password\s*=\s*['\"][^'\"]{3,}['\"]",
        r"api_key\s*=\s*['\"][^'\"]{10,}['\"]",
        r"secret\s*=\s*['\"][^'\"]{8,}['\"]",
        r"token\s*=\s*['\"][^'\"]{10,}['\"]",
        r"key\s*=\s*['\"][^'\"]{8,}['\"]",
    ]


class SecurityAnalysisResult(BaseAnalysisResult):
    """
    解析結果(セキュリティ)

    Attributes
    ----------
    hardcoded_secrets_count : int
        ハードコードされた秘密情報の数
    dangerous_function_count : int
        危険な関数の使用数
    sql_injection_risk_count : int
        SQLインジェクション脆弱性の可能性がある箇所の数
    input_validation_missing_count : int
        入力検証不備の数
    security_score : float
        セキュリティスコア（0.0-1.0、高いほど安全）
    """

    hardcoded_secrets_count: int
    dangerous_function_count: int
    sql_injection_risk_count: int
    input_validation_missing_count: int
    security_score: float


class Security(AbstractAnalysis[SecurityAnalysisResult, SecurityAnalysisConfig]):
    """
    解析クラス(セキュリティ)

    Notes
    -----
    コードのセキュリティ脆弱性を多角的に解析するクラス
    """

    def __init__(self, config: SecurityAnalysisConfig | None = None) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        config : SecurityAnalysisConfig | None, optional
            セキュリティ解析設定, by default None
        """
        super().__init__(config)

    def get_default_config(self) -> SecurityAnalysisConfig:
        """
        デフォルト設定を取得

        Returns
        -------
        SecurityAnalysisConfig
            デフォルトのセキュリティ解析設定
        """
        return SecurityAnalysisConfig()

    def analyze(self, source_code: str) -> SecurityAnalysisResult:
        """
        コード解析

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        SecurityAnalysisResult
            セキュリティ解析結果
        """
        if not self.config.enabled:
            return SecurityAnalysisResult(
                hardcoded_secrets_count=0,
                dangerous_function_count=0,
                sql_injection_risk_count=0,
                input_validation_missing_count=0,
                security_score=1.0,
            )

        tree = self.parse_source_code(source_code)

        hardcoded_secrets = self.get_hardcoded_secrets_count(source_code, tree)
        dangerous_functions = self.get_dangerous_function_count(source_code, tree)
        sql_injection_risks = self.get_sql_injection_risk_count(source_code, tree)
        input_validation_missing = self.get_input_validation_missing_count(source_code, tree)

        security_score = self.calculate_security_score(
            hardcoded_secrets, dangerous_functions, sql_injection_risks, input_validation_missing
        )

        return SecurityAnalysisResult(
            hardcoded_secrets_count=hardcoded_secrets,
            dangerous_function_count=dangerous_functions,
            sql_injection_risk_count=sql_injection_risks,
            input_validation_missing_count=input_validation_missing,
            security_score=security_score,
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
        return ast.parse(source_code)

    def get_hardcoded_secrets_count(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """
        ハードコードされた秘密情報の数を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        int
            ハードコードされた秘密情報の数
        """
        if not self.config.check_hardcoded_secrets:
            return 0

        count = 0
        source_lower = source_code.lower()

        for pattern in self.config.secret_patterns:
            matches = re.findall(pattern, source_lower, re.IGNORECASE)
            count += len(matches)

        return count

    def get_dangerous_function_count(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """
        危険な関数の使用数を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        int
            危険な関数の使用数
        """
        if not self.config.check_dangerous_functions:
            return 0

        tree = tree or self.parse_source_code(source_code)
        dangerous_functions = {"eval", "exec", "compile", "__import__"}
        count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in dangerous_functions:
                    count += 1

        return count

    def get_sql_injection_risk_count(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """
        SQLインジェクション脆弱性の可能性がある箇所の数を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        int
            SQLインジェクション脆弱性の可能性がある箇所の数
        """
        if not self.config.check_sql_injection:
            return 0

        tree = tree or self.parse_source_code(source_code)
        count = 0

        sql_patterns = [
            r"select\s+.*\s+from\s+.*\+",
            r"insert\s+into\s+.*\+",
            r"update\s+.*\s+set\s+.*\+",
            r"delete\s+from\s+.*\+",
        ]

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                    sql_text = node.left.value.lower()
                    for pattern in sql_patterns:
                        if re.search(pattern, sql_text):
                            count += 1
                            break

        return count

    def get_input_validation_missing_count(
        self, source_code: str, tree: ast.AST | None = None
    ) -> int:
        """
        入力検証不備の数を取得

        Parameters
        ----------
        source_code : str
            解析対象のソースコード
        tree : ast.AST | None, optional
            解析済みのAST, by default None

        Returns
        -------
        int
            入力検証不備の数
        """
        tree = tree or self.parse_source_code(source_code)
        count = 0
        input_functions = {"input", "raw_input"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in input_functions:
                    parent_found = False
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.If):
                            for child in ast.walk(parent):
                                if child is node:
                                    parent_found = True
                                    break
                    if not parent_found:
                        count += 1

        return count

    def calculate_security_score(
        self,
        hardcoded_secrets: int,
        dangerous_functions: int,
        sql_injection_risks: int,
        input_validation_missing: int,
    ) -> float:
        """
        セキュリティスコアを計算

        Parameters
        ----------
        hardcoded_secrets : int
            ハードコードされた秘密情報の数
        dangerous_functions : int
            危険な関数の使用数
        sql_injection_risks : int
            SQLインジェクション脆弱性の可能性がある箇所の数
        input_validation_missing : int
            入力検証不備の数

        Returns
        -------
        float
            セキュリティスコア（0.0-1.0、高いほど安全）
        """
        total_issues = hardcoded_secrets + dangerous_functions + sql_injection_risks + input_validation_missing

        if total_issues == 0:
            return 1.0

        penalty = min(total_issues * 0.1, 1.0)
        return max(1.0 - penalty, 0.0)
