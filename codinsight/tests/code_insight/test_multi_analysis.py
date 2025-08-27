from pathlib import Path

from code_insight.core import CodeAnalysisType
from code_insight.multi_analysis import MultiFileAnalyzer, analyze_paths


def write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def simple_py(i: int = 0) -> str:
    return f"def foo():\n    '''doc'''\n    # comment\n    return {i}\n"


def test_directory_recursive_and_filter_and_exclude(tmp_path: Path) -> None:
    # Arrange
    src = tmp_path / "proj" / "src"
    write(src / "a.py", simple_py(1))
    write(src / "sub" / "b.py", simple_py(2))
    write(tmp_path / "proj" / "node_modules" / "skip.py", simple_py(3))
    write(src / "c.txt", "not python")

    analyzer = MultiFileAnalyzer(exts={".py"}, excludes={"node_modules", ".git"})

    # Act
    result = analyzer.analyze([str(tmp_path / "proj")], [CodeAnalysisType.STYLE])

    # Assert
    assert result.aggregate.analyzed_files == 2
    assert result.aggregate.total_files == 2
    assert len(result.files) == 2
    for fa in result.files:
        assert CodeAnalysisType.STYLE in fa.results
        style = fa.results[CodeAnalysisType.STYLE]
        assert "naming_convention" in style.model_fields_set


def test_mixed_inputs_multi_dirs_and_files(tmp_path: Path) -> None:
    # Arrange
    dir1 = tmp_path / "d1"
    dir2 = tmp_path / "d2"
    f_standalone = tmp_path / "x.py"
    write(dir1 / "a.py", simple_py(10))
    write(dir1 / "b.py", simple_py(11))
    write(dir2 / "c.py", simple_py(12))
    write(f_standalone, simple_py(13))

    # Act
    result = analyze_paths(
        [str(dir1), str(dir2), str(f_standalone)],
        [CodeAnalysisType.STYLE, CodeAnalysisType.STRUCT],
        exts={".py"},
        excludes={"node_modules", ".git"},
    )

    # Assert
    assert result.aggregate.analyzed_files == 4
    assert result.aggregate.total_files == 4
    assert len(result.files) == 4
    for fa in result.files:
        assert CodeAnalysisType.STYLE in fa.results
        assert CodeAnalysisType.STRUCT in fa.results


def test_json_serialization(tmp_path: Path) -> None:
    # Arrange
    write(tmp_path / "t.py", simple_py(0))
    analyzer = MultiFileAnalyzer()

    # Act
    result = analyzer.analyze([str(tmp_path)], [CodeAnalysisType.STYLE])
    d = result.model_dump()
    s = result.model_dump_json()

    # Assert
    assert isinstance(d, dict)
    assert '"files"' in s
    assert '"aggregate"' in s
    assert "by_type_avg" in d["aggregate"]
