import numpy as np
from scipy.stats import norm
from typing import Dict


class BlackScholesGreeks:
    """Vectorized Black-Scholes pricing and Greeks calculator."""

    @staticmethod
    def calculate_greeks(
        S: float, K: float, t: float, r: float, sigma: float, option_type: str = 'CE'
    ) -> Dict[str, float]:
        """
        S: Underlying price
        K: Strike price
        t: Time to expiration in years (e.g., days / 365.0)
        r: Risk-free interest rate (decimal, e.g., 0.07)
        sigma: Implied Volatility (decimal, e.g., 0.15)
        """
        if t <= 0.0001:  # Expiry boundary protection
            intrinsic = max(0.0, S - K) if option_type == 'CE' else max(0.0, K - S)
            return {
                "price": intrinsic,
                "delta": 1.0 if (option_type == 'CE' and S > K) else 0.0,
                "gamma": 0.0,
                "theta": 0.0,
                "vega": 0.0
            }

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)

        pdf_d1 = norm.pdf(d1)

        if option_type == 'CE':
            price = S * norm.cdf(d1) - K * np.exp(-r * t) * norm.cdf(d2)
            delta = norm.cdf(d1)
        else:
            price = K * np.exp(-r * t) * norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = -norm.cdf(-d1)

        gamma = pdf_d1 / (S * sigma * np.sqrt(t))
        vega = (S * np.sqrt(t) * pdf_d1) / 100.0  # Normalized for 1% IV shift

        # Daily theta decay
        theta_call = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(t)) - r * K * np.exp(-r * t) * norm.cdf(d2)) / 365.0
        theta_put = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(t)) + r * K * np.exp(-r * t) * norm.cdf(-d2)) / 365.0
        theta = theta_call if option_type == 'CE' else theta_put

        return {
            "price": float(price),
            "delta": float(delta),
            "gamma": float(gamma),
            "theta": float(theta),
            "vega": float(vega)
        }

    @classmethod
    def implied_volatility(
        cls, target_price: float, S: float, K: float, t: float, r: float, option_type: str, max_iter: int = 100
    ) -> float:
        """Calculates Implied Volatility via Newton-Raphson method."""
        sigma = 0.20  # Initial guess (20% IV)
        tol = 1e-4

        for _ in range(max_iter):
            metrics = cls.calculate_greeks(S, K, t, r, sigma, option_type)
            diff = metrics["price"] - target_price
            vega = metrics["vega"] * 100.0

            if abs(diff) < tol:
                return sigma
            if abs(vega) < 1e-6:
                break

            sigma -= diff / vega

        return float(sigma)