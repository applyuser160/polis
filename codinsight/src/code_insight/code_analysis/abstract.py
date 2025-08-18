"""解析の抽象基底クラスモジュール."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel


class BaseAnalysisConfig(BaseModel):
    """
    解析設定のベースクラス.

    Attributes
    ----------
    enabled : bool
        解析の有効/無効フラグ, by default True
    """

    enabled: bool = True


class BaseAnalysisResult(BaseModel):
    """
    解析結果のベースモデル.

    Notes
    -----
    全ての解析結果クラスの基底クラス
    """


R = TypeVar("R", bound=BaseAnalysisResult)
C = TypeVar("C", bound=BaseAnalysisConfig)


class AbstractAnalysis(ABC, Generic[R, C]):
    """
    解析抽象クラス.

    Parameters
    ----------
    R : TypeVar
        解析結果の型
    C : TypeVar
        解析設定の型

    Attributes
    ----------
    config : C
        解析設定
    """

    config: C

    def __init__(self, config: C | None = None) -> None:
        """
        コンストラクタ.

        Parameters
        ----------
        config : C | None, optional
            解析設定, by default None
        """
        self.config = config or self.get_default_config()

    @abstractmethod
    def get_default_config(self) -> C:
        """
        デフォルト設定を取得.

        Returns
        -------
        C
            デフォルト設定
        """
        raise NotImplementedError("get_default_config method must be implemented")

    @abstractmethod
    def analyze(self, source_code: str) -> R:
        """
        コードを解析する.

        Parameters
        ----------
        source_code : str
            解析対象のソースコード

        Returns
        -------
        R
            解析結果
        """
        raise NotImplementedError("analyze method must be implemented")
