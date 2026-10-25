import pandas as pd


def make_features(monthly: pd.DataFrame) -> pd.DataFrame:
    df = monthly.copy().sort_values("Month")
    df["Month"] = pd.to_datetime(df["Month"])

    df["month_number"] = df["Month"].dt.month
    df["year"] = df["Month"].dt.year

    df["lag_1"] = df["Revenue"].shift(1)
    df["lag_2"] = df["Revenue"].shift(2)
    df["lag_3"] = df["Revenue"].shift(3)
    df["rolling_mean_3"] = (
        df["Revenue"].shift(1).rolling(3).mean()
    )

    df["rolling_mean_6"] = (
        df["Revenue"].shift(1).rolling(6).mean()
    )

    return df.dropna().reset_index(drop=True)