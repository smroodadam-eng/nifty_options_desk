from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


@dataclass(frozen=True)
class FuturesBar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float


@dataclass(frozen=True)
class OptionQuote:
    timestamp: datetime
    ticker: str
    strike: float
    option_type: str  # 'CE' or 'PE'
    expiry: datetime
    ltp: float
    bid: float
    ask: float
    volume: int
    open_interest: int


@dataclass
class OptionStructure:
    """Represents a combined short straddle or strangle structure."""
    timestamp: datetime
    underlying_price: float
    call_leg: OptionQuote
    put_leg: OptionQuote

    @property
    def combined_mid(self) -> float:
        call_mid = (self.call_leg.bid + self.call_leg.ask) / 2.0
        put_mid = (self.put_leg.bid + self.put_leg.ask) / 2.0
        return call_mid + put_mid

    @property
    def combined_ltp(self) -> float:
        return self.call_leg.ltp + self.put_leg.ltp

    @property
    def bid_ask_spread_cost(self) -> float:
        """Calculates combined half-spread entry penalty."""
        call_spread = self.call_leg.ask - self.call_leg.bid
        put_spread = self.put_leg.ask - self.put_leg.bid
        return (call_spread + put_spread) / 2.0


class DataLoader:
    """Handles loading and cleaning of raw minute-level OHLCV data."""
    
    @staticmethod
    def load_futures_csv(file_path: str) -> pd.DataFrame:
        """Loads and formats futures CSV data."""
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate standard intraday VWAP if not present
        if 'vwap' not in df.columns:
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3.0
            df['cum_tp_vol'] = (df['typical_price'] * df['volume']).groupby(df['timestamp'].dt.date).cumsum()
            df['cum_vol'] = df['volume'].groupby(df['timestamp'].dt.date).cumsum()
            df['vwap'] = df['cum_tp_vol'] / df['cum_vol']
            df.drop(columns=['typical_price', 'cum_tp_vol', 'cum_vol'], inplace=True)
            
        return df