import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.risk_layer.risk_manager import RiskManager


def test_risk_manager_logic():
    print("Testing Risk Manager Guardrails...")
    rm = RiskManager(initial_capital=100000.0)

    # 1. Entry allowed when fresh
    assert rm.check_entry_permission() is True

    # 2. Check per-trade stop-loss evaluation
    # Entry combined premium = 230.0, Current combined premium = 270.0 (40 pt loss * 25 lot size = ₹1000 loss)
    is_stop_hit = rm.evaluate_live_structure_risk(entry_premium=230.0, current_premium=270.0, lot_size=25)
    assert is_stop_hit is True

    # 3. Simulate two losing trades hitting the daily loss cap
    rm.update_realized_pnl(-1000.0)
    assert rm.check_entry_permission() is True  # Still allowed (loss is ₹1000 < ₹2000 cap)

    rm.update_realized_pnl(-1100.0)  # Total loss now ₹2100 (> ₹2000 cap)
    assert rm.check_entry_permission() is False  # Must be BLOCKED

    print("✓ Risk Manager Verification Tests Passed!")


if __name__ == "__main__":
    test_risk_manager_logic()