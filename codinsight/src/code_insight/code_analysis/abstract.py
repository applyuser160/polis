from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel


class BaseAnalysisResult(BaseModel):
    """解析結果のベースモデル"""


T = TypeVar("T", bound=BaseAnalysisResult)


class AbstractAnalysis(ABC, Generic[T]):
    """解析抽象クラス"""

    @abstractmethod
    def analyze(self, source_code: str) -> T:
        """コードを解析する"""
        raise NotImplementedError("analyze method must be implemented")
