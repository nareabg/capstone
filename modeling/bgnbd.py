import logging
from sqlalchemy.orm import load_only
from database.database_utils import Database, Fact, BGnbdPredictions
from lifetimes import BetaGeoFitter

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class BGnbd:
    def __init__(self, db_url):
        self.db = Database(db_url)

    def fit(self):
        # Get the recency and frequency of each customer
        logging.info('Calculating recency and frequency')
        query = self.db.session.query(Fact.customer_id,
                                       (self.db.session.query(Fact.date)
                                        .filter_by(customer_id=Fact.customer_id)
                                        .order_by(Fact.date.desc())
                                        .limit(1)
                                        .scalar() - Fact.date).label('recency'),
                                       Fact.frequency).options(load_only("customer_id")).all()
        data = [(c_id, recency.days, freq) for c_id, recency, freq in query]

        # Fit the model
        logging.info('Fitting BG/NBD model')
        self.model = BetaGeoFitter(penalizer_coef=0)
        self.model.fit(*zip(*data))

    def predict(self):
        # Get all customer IDs
        logging.info('Getting all customer IDs')
        customer_ids = [r[0] for r in self.db.session.query(Fact.customer_id).distinct().all()]

    # Predict the expected number of transactions and the conditional expected average transaction value
    logging.info('Predicting expected number of transactions and expected average transaction value')
    predictions = []
    for customer_id in customer_ids:
        expected_transactions = self.model.predict(t=1, frequency=self.db.get_customer_frequency(customer_id),
                                                    recency=self.db.get_customer_recency(customer_id),
                                                    n_periods=1)
        expected_avg_value = self.db.get_customer_avg_value(customer_id)
        predictions.append(BGnbdPredictions(customer_id=customer_id,
                                            expected_transactions=expected_transactions,
                                            expected_avg_value=expected_avg_value))

    # Save the predictions to the database
    logging.info('Saving predictions to the database')
    self.db.session.bulk_save_objects(predictions)
    self.db.session.commit()

    logging.info('Predictions saved successfully') 
