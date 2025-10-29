from flask import jsonify


def format_iso_datetime(dt) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def error_response(message: str, status_code: int):
    return jsonify({"error": message}), status_code
