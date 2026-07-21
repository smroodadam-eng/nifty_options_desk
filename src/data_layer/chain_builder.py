from datetime import datetime
from typing import Dict, Optional, Tuple
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.data_layer.data_loader import OptionQuote, OptionStructure

from src.data_layer.data_loader import OptionQuote, OptionStructure


class ChainBuilder:
    """Constructs dynamic option chains and identifies ATM/OTM structures."""

    def __init__(self, strike_step: float = 50.0):
        self.strike_step = strike_step

    def get_atm_strike(self, underlying_price: float) -> float:
        """Finds the closest NIFTY strike price (multiples of 50)."""
        return round(underlying_price / self.strike_step) * self.strike_step

    def build_straddle_structure(
        self,
        timestamp: datetime,
        underlying_price: float,
        chain_snapshot: pd.DataFrame,
        max_allowed_spread: float = 5.0
    ) -> Optional[OptionStructure]:
        """
        Extracts ATM Call and Put options for a given timestamp,
        validating bid-ask spreads and liquidity.
        """
        atm_strike = self.get_atm_strike(underlying_price)
        
        # Filter for ATM CE and PE
        ce_df = chain_snapshot[(chain_snapshot['strike'] == atm_strike) & (chain_snapshot['option_type'] == 'CE')]
        pe_df = chain_snapshot[(chain_snapshot['strike'] == atm_strike) & (chain_snapshot['option_type'] == 'PE')]

        if ce_df.empty or pe_df.empty:
            return None

        ce_row = ce_df.iloc[0]
        pe_row = pe_df.iloc[0]

        # Bid-ask sanity checks
        ce_spread = ce_row['ask'] - ce_row['bid']
        pe_spread = pe_row['ask'] - pe_row['bid']

        if ce_spread > max_allowed_spread or pe_spread > max_allowed_spread:
            return None  # Rejects wide, illiquid quotes

        call_leg = OptionQuote(
            timestamp=timestamp, ticker=ce_row['ticker'], strike=atm_strike,
            option_type='CE', expiry=ce_row['expiry'], ltp=ce_row['ltp'],
            bid=ce_row['bid'], ask=ce_row['ask'], volume=ce_row['volume'],
            open_interest=ce_row.get('open_interest', 0)
        )

        put_leg = OptionQuote(
            timestamp=timestamp, ticker=pe_row['ticker'], strike=atm_strike,
            option_type='PE', expiry=pe_row['expiry'], ltp=pe_row['ltp'],
            bid=pe_row['bid'], ask=pe_row['ask'], volume=pe_row['volume'],
            open_interest=pe_row.get('open_interest', 0)
        )

        return OptionStructure(
            timestamp=timestamp,
            underlying_price=underlying_price,
            call_leg=call_leg,
            put_leg=put_leg
        )