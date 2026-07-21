import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from datetime import datetime, time
from typing import Optional, Dict
import pandas as pd

from src.data_layer.data_loader import OptionStructure, FuturesBar
from src.analytics_layer.greeks import BlackScholesGreeks
from src.analytics_layer.volatility import VolatilityEngine


class ShortVolStrategy:
    """
    Intraday Short Volatility Strategy Engine.
    Trades NIFTY ATM Straddles when IV > Realized Vol and market is consolidated.
    """

    def __init__(
        self,
        min_iv_rv_spread: float = 0.02,   # Minimum 2% IV premium over Realized Vol
        max_allowed_spread: float = 5.0,  # Max allowed bid-ask spread
        start_time: time = time(10, 0),    # No trades before 10:00 AM
        cutoff_time: time = time(14, 30), # No fresh entries after 2:30 PM
        flatten_time: time = time(14, 45) # Force close by 2:45 PM
    ):
        self.min_iv_rv_spread = min_iv_rv_spread
        self.max_allowed_spread = max_allowed_spread
        self.start_time = start_time
        self.cutoff_time = cutoff_time
        self.flatten_time = flatten_time

    def evaluate_entry(
        self,
        current_time: time,
        structure: OptionStructure,
        futures_history: pd.Series,
        current_iv: float
    ) -> bool:
        """
        Evaluates all core strategy conditions for entering a Short Straddle.
        """
        # 1. Time Filters
        if current_time < self.start_time or current_time > self.cutoff_time:
            return False

        # 2. Bid-Ask Spread Check
        if structure.bid_ask_spread_cost > self.max_allowed_spread:
            return False

        # 3. Volatility Premium Check (IV vs Realized Volatility)
        realized_vol = VolatilityEngine.calculate_realized_volatility(futures_history, window_minutes=30)
        vrp_spread = VolatilityEngine.calculate_iv_rv_spread(current_iv, realized_vol)

        if vrp_spread < self.min_iv_rv_spread:
            return False

        return True

    def check_time_exit(self, current_time: time) -> bool:
        """Checks if mandatory intraday end-of-day flattening time is reached."""
        return current_time >= self.flatten_time