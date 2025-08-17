from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


class BaseAnalysisConfig(BaseModel):
    """解析設定のベースクラス"""

    enabled: bool = True


class BaseAnalysisResult(BaseModel):
    """解析結果のベースモデル"""


T = TypeVar("T", bound=BaseAnalysisResult)
C = TypeVar("C", bound=BaseAnalysisConfig)


class AbstractAnalysis(ABC, Generic[T, C]):
    """解析抽象クラス"""

    def __init__(self, config: Optional[C] = None) -> None:
        """コンストラクタ"""
        self.config = config or self.get_default_config()

    @abstractmethod
    def get_default_config(self) -> C:
        """デフォルト設定を取得"""
        raise NotImplementedError("get_default_config method must be implemented")

    @abstractmethod
    def analyze(self, source_code: str) -> T:
        """コードを解析する"""
        raise NotImplementedError("analyze method must be implemented")
