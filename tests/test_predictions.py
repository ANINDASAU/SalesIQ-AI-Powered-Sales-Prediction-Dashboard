import pandas as pd
import pytest

from src.predict import forecast_sales


def test_forecast_returns_requested_months_and_nonnegative_values():
    monthly = pd.DataFrame({
        "Month": pd.date_range("2024-01-01", periods=15, freq="MS"),
        "Revenue": [1000 + i * 100 + (i % 4) * 75 for i in range(15)],
    })
    forecast, metrics = forecast_sales(monthly, horizon=6)
    assert len(forecast) == 6
    assert forecast["Month"].iloc[0] == pd.Timestamp("2025-04-01")
    assert forecast["Revenue"].ge(0).all()
    assert metrics["model"] == "Random forest"
    assert metrics["mae"] >= 0


def test_forecast_uses_trend_baseline_for_short_history():
    monthly = pd.DataFrame({
        "Month": pd.date_range("2025-01-01", periods=5, freq="MS"),
        "Revenue": [100, 110, 120, 130, 140],
    })
    forecast, metrics = forecast_sales(monthly, horizon=3)
    assert metrics["model"] == "Short-history trend baseline"
    assert forecast["Revenue"].iloc[-1] > forecast["Revenue"].iloc[0]


def test_forecast_rejects_invalid_horizons_and_too_little_history():
    monthly = pd.DataFrame({"Month": pd.date_range("2025-01-01", periods=4, freq="MS"), "Revenue": [1, 2, 3, 4]})
    with pytest.raises(ValueError, match="between 1 and 24"):
        forecast_sales(monthly, horizon=25)
    with pytest.raises(ValueError, match="At least four months"):
        forecast_sales(monthly.iloc[:3], horizon=2)