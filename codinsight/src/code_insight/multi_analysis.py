import os
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

from code_insight.code_analysis.abstract import BaseAnalysisResult
from code_insight.core import AnalysisConfigs, CodeAnalysis, CodeAnalysisType

DEFAULT_EXTS: set[str] = {".py"}
DEFAULT_EXCLUDES: set[str] = {"node_modules", "target", ".git", ".venv", "__pycache__"}


class FileAnalysisResult(BaseModel):
    """
    単一ファイルの解析結果モデル

    Attributes
    ----------
    path : str
        解析対象ファイルのパス
    results : dict[str, dict[str, Any]]
        解析結果の辞書
    """

    path: str
    results: dict[CodeAnalysisType, BaseAnalysisResult]


class AggregateStats(BaseModel):
    """
    解析全体の集約統計モデル

    Attributes
    ----------
    total_files : int
        総ファイル数
    analyzed_files : int
        解析済みファイル数
    errors : list[str]
        エラーが発生したファイルのリスト
    by_type_avg : dict[str, dict[str, float]]
        解析タイプ別の平均値
    """

    total_files: int
    analyzed_files: int
    errors: list[str]
    by_type_avg: dict[CodeAnalysisType, dict[str, float]]


class MultiAnalysisResult(BaseModel):
    """
    複数ファイル解析の結果モデル

    Attributes
    ----------
    files : list[FileAnalysisResult]
        ファイル別解析結果のリスト
    aggregate : AggregateStats
        集約統計
    """

    files: list[FileAnalysisResult]
    aggregate: AggregateStats

    def to_json(self) -> str:
        """
        JSON文字列へのシリアライズ

        Returns
        -------
        str
            JSON文字列
        """
        return self.model_dump_json()


def _is_excluded(path: Path, excludes: set[str]) -> bool:
    """
    パスが除外対象かどうかを判定

    Parameters
    ----------
    path : Path
        判定対象のパス
    excludes : set[str]
        除外パターンのセット

    Returns
    -------
    bool
        除外対象の場合True
    """
    parts = set(path.parts)
    return any(ex in parts for ex in excludes)


def collect_paths(
    inputs: Iterable[str],
    exts: set[str] | None = None,
    excludes: set[str] | None = None,
) -> list[Path]:
    """
    入力から解析対象ファイルパスを再帰収集

    Parameters
    ----------
    inputs : Iterable[str]
        入力パスのリスト
    exts : set[str] | None, optional
        対象拡張子のセット, by default None
    excludes : set[str] | None, optional
        除外パターンのセット, by default None

    Returns
    -------
    list[Path]
        収集されたファイルパスのリスト
    """
    exts = exts or DEFAULT_EXTS
    excludes = excludes or DEFAULT_EXCLUDES

    collected: list[Path] = []
    for p in inputs:
        path = Path(p)
        if not path.exists():
            continue

        if path.is_file():
            if not _is_excluded(path.parent, excludes) and path.suffix in exts:
                collected.append(path)
            continue

        for root, dirs, files in os.walk(path):
            root_path = Path(root)
            if _is_excluded(root_path, excludes):
                dirs[:] = [d for d in dirs if d not in excludes]
                continue
            dirs[:] = [d for d in dirs if d not in excludes]
            for fname in files:
                fpath = root_path / fname
                if fpath.suffix in exts and not _is_excluded(fpath.parent, excludes):
                    collected.append(fpath)

    return collected


def analyze_file(
    path: Path, types: list[CodeAnalysisType], configs: AnalysisConfigs | None = None
) -> FileAnalysisResult:
    """
    単一ファイルを解析して結果を返却

    Parameters
    ----------
    path : Path
        解析対象ファイルのパス
    types : list[CodeAnalysisType]
        実行する解析タイプのリスト
    configs : AnalysisConfigs | None, optional
        解析設定, by default None

    Returns
    -------
    FileAnalysisResult
        ファイル解析結果
    """
    source_code = path.read_text(encoding="utf-8", errors="ignore")
    analysis = CodeAnalysis(source_code=source_code, configs=configs)
    result_map = analysis.analyze(types)
    as_dict: dict[CodeAnalysisType, BaseAnalysisResult] = {}
    for t, model in result_map.items():
        as_dict[t] = model
    return FileAnalysisResult(path=str(path), results=as_dict)


