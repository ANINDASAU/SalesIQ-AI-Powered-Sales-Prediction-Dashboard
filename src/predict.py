"""Recursive monthly sales forecasting with a scikit-learn regressor."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from src.features import make_features
from src.train_model import FEATURES


def forecast_sales(monthly: pd.DataFrame, horizon: int = 6) -> tuple[pd.DataFrame, dict[str, float | str]]:
	"""Forecast future revenue recursively and report chronological holdout MAE."""
	if horizon < 1 or horizon > 24:
		raise ValueError("Forecast horizon must be between 1 and 24 months.")

	history = monthly[["Month", "Revenue"]].copy()
	history["Month"] = pd.to_datetime(history["Month"])
	history["Revenue"] = pd.to_numeric(history["Revenue"], errors="coerce")
	history = history.dropna().groupby("Month", as_index=False)["Revenue"].sum()
	history = history.sort_values("Month").reset_index(drop=True)
	if len(history) < 4:
		raise ValueError("At least four months of sales history are required.")

	features = make_features(history)
	metrics: dict[str, float | str] = {"mae": float("nan"), "model": "Random forest"}
	model = RandomForestRegressor(
		n_estimators=300,
		max_depth=8,
		min_samples_leaf=1,
		random_state=42,
	)

	if len(features) >= 6:
		test_size = max(1, min(3, len(features) // 5))
		split = len(features) - test_size
		evaluation_model = RandomForestRegressor(
			n_estimators=200,
			max_depth=8,
			min_samples_leaf=1,
			random_state=42,
		)
		evaluation_model.fit(features.iloc[:split][FEATURES], features.iloc[:split]["Revenue"])
		evaluation_prediction = evaluation_model.predict(features.iloc[split:][FEATURES])
		metrics["mae"] = float(mean_absolute_error(features.iloc[split:]["Revenue"], evaluation_prediction))
		model.fit(features[FEATURES], features["Revenue"])
	else:
		metrics["model"] = "Short-history trend baseline"

	values = history["Revenue"].astype(float).tolist()
	last_month = history["Month"].max()
	future_rows: list[dict[str, object]] = []

	for step in range(1, horizon + 1):
		month = last_month + pd.offsets.MonthBegin(step)
		recent = values[-3:]
		if len(features) >= 6:
			row = pd.DataFrame([{
				"month_number": month.month,
				"year": month.year,
				"lag_1": values[-1],
				"lag_2": values[-2],
				"lag_3": values[-3],
				"rolling_mean_3": sum(recent) / len(recent),
			}])
			prediction = float(model.predict(row[FEATURES])[0])
		else:
			trend = (values[-1] - values[0]) / max(len(values) - 1, 1)
			prediction = values[-1] + trend * 0.35

		prediction = max(0.0, prediction)
		values.append(prediction)
		future_rows.append({"Month": month, "Revenue": prediction})

	return pd.DataFrame(future_rows), metrics
