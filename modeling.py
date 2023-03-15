import pandas as pd
import numpy as np
from scipy.stats import gamma, beta

class Modeling:
    def __init__(self, database):
        self.database = database
        self.data = None
        self.ggf_params = None
        self.bgnbd_params = None

    def load_data(self):
        """
        Loads the data from the database.
        """
        self.data = pd.DataFrame(self.database.get_data(), columns=['purchase_date', 'customer_id', 'product_price',
                                                                     'product_quantity', 'gender', 'location'])

    def fit_models(self):
        """
        Fits the Gamma Gamma and BG/NBD models to the data.
        """
        # Compute the expected average transaction value and the conditional variance of the transaction value
        self.data['avg_transaction_value'] = self.data['product_price'] / self.data['product_quantity']
        self.data['conditional_var'] = self.data['product_price']**2 / self.data['product_quantity']

        # Compute the mean and variance of the average transaction value for each customer
        customer_data = self.data.groupby('customer_id').agg({'avg_transaction_value': ['mean', 'var'], 'purchase_date': 'count'})
        customer_data.columns = ['_'.join(col).strip() for col in customer_data.columns.values]
        customer_data = customer_data.reset_index()

        # Fit the Gamma Gamma model to the data
        ggf_params = gamma.fit(customer_data['avg_transaction_value_mean'])
        self.ggf_params = {'mu': ggf_params[0], 'sigma': ggf_params[1]}

        # Fit the BG/NBD model to the data
        t = (self.data['purchase_date'].max() - self.data['purchase_date'].min()).days + 1
        frequency = self.data.groupby('customer_id').size()
        recency = (pd.to_datetime('now') - self.data.groupby('customer_id')['purchase_date'].max()).dt.days
        age = (self.data.groupby('customer_id')['purchase_date'].max() - self.data.groupby('customer_id')['purchase_date'].min()).dt.days
        bgnbd_params = beta.fit((frequency-1)/(age+1), recency, floc=0, fscale=t)
        self.bgnbd_params = {'r': bgnbd_params[0], 'alpha': bgnbd_params[1], 'a': bgnbd_params[2], 'b': bgnbd_params[3]}

    def predict_clv(self, customer_id, time_period):
        """
        Predicts the customer lifetime value for the specified customer and time period.
        """
        # Compute the expected average transaction value for the customer
        customer_data = self.data[self.data['customer_id'] == customer_id]
        expected_avg_transaction_value = gamma.mean(self.ggf_params['mu'], scale=self.ggf_params['sigma'])

        # Compute the conditional variance of the transaction value for the customer
        conditional_var = np.mean(customer_data['conditional_var'])

        # Compute the probability of being alive at the end of the time period
        t = (customer_data['purchase_date'].max() - customer_data['purchase_date'].min()).days + 1
        alive_prob = beta.cdf(t + time_period, self.bgnbd_params['r'] + customer_data['purchase_date'].nunique(),
                              self.bgnbd_params['alpha'], self.bgnbd_params['a'] + self.bgn)
                              