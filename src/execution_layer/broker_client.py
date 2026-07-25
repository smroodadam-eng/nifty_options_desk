import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


@dataclass
class Order:
    order_id: str
    ticker: str
    action: str  # 'BUY' or 'SELL'
    quantity: int
    order_type: OrderType
    price: float
    status: OrderStatus
    timestamp: datetime


class ExecutionEngine:
    """
    Handles live and paper order execution.
    Translates strategy signals into multi-leg execution orders with safety validation.
    """

    def __init__(self, paper_trading: bool = True):
        self.paper_trading = paper_trading
        self.order_counter = 1000

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ExecutionEngine")

    def _generate_order_id(self) -> str:
        self.order_counter += 1
        return f"ORD_{self.order_counter}"

    def execute_straddle_entry(
        self,
        call_ticker: str,
        put_ticker: str,
        call_bid: float,
        put_bid: float,
        quantity: int = 25
    ) -> Dict[str, Optional[Order]]:
        """
        Executes a short straddle entry (Simultaneous SELL of ATM Call & Put).
        """
        self.logger.info(f"Initiating Short Straddle Entry for {quantity} qty...")

        if self.paper_trading:
            # Simulate immediate paper fills at bid prices
            call_order = Order(
                order_id=self._generate_order_id(),
                ticker=call_ticker,
                action="SELL",
                quantity=quantity,
                order_type=OrderType.LIMIT,
                price=call_bid,
                status=OrderStatus.FILLED,
                timestamp=datetime.now()
            )
            put_order = Order(
                order_id=self._generate_order_id(),
                ticker=put_ticker,
                action="SELL",
                quantity=quantity,
                order_type=OrderType.LIMIT,
                price=put_bid,
                status=OrderStatus.FILLED,
                timestamp=datetime.now()
            )

            self.logger.info(
                f"[PAPER FILL] Short CE: {call_ticker} @ ₹{call_bid:.2f} | Short PE: {put_ticker} @ ₹{put_bid:.2f}"
            )

            return {"call_leg": call_order, "put_leg": put_order}

        else:
            # --- LIVE BROKER API ROUTE (e.g., Zerodha Kite / Angel One / Dhan) ---
            # Example API calls for live deployment:
            # kite.place_order(variety='regular', exchange='NFO', tradingsymbol=call_ticker, transaction_type='SELL', quantity=quantity, order_type='MARKET', product='MIS')
            # kite.place_order(variety='regular', exchange='NFO', tradingsymbol=put_ticker, transaction_type='SELL', quantity=quantity, order_type='MARKET', product='MIS')
            raise NotImplementedError("Live API keys not configured. Set paper_trading=True for testing.")

    def execute_straddle_exit(
        self,
        call_ticker: str,
        put_ticker: str,
        call_ask: float,
        put_ask: float,
        quantity: int = 25
    ) -> Dict[str, Optional[Order]]:
        """
        Flattens a short straddle position (Simultaneous BUY to cover ATM Call & Put).
        """
        self.logger.info("Executing Short Straddle Exit / Square-Off...")

        if self.paper_trading:
            call_order = Order(
                order_id=self._generate_order_id(),
                ticker=call_ticker,
                action="BUY",
                quantity=quantity,
                order_type=OrderType.LIMIT,
                price=call_ask,
                status=OrderStatus.FILLED,
                timestamp=datetime.now()
            )
            put_order = Order(
                order_id=self._generate_order_id(),
                ticker=put_ticker,
                action="BUY",
                quantity=quantity,
                order_type=OrderType.LIMIT,
                price=put_ask,
                status=OrderStatus.FILLED,
                timestamp=datetime.now()
            )

            self.logger.info(
                f"[PAPER FILL] Cover CE: {call_ticker} @ ₹{call_ask:.2f} | Cover PE: {put_ticker} @ ₹{put_ask:.2f}"
            )

            return {"call_leg": call_order, "put_leg": put_order}
        else:
            raise NotImplementedError("Live API keys not configured. Set paper_trading=True for testing.")