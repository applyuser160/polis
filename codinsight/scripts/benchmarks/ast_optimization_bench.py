#!/usr/bin/env python3
import argparse
import time
from pathlib import Path
from typing import Iterable

from code_insight.core import CodeAnalysisType


def iter_py_files(paths: list[str]) -> Iterable[Path]:
    for p in paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".py":
            yield path
        elif path.is_dir():
            for f in path.rglob("*.py"):
                if any(part in {".venv", ".git", "__pycache__"} for part in f.parts):
                    continue
                yield f


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def bench_once(
    target_files: list[Path], types: list[CodeAnalysisType]
) -> dict[str, float]:
    results: dict[str, float] = {}
    for t in types:
        analyzer = CodeAnalysisType.get_code_analysis_class(t)
        start = time.perf_counter()
        for fp in target_files:
            src = read_text(fp)
            try:
                analyzer.analyze(src)
            except Exception:
                pass
        elapsed = (time.perf_counter() - start) * 1000.0
        results[t.value] = elapsed
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="AST最適化ベンチマーク")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[
            "codinsight/src/code_insight",
            "codinsight/tests",
        ],
        help="ベンチマーク対象パス",
    )
    parser.add_argument("--repeat", type=int, default=3, help="繰り返し回数")
    args = parser.parse_args()

    files = list(iter_py_files(args.paths))
    types = list(CodeAnalysisType)

    totals = {t.value: 0.0 for t in types}
    for _ in range(args.repeat):
        res = bench_once(files, types)
        for k, v in res.items():
            totals[k] += v

    print("===== AST最適化ベンチマーク結果 =====")
    print(f"対象ファイル数: {len(files)}")
    print(f"繰り返し回数: {args.repeat}")
    overall = 0.0
    for name, total_ms in totals.items():
        avg_ms = total_ms / args.repeat
        overall += avg_ms
        print(f"- {name}: {avg_ms:.2f} ms")
    print(f"総合: {overall:.2f} ms")


if __name__ == "__main__":
    main()
