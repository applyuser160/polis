from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel

from code_insight.core import CodeAnalysis, CodeAnalysisType


DEFAULT_EXTS: set[str] = {".py"}
DEFAULT_EXCLUDES: set[str] = {"node_modules", "target", ".git", ".venv", "__pycache__"}


class FileAnalysisResult(BaseModel):
    path: str
    results: dict[str, dict[str, Any]]


class AggregateStats(BaseModel):
    total_files: int
    analyzed_files: int
    errors: list[str]
    by_type_avg: dict[str, dict[str, float]]


class MultiAnalysisResult(BaseModel):
    files: list[FileAnalysisResult]
    aggregate: AggregateStats

    def to_json(self) -> str:
        return self.model_dump_json()


def _is_excluded(path: Path, excludes: set[str]) -> bool:
    parts = set(path.parts)
    return any(ex in parts for ex in excludes)


def collect_paths(
    inputs: Iterable[str],
    exts: set[str] | None = None,
    excludes: set[str] | None = None,
) -> list[Path]:
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


def analyze_file(path: Path, types: list[CodeAnalysisType]) -> FileAnalysisResult:
    source_code = path.read_text(encoding="utf-8", errors="ignore")
    analysis = CodeAnalysis(source_code=source_code)
    result_map = analysis.analyze(types)
    as_dict: dict[str, dict[str, Any]] = {}
    for t, model in result_map.items():
        as_dict[t.name] = model.model_dump()
    return FileAnalysisResult(path=str(path), results=as_dict)


def _aggregate_numeric_means(files: list[FileAnalysisResult]) -> dict[str, dict[str, float]]:
    by_type: dict[str, dict[str, list[float]]] = {}

    for fa in files:
        for tname, metrics in fa.results.items():
            if tname not in by_type:
                by_type[tname] = {}
            for key, val in metrics.items():
                if isinstance(val, (int, float)):
                    by_type[tname].setdefault(key, []).append(float(val))

    avg: dict[str, dict[str, float]] = {}
    for tname, metrics_map in by_type.items():
        avg[tname] = {}
        for key, values in metrics_map.items():
            if values:
                avg[tname][key] = sum(values) / len(values)
    return avg


class MultiFileAnalyzer:
    exts: set[str]
    excludes: set[str]

    def __init__(self, exts: set[str] | None = None, excludes: set[str] | None = None) -> None:
        self.exts = exts or DEFAULT_EXTS
        self.excludes = excludes or DEFAULT_EXCLUDES

    def analyze(
        self,
        inputs: list[str],
        types: list[CodeAnalysisType],
    ) -> MultiAnalysisResult:
        paths = collect_paths(inputs=inputs, exts=self.exts, excludes=self.excludes)
        files: list[FileAnalysisResult] = []
        errors: list[str] = []

        for p in paths:
            try:
                files.append(analyze_file(p, types))
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
) -> MultiAnalysisResult:
    analyzer = MultiFileAnalyzer(exts=exts, excludes=excludes)
    return analyzer.analyze(inputs=inputs, types=types)
