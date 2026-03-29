from flask import Blueprint, request, jsonify
import pandas as pd
from services.market_data import get_history
from services.indicators import compute_rsi, compute_macd, compute_moving_averages
from utils.formatting import format_iso_datetime, error_response

indicators_bp = Blueprint('indicators', __name__)


@indicators_bp.route('/get_rsi', methods=['GET'])
def get_rsi():
    try:
        ticker = request.args.get('ticker', default='AAPL')
        period = request.args.get('period', default='1mo')
        interval = request.args.get('interval', default='1d')
        rsi_period = int(request.args.get('rsi_period', default='14'))

        data = get_history(ticker, period, interval)
        data['RSI'] = compute_rsi(data['Close'], rsi_period)

        data = data.reset_index()
        data['Date'] = data['Date'].apply(format_iso_datetime)

        result = []
        for _, row in data.iterrows():
            if not pd.isna(row['RSI']):
                result.append({
                    "date": row['Date'],
                    "rsi": float(row['RSI']),
                    "close": float(row['Close'])
                })

        return jsonify({"rsiData": result, "rsiPeriod": rsi_period})

    except ValueError as ve:
        return error_response(str(ve), 404)
    except Exception as e:
        return error_response(str(e), 500)


@indicators_bp.route('/get_macd', methods=['GET'])
def get_macd():
    try:
        ticker = request.args.get('ticker', default='AAPL')
        period = request.args.get('period', default='3mo')
        interval = request.args.get('interval', default='1d')
        fast = int(request.args.get('fast', default='12'))
        slow = int(request.args.get('slow', default='26'))
        signal = int(request.args.get('signal', default='9'))

        data = get_history(ticker, period, interval)
        macd_data = compute_macd(data['Close'], fast, slow, signal)
        if macd_data is None:
            return error_response("Unable to calculate MACD. Try using a longer period (3mo or more).", 400)

        data = pd.concat([data, macd_data], axis=1)

        data = data.reset_index()
        data['Date'] = data['Date'].apply(format_iso_datetime)

        macd_col = f'MACD_{fast}_{slow}_{signal}'
        macd_signal_col = f'MACDs_{fast}_{slow}_{signal}'
        macd_hist_col = f'MACDh_{fast}_{slow}_{signal}'

        chart_data = {
            "dates": [],
            "macd": [],
            "macd_signal": [],
            "macd_histogram": [],
            "close": []
        }

        for _, row in data.iterrows():
            if not pd.isna(row.get(macd_col)):
                chart_data["dates"].append(row['Date'])
                chart_data["macd"].append(float(row[macd_col]))
                chart_data["close"].append(float(row['Close']))

                if not pd.isna(row.get(macd_signal_col)):
                    chart_data["macd_signal"].append({
                        "date": row['Date'],
                        "value": float(row[macd_signal_col])
                    })

                if not pd.isna(row.get(macd_hist_col)):
                    chart_data["macd_histogram"].append({
                        "date": row['Date'],
                        "value": float(row[macd_hist_col])
                    })

        return jsonify(chart_data)

    except ValueError as ve:
        return error_response(str(ve), 404)
    except Exception as e:
        return error_response(str(e), 500)


@indicators_bp.route('/get_moving_averages', methods=['GET'])
def get_moving_averages():
    try:
        ticker = request.args.get('ticker', default='AAPL')
        period = request.args.get('period', default='1mo')
        interval = request.args.get('interval', default='1d')
        sma_periods = request.args.get('sma_periods', default='20,50').split(',')
        ema_periods = request.args.get('ema_periods', default='12,26').split(',')

        sma_periods = [int(p.strip()) for p in sma_periods]
        ema_periods = [int(p.strip()) for p in ema_periods]

        data = get_history(ticker, period, interval)

        ma_series_map = compute_moving_averages(data['Close'], sma_periods, ema_periods)
        for name, series in ma_series_map.items():
            data[name] = series

        data = data.reset_index()
        data['Date'] = data['Date'].apply(format_iso_datetime)

        result = []
        for _, row in data.iterrows():
            ma_data = {
                "date": row['Date'],
                "close": float(row['Close'])
            }
            for p in sma_periods:
                key = f'SMA_{p}'
                if not pd.isna(row.get(key)):
                    ma_data[f'sma_{p}'] = float(row[key])
            for p in ema_periods:
                key = f'EMA_{p}'
                if not pd.isna(row.get(key)):
                    ma_data[f'ema_{p}'] = float(row[key])
            result.append(ma_data)

        return jsonify({
            "movingAveragesData": result,
            "smaPeriods": sma_periods,
            "emaPeriods": ema_periods
        })

    except ValueError as ve:
        return error_response(str(ve), 404)
    except Exception as e:
        return error_response(str(e), 500)
