Codinsight - 複数ファイル解析の利用方法

概要
- 複数のファイルやディレクトリを再帰的に走査し、既存の解析エンジン（Style/Struct/Readability/Redundancy/Algorithm/Complexity/Quality）で一括解析を実行
- 拡張子のフィルタや除外パターン（node_modules, .git など）に対応
- 結果をファイル単位と集約統計（平均など）で取得可能
- Pydantic BaseModel で JSON 化が容易

API 使用例
from code_insight.core import CodeAnalysisType
from code_insight.multi_analysis import MultiFileAnalyzer

analyzer = MultiFileAnalyzer(
    exts={".py"},
    excludes={"node_modules", "target", ".git", ".venv", "__pycache__"},
)
result = analyzer.analyze(
    ["src", "tests"],
    [CodeAnalysisType.STYLE, CodeAnalysisType.STRUCT],
)
print(result.model_dump_json())

主なオプション
- exts: 対象拡張子のセット（デフォルト: {".py"}）
- excludes: 除外ディレクトリ名のセット（デフォルト: {"node_modules", "target", ".git", ".venv", "__pycache__"}）

返却データの構造
- files: 各ファイルの解析結果（解析タイプ名 → メトリクス辞書）
- aggregate:
  - total_files: 解析対象に収集されたファイル数
  - analyzed_files: 実際に解析に成功したファイル数
  - errors: 解析時にエラーとなったファイルパスの一覧
  - by_type_avg: 解析タイプごとの各数値メトリクスの平均値

注意
- 現時点では直列処理のみ対応。大規模データや並列化は将来的な拡張予定
