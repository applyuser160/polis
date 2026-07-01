from unittest.mock import MagicMock, patch

import pytest

from codetovec import CodeToVec


from code_insight.code_analysis.vector import (
    Vector,
    VectorAnalysisConfig,
    VectorAnalysisResult,
)


@pytest.fixture
def sample_code():
    return """
def hello_world():
    # This is a comment
    '''This is a docstring'''
    print("Hello, World!")

    return True
"""


def test_vector_analysis_default_config(sample_code):
    # CodeToVecのモックを作成
    mock_codetovec = MagicMock(spec=CodeToVec)
    mock_codetovec.execute.return_value = [0.1, 0.2, 0.3]

    with patch(
        "code_insight.code_analysis.vector.CodeToVec", return_value=mock_codetovec
    ):
        vector_analysis = Vector()
        result = vector_analysis.analyze(sample_code)

        # アサーション
        assert isinstance(result, VectorAnalysisResult)
        assert result.vector == [0.1, 0.2, 0.3]

        # executeが正しい引数で呼ばれたか確認
        mock_codetovec.execute.assert_called_once_with(
            text=sample_code,
            remove_comments=False,
            remove_docstrings=False,
            remove_blank_lines=False,
        )


def test_vector_analysis_custom_config(sample_code):
    # カスタム設定
    config = VectorAnalysisConfig(
        remove_comments=True,
        remove_docstrings=True,
        remove_blank_lines=True,
    )

    # CodeToVecのモックを作成
    mock_codetovec = MagicMock(spec=CodeToVec)
    mock_codetovec.execute.return_value = [0.4, 0.5, 0.6]

    with patch(
        "code_insight.code_analysis.vector.CodeToVec", return_value=mock_codetovec
    ):
        vector_analysis = Vector(config)
        result = vector_analysis.analyze(sample_code)

        # アサーション
        assert isinstance(result, VectorAnalysisResult)
        assert result.vector == [0.4, 0.5, 0.6]

        # executeが正しい引数で呼ばれたか確認
        mock_codetovec.execute.assert_called_once_with(
            text=sample_code,
            remove_comments=True,
            remove_docstrings=True,
            remove_blank_lines=True,
        )
