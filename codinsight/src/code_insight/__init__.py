"""コードインサイトパッケージ."""
from .code_analysis.algorithm import (
    Algorithm,
    AlgorithmAnalysisConfig,
    AlgorithmAnalysisResult,
)
from .code_analysis.complexity import (
    Complexity,
    ComplexityAnalysisConfig,
    ComplexityAnalysisResult,
)
from .code_analysis.quality import Quality, QualityAnalysisConfig, QualityAnalysisResult
from .code_analysis.readability import (
    Readability,
    ReadabilityAnalysisConfig,
    ReadabilityAnalysisResult,
)
from .code_analysis.redundancy import (
    Redundancy,
    RedundancyAnalysisConfig,
    RedundancyAnalysisResult,
)
from .code_analysis.struct import Struct, StructAnalysisConfig, StructAnalysisResult
from .code_analysis.style import Style, StyleAnalysisConfig, StyleAnalysisResult
from .core import AnalysisConfigs, CodeAnalysis, CodeAnalysisType
from .multi_analysis import FileAnalysisResult, MultiAnalysisResult, MultiFileAnalyzer
from .trend_analysis.trend_analysis import TrendAnalysis

__all__ = [
    "CodeAnalysis",
    "CodeAnalysisType",
    "AnalysisConfigs",
    "MultiFileAnalyzer",
    "MultiAnalysisResult",
    "FileAnalysisResult",
    "Readability",
    "ReadabilityAnalysisResult",
    "ReadabilityAnalysisConfig",
    "Algorithm",
    "AlgorithmAnalysisResult",
    "AlgorithmAnalysisConfig",
    "Complexity",
    "ComplexityAnalysisResult",
    "ComplexityAnalysisConfig",
    "Quality",
    "QualityAnalysisResult",
    "QualityAnalysisConfig",
    "Redundancy",
    "RedundancyAnalysisResult",
    "RedundancyAnalysisConfig",
    "Struct",
    "StructAnalysisResult",
    "StructAnalysisConfig",
    "Style",
    "StyleAnalysisResult",
    "StyleAnalysisConfig",
    "TrendAnalysis",
]
