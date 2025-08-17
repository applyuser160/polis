from .code_analysis.struct import Struct, StructAnalysisResult
from .code_analysis.style import Style, StyleAnalysisResult
from .core import CodeAnalysis, CodeAnalysisType
from .trend_analysis.trend_analysis import TrendAnalysis

__all__ = [
    "CodeAnalysis",
    "CodeAnalysisType",
    "Style",
    "StyleAnalysisResult",
    "Struct",
    "StructAnalysisResult",
    "TrendAnalysis",
]
