import json
import requests
import pytest

# Тест для функции handle_factorial
@pytest.mark.parametrize("query_params, expected_status, expected_result", [
    ({'n': '4'}, 200, {"result": 24}),
    ({'n': '-4'}, 400, {"error": "Invalid value for n, must be non-negative number"}),
    ({'n': 'abc'}, 422, {"error": "Invalid value for n, must be non-negative number"})
])
def test_handle_factorial(query_params, expected_status, expected_result):
    url = "http://localhost:8000/factorial"
    response = requests.get(url, params=query_params)
    assert response.status_code == expected_status
    assert response.json() == expected_result

# Тест для функции handle_fibonacci
@pytest.mark.parametrize("n, expected_status, expected_result", [
    (3, 200, {"result": 2}),
    (0, 200, {"result": 1}),
    (-4, 400, {"error": "Invalid value for n, must be non-negative number"}),
    ('abc', 422, {"error": "Invalid value for n, must be non-negative number"})
])
def test_handle_fibonacci(n, expected_status, expected_result):
    url = f"http://localhost:8000/fibonacci/{n}"
    response = requests.get(url)
    assert response.status_code == expected_status
    assert response.json() == expected_result

# Тест для функции handle_mean
@pytest.mark.parametrize("data, expected_status, expected_result", [
([1, 2, 3], 200, {"result": 2.0}),
([], 400, {"error": "JSON body must not be empty"}),
(None, 422, {"error": "JSON body is missing or invalid"})
])
def test_handle_mean(data, expected_status, expected_result):
    url = "http://localhost:8000/mean"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, data=json.dumps(data), headers=headers)
    assert response.status_code == expected_status
    assert response.json() == expected_result

