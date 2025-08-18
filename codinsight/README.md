Codinsight - 複数ファイル解析の利用方法

概要
- 複数のファイルやディレクトリを再帰的に走査し、既存の解析エンジン（Style/Struct/Readability/Redundancy/Algorithm/Complexity/Quality）で一括解析を実行
- 拡張子のフィルタや除外パターン（node_modules, .git など）に対応
- 結果をファイル単位と集約統計（平均など）で取得可能
- Pydantic BaseModel で JSON 化が容易

## API 使用例

```python
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
```

## 設定のカスタマイズ

```python
from code_insight.core import CodeAnalysis, AnalysisConfigs, CodeAnalysisType
from code_insight.code_analysis.quality import QualityAnalysisConfig
from code_insight.code_analysis.redundancy import RedundancyAnalysisConfig
from code_insight.code_analysis.style import StyleAnalysisConfig

# カスタム設定の作成
configs = AnalysisConfigs(
    quality=QualityAnalysisConfig(
        long_param_threshold=3,  # デフォルト: 5
        enabled=True
    ),
    redundancy=RedundancyAnalysisConfig(
        long_function_lines_threshold=30,  # デフォルト: 50
        long_function_complexity_threshold=8,  # デフォルト: 10
        ignored_function_names={"main", "__init__", "setup"}
    ),
    style=StyleAnalysisConfig(
        function_name_pattern=r"^[a-z_][a-z0-9_]*$",  # snake_case
        class_name_pattern=r"^[A-Z][a-zA-Z0-9]*$"     # PascalCase
    )
)

# 設定を使用した解析
analysis = CodeAnalysis(source_code, configs)
result = analysis.analyze([CodeAnalysisType.QUALITY, CodeAnalysisType.REDUNDANCY])

# 複数ファイル解析での設定使用
analyzer = MultiFileAnalyzer(configs=configs)
result = analyzer.analyze(["src"], [CodeAnalysisType.STYLE])
```

### 設定可能な項目

#### Quality解析
- `long_param_threshold`: 長引数関数の閾値（デフォルト: 5）
- `enabled`: 解析の有効/無効（デフォルト: True）

#### Redundancy解析
- `long_function_lines_threshold`: 長大関数の行数閾値（デフォルト: 50）
- `long_function_complexity_threshold`: 長大関数の複雑度閾値（デフォルト: 10）
- `ignored_function_names`: 未使用コード検出で無視する関数名（デフォルト: {"main", "__init__", "__main__"}）

#### Style解析
- `function_name_pattern`: 関数名の正規表現パターン（デフォルト: snake_case）
- `class_name_pattern`: クラス名の正規表現パターン（デフォルト: PascalCase）

#### その他の解析エンジン
- Algorithm, Complexity, Readability, Structの各解析エンジンにも同様の設定項目があります

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
