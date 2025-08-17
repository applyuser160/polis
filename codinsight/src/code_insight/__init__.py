from .code_analysis.redundancy import Redundancy, RedundancyAnalysisResult
from .code_analysis.struct import Struct, StructAnalysisResult
from .code_analysis.style import Style, StyleAnalysisResult
from .core import CodeAnalysis
from .trend_analysis.trend_analysis import TrendAnalysis

__all__ = [
    "CodeAnalysis",
    "Style",
    "StyleAnalysisResult",
    "Struct",
    "StructAnalysisResult",
    "Redundancy",
    "RedundancyAnalysisResult",
    "TrendAnalysis",
]
