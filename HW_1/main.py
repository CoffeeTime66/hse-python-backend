import json
import math
from urllib.parse import parse_qs
import uvicorn


def handle_factorial(query_params):
    n_str = query_params.get('n', [''])[0]
    try:
        n = int(n_str)
        if n < 0:
            return 400, {"error": "Invalid value for n, must be non-negative number"}
        result = math.factorial(n)
        return 200, {"result": result}
    except (ValueError, TypeError):
        return 422, {"error": "Invalid value for n, must be non-negative number"}


def handle_fibonacci(path_parts):
    n_str = path_parts[-1]
    try:
        n = int(n_str)
        if n < 0:
            return 400, {"error": "Invalid value for n, must be non-negative number"}
        elif n <= 1:
            return 200, {"result": 1}
        else:
            phi = (1 + math.sqrt(5)) / 2
            return 200, {"result": round(math.pow(phi, n) / math.sqrt(5))}
    except (ValueError, TypeError):
        return 422, {"error": "Invalid value for n, must be non-negative number"}


def handle_mean(json):
    try:
        if json is None:
            return 422, {"error": "JSON body is missing or invalid"}
        if not isinstance(json, list):
            return 400, {"error": "JSON body must be a list"}
        if not json:
            return 400, {"error": "JSON body must not be empty"}

        values = json

        if any(not isinstance(v, (int, float)) for v in values):
            return 400, {"error": "All values in JSON body must be numbers"}

        mean_result = sum(values) / len(values)

        return 200, {"result": mean_result}
    except (ValueError, TypeError):
        return 422, {"error": "Invalid value for n, must be non-negative number"}

async def app(scope, receive, send):
    assert scope['type'] == 'http'
    message = await receive()

    if message['type'] == 'http.disconnect':
        return

    path = scope['path']

    if path.startswith('/factorial') and scope['method'] == 'GET':
        query_params = parse_qs(scope['query_string'].decode('utf-8'))
        status_code, result = handle_factorial(query_params)
    elif path.startswith('/fibonacci/') and scope['method'] == 'GET':
        path_parts = path.split('/')
        status_code, result = handle_fibonacci(path_parts)
    elif path.startswith('/mean') and scope['method'] == 'GET':
        body = message.get('body', b'')
        json_body = json.loads(body.decode('utf-8')) if body else None
        status_code, result = handle_mean(json_body)
    else:
        status_code, result = 404, {"error": "Not Found"}

    response = {
        "type": "http.response.start",
        "status": status_code,
        "headers": [
            (b"content-type", b"application/json"),
        ],
    }
    await send(response)

    await send({
        "type": "http.response.body",
        "body": json.dumps(result).encode('utf-8'),
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

