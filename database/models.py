import logging

import pandas as pd
import numpy as np
import lifetimes
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.plotting import plot_period_transactions, plot_calibration_purchases_vs_holdout_purchases

from database.db_utils import Database

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class CLVModel:
    def __init__(self, db_url):
        self.db = Database(db_url)
        self.transactions = None
        self.bgf = None
        self.ggf = None

    def load_transactions(self):
        """Load transaction data from database"""
        query = """SELECT
                       c.customer_id,
                       DATE_TRUNC('month', f.date) AS month,
                       SUM(f.price) AS sales
                   FROM fact f
                   JOIN customer c ON c.customer_id = f.customer_id
                   GROUP BY 1, 2"""
        self.transactions = pd.read_sql(query, con=self.db.engine)
        logging.info(f"{len(self.transactions)} transaction records loaded from the database")

    def fit_bgf_model(self):
        """Fit the Beta Geometric/Negative Binomial (BG/NBD) model"""
        self.bgf = BetaGeoFitter(penalizer_coef=0.0)
        self.bgf.fit(self.transactions['month'], self.transactions['frequency'], self.transactions['recency'])
        plot_period_transactions(self.bgf)
        logging.info(f"Beta Geometric/Negative Binomial (BG/NBD) model fitted")

    def fit_ggf_model(self):
        """Fit the Gamma Gamma (GG) model"""
        self.ggf = GammaGammaFitter(penalizer_coef=0.0)
        self.ggf.fit(self.transactions['frequency'], self.transactions['monetary_value'])
        plot_calibration_purchases_vs_holdout_purchases(self.ggf, self.transactions)
        logging.info(f"Gamma Gamma (GG) model fitted")

    def predict_clv(self, customer_id, months=12):
        """Predict the customer's CLV for the next n months using the fitted BG/NBD and GG models"""
        t = months
        summary = self.transactions[self.transactions['customer_id'] == customer_id]
        bgf_pred = self.bgf.predict(t, summary['frequency'], summary['recency'], summary['T'])
        ggf_pred = self.ggf.customer_lifetime_value(self.bgf,
                                                    summary['frequency'],
                                                    summary['recency'],
                                                    summary['T'],
                                                    summary['monetary_value'],
                                                    time=t,
                                                    freq='M',
                                                    discount_rate=0.01)
        clv_pred = ggf_pred * bgf_pred
        self.db.session.add(BGnbdPredictions(customer_id=customer_id, predicted_clv=bgf_pred))
        self.db.session.add(GammaPredictions(customer_id=customer_id, predicted_clv=ggf_pred))
        self.db.session.commit()
        logging.info(f"Predicted CLV for customer '{customer_id}' using BG/NBD and GG models: {clv_pred:.2f}")
        return clv_pred
