from flask import Flask, request, jsonify
from database.models import BGnbdPredictions, GammaPredictions, db
from modeling.bgnbd import BGnbd
from modeling.gammagamma import GammaGamma
from visualization.plot_utils import plot_frequency_recency_matrix

app = Flask(__name__)
app.config.from_pyfile('config.py')

# initialize database
db.init_app(app)


@app.route('/')
def home():
    return "Welcome to CLV API!"


@app.route('/predict_bgf_clv', methods=['POST'])
def predict_bgf_clv():
    data = request.json
    customer_id = data['customer_id']
    model = BGnbd(app.config['DATABASE_URI'])
    model.fit()
    clv_pred = model.predict()
    return jsonify({'clv': clv_pred})


@app.route('/predict_ggf_clv', methods=['POST'])
def predict_ggf_clv():
    data = request.json
    customer_id = data['customer_id']
    model = GammaGamma(app.config['DATABASE_URI'])
    model.fit()
    clv_pred = model.predict()
    return jsonify({'clv': clv_pred})


@app.route('/plot_frequency_recency_matrix', methods=['POST'])
def plot_transactions():
    data = request.json
    customer_id = data['customer_id']
    transactions = data['transactions']
    plot_frequency_recency_matrix(customer_id, transactions)
    return "Customer transactions plotted!"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
