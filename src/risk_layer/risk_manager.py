import sys
import os

# Add project root directory to Python path for seamless VS Code execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import logging


class RiskManager:
    """
    Enforces position rules, drawdown caps, and the intraday kill switch.
    Acts as the non-negotiable safety guardrail for the options desk.
    """

    def __init__(self, initial_capital: float = 100000.0):
        self.capital = initial_capital

        # Rigid Risk Settings (₹1L Account Rules)
        self.max_per_trade_loss = 900.0   # Stop out single trade at ₹900 loss
        self.max_daily_loss = 2000.0      # Lock the entire system for the day at ₹2,000 loss
        self.max_structures = 1           # Never hold more than 1 active straddle/strangle

        # Tracking state variables
        self.daily_pnl = 0.0
        self.active_structures_count = 0
        self.trading_halted = False

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("RiskManager")

    def reset_daily_metrics(self) -> None:
        """Resets the daily counter at the start of every trading session."""
        self.daily_pnl = 0.0
        self.trading_halted = False
        self.active_structures_count = 0
        self.logger.info("Daily risk metrics reset for new session.")

    def check_entry_permission(self) -> bool:
        """
        Validates if a new structure can be legally entered.
        Returns True only if all safety conditions pass.
        """
        if self.trading_halted:
            self.logger.warning("Entry Rejected: Trading halted due to risk breaches.")
            return False

        if self.daily_pnl <= -self.max_daily_loss:
            self.trading_halted = True
            self.logger.error("Entry Rejected: Daily drawdown limit hit!")
            return False

        if self.active_structures_count >= self.max_structures:
            self.logger.warning("Entry Rejected: Max structure allocation reached.")
            return False

        return True

    def evaluate_live_structure_risk(
        self, entry_premium: float, current_premium: float, lot_size: int = 25
    ) -> bool:
        """
        Monitors active position MTM.
        Returns True if the per-trade stop-loss is breached (triggering an exit signal).
        """
        # For a SHORT position, an increase in premium = MTM loss
        structure_pnl = (entry_premium - current_premium) * lot_size

        if structure_pnl <= -self.max_per_trade_loss:
            self.logger.error(
                f"CRITICAL: Per-trade stop-loss hit! Current PnL: ₹{structure_pnl:.2f}"
            )
            return True

        return False

    def update_realized_pnl(self, trade_pnl: float) -> None:
        """
        Updates cumulative daily P&L when a trade closes.
        Triggers the global kill-switch if the daily drawdown limit is reached.
        """
        self.daily_pnl += trade_pnl
        self.logger.info(f"Updated Daily Realized PnL: ₹{self.daily_pnl:.2f}")

        if self.daily_pnl <= -self.max_daily_loss:
            self.trading_halted = True
            self.logger.critical(
                f"Daily global kill-switch activated! Total Daily Loss: ₹{self.daily_pnl:.2f}"
            )