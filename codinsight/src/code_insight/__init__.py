from .code_analysis.struct import Struct, StructAnalysisResult
from .code_analysis.style import Style, StyleAnalysisResult
from .code_analysis.complexity import Complexity, ComplexityAnalysisResult
from .core import CodeAnalysis
from .trend_analysis.trend_analysis import TrendAnalysis

__all__ = [
    "CodeAnalysis",
    "Style",
    "StyleAnalysisResult",
    "Struct",
    "StructAnalysisResult",
    "Complexity",
    "ComplexityAnalysisResult",
    "TrendAnalysis",
]