def _aggregate_numeric_means(
    files: list[FileAnalysisResult],
) -> dict[CodeAnalysisType, dict[str, float]]:
    """
    数値メトリクスの平均値を集約

    Parameters
    ----------
    files : list[FileAnalysisResult]
        ファイル解析結果のリスト

    Returns
    -------
    dict[str, dict[str, float]]
        解析タイプ別の平均値辞書
    """
    by_type: dict[CodeAnalysisType, dict[str, list[float]]] = {}

    for fa in files:
        for tname, metrics in fa.results.items():
            if tname not in by_type:
                by_type[tname] = {}
            for key, val in metrics.model_dump().items():
                if isinstance(val, (int, float)):
                    by_type[tname].setdefault(key, []).append(float(val))

    avg: dict[CodeAnalysisType, dict[str, float]] = {}
    for tname, metrics_map in by_type.items():
        avg[tname] = {}
        for key, values in metrics_map.items():
            if values:
                avg[tname][key] = sum(values) / len(values)
    return avg


class MultiFileAnalyzer:
    """
    複数ファイル解析の管理クラス

    Attributes
    ----------
    exts : set[str]
        対象拡張子のセット
    excludes : set[str]
        除外パターンのセット
    configs : AnalysisConfigs | None
        解析設定
    """

    exts: set[str]
    excludes: set[str]
    configs: AnalysisConfigs | None

    def __init__(
        self,
        exts: set[str] | None = None,
        excludes: set[str] | None = None,
        configs: AnalysisConfigs | None = None,
    ) -> None:
        """
        コンストラクタ

        Parameters
        ----------
        exts : set[str] | None, optional
            対象拡張子のセット, by default None
        excludes : set[str] | None, optional
            除外パターンのセット, by default None
        configs : AnalysisConfigs | None, optional
            解析設定, by default None
        """
        self.exts = exts or DEFAULT_EXTS
        self.excludes = excludes or DEFAULT_EXCLUDES
        self.configs = configs

    def analyze(
        self,
        inputs: list[str],
        types: list[CodeAnalysisType],
    ) -> MultiAnalysisResult:
        """
        入力パス群を解析して結果を返却

        Parameters
        ----------
        inputs : list[str]
            入力パスのリスト
        types : list[CodeAnalysisType]
            実行する解析タイプのリスト

        Returns
        -------
        MultiAnalysisResult
            複数ファイル解析結果
        """
        paths = collect_paths(inputs=inputs, exts=self.exts, excludes=self.excludes)
        files: list[FileAnalysisResult] = []
        errors: list[str] = []

        for p in paths:
            try:
                files.append(analyze_file(p, types, self.configs))
            except Exception:
                errors.append(str(p))

        aggregate = AggregateStats(
            total_files=len(paths),
            analyzed_files=len(files),
            errors=errors,
            by_type_avg=_aggregate_numeric_means(files),
        )
        return MultiAnalysisResult(files=files, aggregate=aggregate)


def analyze_paths(
    inputs: list[str],
    types: list[CodeAnalysisType],
    exts: set[str] | None = None,
    excludes: set[str] | None = None,
    configs: AnalysisConfigs | None = None,
) -> MultiAnalysisResult:
    """
    関数APIによる複数ファイル解析の実行

    Parameters
    ----------
    inputs : list[str]
        入力パスのリスト
    types : list[CodeAnalysisType]
        実行する解析タイプのリスト
    exts : set[str] | None, optional
        対象拡張子のセット, by default None
    excludes : set[str] | None, optional
        除外パターンのセット, by default None
    configs : AnalysisConfigs | None, optional
        解析設定, by default None

    Returns
    -------
    MultiAnalysisResult
        複数ファイル解析結果
    """
    analyzer = MultiFileAnalyzer(exts=exts, excludes=excludes, configs=configs)
    return analyzer.analyze(inputs=inputs, types=types)
