import pandas as pd
import numpy as np
from scipy import optimize
from scipy.special import gammaln, hyp2f1
from typing import List


class BetaGammaFitter:
    def __init__(self, penalizer_coef=0.0):
        self.penalizer_coef = penalizer_coef

    def fit(self, frequency: List[int], recency: List[int], T: List[int]):
        """
        Fit the BG/NBD model to the data

        Args:
        - frequency (list): a list of the number of repeat purchases each customer made
        - recency (list): a list of the time between a customer's first purchase and their latest purchase
        - T (list): a list of the time between a customer's first purchase and the end of the observation period

        Returns:
        - self
        """
        assert len(frequency) == len(recency) == len(T)

        self.frequency = frequency
        self.recency = recency
        self.T = T

        penalizer_term = self.penalizer
