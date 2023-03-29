import logging
from sqlalchemy.orm import load_only
from database.database_utils import Database, Fact, GammaPredictions
from lifetimes import GammaGammaFitter

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class GammaGamma:
    def __init__(self, db_url):
        self.db = Database(db_url)

    def fit(self):
        # Get the monetary value per transaction for each customer
        logging.info('Calculating monetary value per transaction')
        query = self.db.session.query(Fact.customer_id,
                                       Fact.price / Fact.weight).options(load_only("customer_id")).all()
        data = {c_id: value for c_id, value in query}

        # Fit the model
        logging.info('Fitting Gamma-Gamma model')
        self.model = GammaGammaFitter(penalizer_coef=0)
        self.model.fit(list(data.values()), list(data.keys()))

    def predict(self):
        # Get all customer IDs
        logging.info('Getting all customer IDs')
        customer_ids = [c.customer_id for c in self.db.session.query(Fact.customer_id).distinct()]

        # Make predictions for each customer
        logging.info('Making predictions')
        for c_id in customer_ids:
            # Get the historical data for the customer
            logging.info(f'Getting historical data for customer {c_id}')
            data = self.db.session.query(Fact).filter_by(customer_id=c_id).all()
            if not data:
                logging.warning(f'No historical data found for customer {c_id}')
                continue

            # Calculate the expected average lifetime value
            logging.info(f'Calculating expected average lifetime value for customer {c_id}')
            avg_ltv = self.model.conditional_expected_average_profit(data['frequency'], data['monetary_value'])
            if avg_ltv < 0:
                logging.warning(f'Negative expected average lifetime value for customer {c_id}')

            # Save the prediction to the database
            logging.info(f'Saving prediction for customer {c_id}')
            self.db.add_gamma_prediction(c_id, avg_ltv)

