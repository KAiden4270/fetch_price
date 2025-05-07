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

if __name__ == '__main__':
    app.run()
