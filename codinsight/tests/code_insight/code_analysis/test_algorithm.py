from code_insight.code_analysis.algorithm import Algorithm, AlgorithmAnalysisResult


def test_algorithm_normal() -> None:
    # Arrange
    source_code = (
        "def factorial(n):\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    else:\n"
        "        return n * factorial(n - 1)\n"
        "\n"
        "def process_data(data):\n"
        "    result = [x * 2 for x in data if x > 0]\n"
        "    filtered = list(filter(lambda x: x % 2 == 0, result))\n"
        "    for item in filtered:\n"
        "        try:\n"
        "            while item > 10:\n"
        "                item //= 2\n"
        "        except ValueError:\n"
        "            pass\n"
        "    return filtered\n"
    )

    # Act
    result: AlgorithmAnalysisResult = Algorithm().analyze(source_code=source_code)

    # Assert
    assert result.if_count == 1
    assert result.for_count == 1
    assert result.while_count == 1
    assert result.try_count == 1
    assert result.recursion_rate == 0.5
    assert result.lambda_count == 1
    assert result.comprehension_count == 1
    assert result.functional_call_count == 1
    assert result.max_nesting_depth == 3


def test_algorithm_empty() -> None:
    # Arrange
    source_code = ""

    # Act
    result: AlgorithmAnalysisResult = Algorithm().analyze(source_code=source_code)

    # Assert
    assert result.if_count == 0
    assert result.for_count == 0
    assert result.while_count == 0
    assert result.try_count == 0
    assert result.recursion_rate == 0.0
    assert result.lambda_count == 0
    assert result.comprehension_count == 0
    assert result.functional_call_count == 0
    assert result.max_nesting_depth == 0


def test_algorithm_complex_recursion() -> None:
    # Arrange
    source_code = (
        "def fibonacci(n):\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return fibonacci(n-1) + fibonacci(n-2)\n"
        "\n"
        "def quicksort(arr):\n"
        "    if len(arr) <= 1:\n"
        "        return arr\n"
        "    pivot = arr[len(arr) // 2]\n"
        "    left = [x for x in arr if x < pivot]\n"
        "    middle = [x for x in arr if x == pivot]\n"
        "    right = [x for x in arr if x > pivot]\n"
        "    return quicksort(left) + middle + quicksort(right)\n"
        "\n"
        "def non_recursive():\n"
        "    return 42\n"
    )

    # Act
    result: AlgorithmAnalysisResult = Algorithm().analyze(source_code=source_code)

    # Assert
    assert result.recursion_rate == 2 / 3
    assert result.comprehension_count == 3
    assert result.if_count == 2


def test_algorithm_functional_programming() -> None:
    # Arrange
    source_code = (
        "from functools import reduce\n"
        "\n"
        "def process_numbers(numbers):\n"
        "    squared = list(map(lambda x: x ** 2, numbers))\n"
        "    evens = list(filter(lambda x: x % 2 == 0, squared))\n"
        "    total = reduce(lambda x, y: x + y, evens, 0)\n"
        "    \n"
        "    result = {\n"
        "        'squares': [x ** 2 for x in numbers],\n"
        "        'evens': {x for x in numbers if x % 2 == 0},\n"
        "        'mapping': {i: x for i, x in enumerate(numbers)}\n"
        "    }\n"
        "    \n"
        "    return total, result\n"
    )

    # Act
    result: AlgorithmAnalysisResult = Algorithm().analyze(source_code=source_code)

    # Assert
    assert result.lambda_count == 3
    assert result.functional_call_count == 3
    assert result.comprehension_count == 3


def test_algorithm_control_structures() -> None:
    # Arrange
    source_code = (
        "def complex_function(data):\n"
        "    for item in data:\n"
        "        if item > 0:\n"
        "            try:\n"
        "                while item > 100:\n"
        "                    item //= 2\n"
        "                    if item < 10:\n"
        "                        break\n"
        "            except ZeroDivisionError:\n"
        "                continue\n"
        "            except ValueError:\n"
        "                pass\n"
        "        elif item < 0:\n"
        "            for i in range(abs(item)):\n"
        "                if i % 2 == 0:\n"
        "                    try:\n"
        "                        result = 1 / i\n"
        "                    except ZeroDivisionError:\n"
        "                        result = 0\n"
        "    return data\n"
    )

    # Act
    result: AlgorithmAnalysisResult = Algorithm().analyze(source_code=source_code)

    # Assert
    assert result.if_count == 4
    assert result.for_count == 2
    assert result.while_count == 1
    assert result.try_count == 2
    assert result.max_nesting_depth == 6
