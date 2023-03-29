import logging
import pandas as pd
import matplotlib.pyplot as plt
from modeling.bgnbd import BGnbd
from modeling.gammagamma import GammaGamma
from database.database_utils import Database, Fact, BGnbdPredictions, GammaGammaPredictions

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class PlotUtils:
    def __init__(self, db_url):
        self.db = Database(db_url)

    def plot_calibration(self, model_name):
        # Get model predictions and actual data from the database
        if model_name == 'bgnbd':
            prediction_table = BGnbdPredictions
            model_class = BGnbd
        elif model_name == 'gammagamma':
            prediction_table = GammaGammaPredictions
            model_class = GammaGamma
        else:
            raise ValueError('Invalid model name')

        logging.info('Getting actual data and model predictions from the database')
        actual_data_query = self.db.session.query(Fact.customer_id, Fact.monetary_value)
        predictions_query = (self.db.session.query(prediction_table.customer_id,
                                                    prediction_table.predicted_monetary_value)
                                 .filter_by(model_name=model_name))

        # Join the actual data and predictions tables
        data = pd.merge(actual_data_query, predictions_query, on='customer_id', how='inner')

        # Plot calibration curve
        fig, ax = plt.subplots()
        ax.plot(data['monetary_value'], data['predicted_monetary_value'], 'o', label='model predictions')
        ax.plot([0, data['monetary_value'].max()], [0, data['monetary_value'].max()], 'r--', label='perfect calibration')
        ax.set_xlabel('Actual monetary value')
        ax.set_ylabel('Predicted monetary value')
        ax.set_title(f'{model_name.upper()} calibration curve')
        ax.legend()
        plt.show()

    def plot_frequency_recency_matrix(self):
        # Get recency and frequency data from the database
        logging.info('Getting recency and frequency data from the database')
        query = self.db.session.query(Fact.customer_id,
                                       (self.db.session.query(Fact.date)
                                        .filter_by(customer_id=Fact.customer_id)
                                        .order_by(Fact.date.desc())
                                        .limit(1)
                                        .scalar() - Fact.date).label('recency'),
                                       Fact.frequency).options(load_only("customer_id")).all()
        data = pd.DataFrame([(c_id, recency.days, freq) for c_id, recency, freq in query],
                            columns=['customer_id', 'recency', 'frequency'])

        # Plot the frequency-recency matrix
        fig, ax = plt.subplots()
        ax.scatter(data['recency'], data['frequency'])
        ax.set_xlabel('Recency (days)')
        ax.set_ylabel('Frequency')
        ax.set_title('Frequency-Recency Matrix')
        plt.show()
