from .code_analysis.readability import Readability, ReadabilityAnalysisResult
from .code_analysis.struct import Struct, StructAnalysisResult
from .code_analysis.style import Style, StyleAnalysisResult
from .core import CodeAnalysis
from .trend_analysis.trend_analysis import TrendAnalysis

__all__ = [
    "CodeAnalysis",
    "Readability",
    "ReadabilityAnalysisResult",
    "Style",
    "StyleAnalysisResult",
    "Struct",
    "StructAnalysisResult",
    "TrendAnalysis",
]
