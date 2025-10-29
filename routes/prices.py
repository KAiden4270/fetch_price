from flask import Blueprint, request, jsonify
import pandas as pd
from services.market_data import get_history, get_close_price
from utils.formatting import format_iso_datetime, error_response

prices_bp = Blueprint('prices', __name__)


@prices_bp.route('/get_stock_price', methods=['GET'])
def get_stock_price():
    ticker_symbol = request.args.get('ticker')
    asset_type = request.args.get('type')

    if not ticker_symbol or not asset_type:
        return error_response('Both ticker and type parameters are required', 400)

    try:
        price = get_close_price(ticker_symbol)
        return jsonify({'price': price})
    except Exception as e:
        return error_response(str(e), 500)


@prices_bp.route('/get_historical_data', methods=['GET'])
def get_historical_data():
    try:
        ticker = request.args.get('ticker', default='AAPL')
        period = request.args.get('period', default='1mo')
        interval = request.args.get('interval', default='1d')

        data = get_history(ticker, period, interval)
        data = data.reset_index()
        data['Date'] = data['Date'].apply(format_iso_datetime)

        result = []
        for _, row in data.iterrows():
            result.append({
                "date": row['Date'],
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']),
                "dividends": float(row.get('Dividends', 0.0)),
                "stock_splits": float(row.get('Stock Splits', 0.0))
            })

        return jsonify({"historicalData": result})

    except ValueError as ve:
        return error_response(str(ve), 404)
    except Exception as e:
        return error_response(str(e), 500)


@prices_bp.route('/get_chart_data', methods=['GET'])
def get_chart_data():
    try:
        ticker = request.args.get('ticker', default='AAPL')
        period = request.args.get('period', default='1mo')
        interval = request.args.get('interval', default='1d')
        chart_type = request.args.get('chart_type', default='line').lower()

        data = get_history(ticker, period, interval)
        data = data.reset_index()
        data['Date'] = data['Date'].apply(format_iso_datetime)

        result = []

        if chart_type == 'line':
            for _, row in data.iterrows():
                result.append({
                    "date": row['Date'],
                    "value": float(row['Close'])
                })
            return jsonify({"chartData": result, "chartType": "line"})

        elif chart_type == 'candle':
            for _, row in data.iterrows():
                result.append({
                    "date": row['Date'],
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })
            return jsonify({"chartData": result, "chartType": "candle"})

        else:
            return error_response("Invalid chart_type. Must be 'line' or 'candle'.", 400)

    except ValueError as ve:
        return error_response(str(ve), 404)
    except Exception as e:
        return error_response(str(e), 500)
