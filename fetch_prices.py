from flask import Flask
from flask import render_template
from routes.prices import prices_bp
from routes.indicators import indicators_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(prices_bp)
    app.register_blueprint(indicators_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


app = create_app()


if __name__ == '__main__':
    app.run()
