import numpy as np
import pandas as pd


class VolatilityEngine:
    """Computes rolling realized volatility metrics and volatility spreads."""

    @staticmethod
    def calculate_realized_volatility(close_prices: pd.Series, window_minutes: int = 30) -> float:
        """
        Calculates annualized realized volatility over a rolling minute window.
        Uses 1-minute logarithmic returns scaled to trading year (375 mins/day * 252 days).
        """
        if len(close_prices) < window_minutes:
            return 0.0

        log_returns = np.log(close_prices / close_prices.shift(1)).dropna()
        recent_returns = log_returns.tail(window_minutes)

        annualization_factor = np.sqrt(375 * 252)
        realized_vol = recent_returns.std() * annualization_factor
        return float(realized_vol)

    @staticmethod
    def calculate_iv_rv_spread(implied_vol: float, realized_vol: float) -> float:
        """
        Computes the Volatility Risk Premium (VRP) proxy.
        Short-vol straddles enter when IV > Realized Vol.
        """
        return implied_vol - realized_vol