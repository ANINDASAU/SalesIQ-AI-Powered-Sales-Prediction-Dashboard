import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from src.features import make_features


FEATURES = [
    "month_number",
    "year",
    "lag_1",
    "lag_2",
    "lag_3",
    "rolling_mean_3",
]


def train(monthly: pd.DataFrame):
    df = make_features(monthly)

    if len(df) < 6:
        raise ValueError(
            "At least nine consecutive months of sales are needed to train "
            "and evaluate the forecasting model."
        )

    # Keep the latest observations out of training to measure future-like error.
    split = max(4, int(len(df) * 0.8))
    split = min(split, len(df) - 2)

    train_df = df.iloc[:split]
    test_df = df.iloc[split:]

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
    )

    model.fit(train_df[FEATURES], train_df["Revenue"])

    predictions = model.predict(test_df[FEATURES])

    metrics = {
        "mae": float(
            mean_absolute_error(test_df["Revenue"], predictions)
        ),
        "rmse": float(
            root_mean_squared_error(test_df["Revenue"], predictions)
        ),
    }

    # Train the final model on all available labeled observations
    # only after evaluating the held-out period.
    final_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
    )

    final_model.fit(df[FEATURES], df["Revenue"])

    project_root = Path(__file__).resolve().parent.parent
    model_path = project_root / "models" / "sales_model.joblib"
    model_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {"model": final_model, "features": FEATURES},
        model_path,
    )

    report_path = project_root / "reports" / "model_metrics.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    # Replace this with monthly revenue loaded from your
    # cleaned database or reporting pipeline.
    project_root = Path(__file__).resolve().parent.parent
    monthly = pd.read_csv(project_root / "data" / "processed" / "monthly_sales.csv")
    monthly["Month"] = pd.to_datetime(monthly["Month"])

    print(train(monthly))