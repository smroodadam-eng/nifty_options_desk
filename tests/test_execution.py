import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.execution_layer.broker_client import ExecutionEngine, OrderStatus


def test_execution_engine():
    print("Testing Execution Engine (Paper Trading Mode)...")
    executor = ExecutionEngine(paper_trading=True)

    # 1. Test Entry Fill
    entry_orders = executor.execute_straddle_entry(
        call_ticker="NIFTY26CE24350",
        put_ticker="NIFTY26PE24350",
        call_bid=120.0,
        put_bid=115.0,
        quantity=25
    )

    assert entry_orders["call_leg"].status == OrderStatus.FILLED
    assert entry_orders["put_leg"].status == OrderStatus.FILLED
    assert entry_orders["call_leg"].price == 120.0

    # 2. Test Exit Fill
    exit_orders = executor.execute_straddle_exit(
        call_ticker="NIFTY26CE24350",
        put_ticker="NIFTY26PE24350",
        call_ask=100.0,
        put_ask=95.0,
        quantity=25
    )

    assert exit_orders["call_leg"].status == OrderStatus.FILLED
    assert exit_orders["put_leg"].action == "BUY"

    print("✓ Execution Layer Paper Test Passed!")


if __name__ == "__main__":
    test_execution_engine()