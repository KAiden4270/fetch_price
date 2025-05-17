from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

def fetch_prices(ticker, asset_type):
    try:
        stock = yf.Ticker(ticker)

        price = stock.history(period="1d")['Close'].iloc[0]
        return price
    except Exception as e:
        return str(e)

@app.route('/get_stock_price', methods=['GET'])
def get_stock_price():
    ticker_symbol = request.args.get('ticker')
    asset_type = request.args.get('type')

    if not ticker_symbol or not asset_type:
        return jsonify({'error': 'Both ticker and type parameters are required'}), 400

    price = fetch_prices(ticker_symbol, asset_type)

    if isinstance(price, str):
        return jsonify({'error': price}), 500
    else:
        return jsonify({'price': price})


@app.route('/get_historical_data', methods=['GET'])
def get_historical_data():
    try:
        ticker = request.args.get('ticker', default='AAPL')
        period = request.args.get('period', default='1mo') 
        interval = request.args.get('interval', default='1d') 

        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)

        data = data.reset_index()
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

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

        print(result)
        return jsonify({"historicalData": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_chart_data', methods=['GET'])
def get_chart_data():
    try:
        ticker = request.args.get('ticker', default='AAPL')
        period = request.args.get('period', default='1mo')
        interval = request.args.get('interval', default='1d')
        chart_type = request.args.get('chart_type', default='line').lower()

        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)

        if data.empty:
            return jsonify({"error": "No data found for the given parameters."}), 404

        data = data.reset_index()
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

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
            return jsonify({"error": "Invalid chart_type. Must be 'line' or 'candle'."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run()
