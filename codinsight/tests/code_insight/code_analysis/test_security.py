from code_insight.code_analysis.security import Security, SecurityAnalysisResult


def test_security_empty() -> None:
    # Arrange
    source_code = ""

    # Act
    result: SecurityAnalysisResult = Security().analyze(source_code=source_code)

    # Assert
    assert result.hardcoded_secrets_count == 0
    assert result.dangerous_function_count == 0
    assert result.sql_injection_risk_count == 0
    assert result.input_validation_missing_count == 0
    assert result.security_score == 1.0


def test_security_normal() -> None:
    # Arrange
    source_code = (
        'password = "secret123"\n'
        'api_key = "sk-1234567890abcdef"\n'
        'def dangerous_func():\n'
        '    eval("print(1)")\n'
        '    exec("x = 1")\n'
        '    return "ok"\n'
        'def sql_query():\n'
        '    query = "SELECT * FROM users WHERE id = " + user_id\n'
        '    return query\n'
        'def get_input():\n'
        '    user_data = input("Enter data: ")\n'
        '    return user_data\n'
    )

    # Act
    result: SecurityAnalysisResult = Security().analyze(source_code=source_code)

    # Assert
    assert result.hardcoded_secrets_count == 3
    assert result.dangerous_function_count == 2
    assert result.sql_injection_risk_count == 0
    assert result.input_validation_missing_count == 1
    assert result.security_score < 1.0


def test_security_disabled() -> None:
    # Arrange
    source_code = (
        'password = "secret123"\n'
        'eval("print(1)")\n'
    )
    config = Security().get_default_config()
    config.enabled = False

    # Act
    result: SecurityAnalysisResult = Security(config).analyze(source_code=source_code)

    # Assert
    assert result.hardcoded_secrets_count == 0
    assert result.dangerous_function_count == 0
    assert result.sql_injection_risk_count == 0
    assert result.input_validation_missing_count == 0
    assert result.security_score == 1.0


def test_security_safe_code() -> None:
    # Arrange
    source_code = (
        'import os\n'
        'def safe_function(data: str) -> str:\n'
        '    """安全な関数"""\n'
        '    if not data:\n'
        '        raise ValueError("Invalid input")\n'
        '    return data.upper()\n'
        'def get_config():\n'
        '    return os.getenv("CONFIG_PATH", "/default/path")\n'
    )

    # Act
    result: SecurityAnalysisResult = Security().analyze(source_code=source_code)

    # Assert
    assert result.hardcoded_secrets_count == 0
    assert result.dangerous_function_count == 0
    assert result.sql_injection_risk_count == 0
    assert result.input_validation_missing_count == 0
    assert result.security_score == 1.0
