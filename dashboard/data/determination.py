import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def four_param_logistic(
    x: float, lower_limit: float, upper_limit: float, ic50: float, slope: float
) -> float:
    """
    Four parameter logistic function used for curve fitting.

    :param x: argument of the function (in our case: concentration)
    :param lower_limit: minimum value that the function can take
    :param upper_limit: maximum value that the function can take
    :param ic50: the x value of the inflection point
    :param slope: the steepness of the curve
    :return: value of the function for given x
    """
    return upper_limit + (lower_limit - upper_limit) / (1 + (x / ic50) ** slope)


def find_argument_four_param_logistic(
    y: float, lower_limit: float, upper_limit: float, ic50: float, slope: float
) -> float:
    """
    Four parameter logistic function used for curve fitting.

    :param y: value of the function
    :param lower_limit: minimum value that the function can take
    :param upper_limit: maximum value that the function can take
    :param ic50: the x value of the inflection point
    :param slope: the steepness of the curve
    :return: argument of the function for given y
    """
    x = ic50 * ((lower_limit - upper_limit) / (y - upper_limit) - 1) ** (1 / slope)
    if type(x) == complex:
        x = np.nan
    return x


def calculate_modulation_ic50_and_concentration_50(row: pd.Series) -> pd.Series:
    """
    Calculates modulation_ic50 and concentration_50 (concentration for modulation = 50) for given row.

    :param row: row of the dataframe
    :return: row with calculated modulation_ic50 and concentration_50
    """
    modulation_ic50 = four_param_logistic(
        row["ic50"], row["BOTTOM"], row["TOP"], row["ic50"], row["slope"]
    )
    concentration_50 = find_argument_four_param_logistic(
        50, row["BOTTOM"], row["TOP"], row["ic50"], row["slope"]
    )

    return pd.Series(
        {"modulation_ic50": modulation_ic50, "concentration_50": concentration_50}
    )


def curve_fit_for_activation(screen_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each compound, performs the curve fitting based on CONCENTRATION column
    (x axis) and VALUE column (y axis)

    :param screen_df: screening dataframe mapping EOS-CONCENTRATION pair into a value
    :return: dataframe denoting curve fit parameters for every EOS
    """
    LOWER_BOUND = -100
    valid_screen_df = screen_df[screen_df["VALUE"] >= LOWER_BOUND]
    by_eos = valid_screen_df.groupby("EOS")
    fit_props = ["lower_limit", "upper_limit", "ic50", "slope"]
    concentration_props = ["min_concentration", "max_concentration"]
    curve_fit_params = {
        key: [] for key in ["EOS", *fit_props, *concentration_props, "r2"]
    }
    for key, group in by_eos:
        by_conc = group.groupby("CONCENTRATION")
        values_avg = by_conc["VALUE"].mean()
        x = values_avg.index.to_numpy()
        y = values_avg.values
        try:
            params, _ = curve_fit(four_param_logistic, x, y, maxfev=10000)
        except RuntimeError:
            print(f"EOS: {key} - curve_fit failed")
            params = [np.nan] * 4

        curve_fit_params["EOS"].append(key)
        for i, name in enumerate(fit_props):
            curve_fit_params[name].append(params[i])

        curve_fit_params["min_concentration"].append(x.min())
        curve_fit_params["max_concentration"].append(x.max())

        y_pred = four_param_logistic(x, *params)
        residuals = y - y_pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        curve_fit_params["r2"].append(r2)

    curve_fit_df = pd.DataFrame(curve_fit_params)
    curve_fit_df["operator"] = np.where(
        curve_fit_df["ic50"] > curve_fit_df["max_concentration"],
        ">",
        np.where(curve_fit_df["ic50"] < curve_fit_df["min_concentration"], "<", "="),
    )
    return curve_fit_df.set_index("EOS")


MAX_MIN_VALUE_THRESHOLD = 75  # Keep
MIN_MAX_VALUE_THRESHOLD = 30  # Keep


def process_activation_df(
    activation_df: pd.DataFrame,
    concentration_lower_bound: float,
    concentration_upper_bound: float,
    top_lower_bound: float,
    top_upper_bound: float,
) -> pd.DataFrame:
    """
    Performs the final processing of the activation dataframe.

    :param activation_df: activation dataframe
    :param concentration_lower_bound: lower bound for concentration
    :param concentration_upper_bound: upper bound for concentration
    :param top_lower_bound: lower bound for top
    :param top_upper_bound: upper bound for top
    :return: processed activation dataframe with determined activity
    """
    activation_df["all_conc_active"] = (
        activation_df["min_value"] > MAX_MIN_VALUE_THRESHOLD
    )
    activation_df["all_conc_inactive"] = (
        activation_df["max_value"] < MIN_MAX_VALUE_THRESHOLD
    )

    activation_df["operator"] = np.where(
        activation_df.all_conc_active,
        "<",
        np.where(activation_df.all_conc_inactive, ">", activation_df.operator),
    )
    activation_df["is_reverse_dose"] = activation_df.slope < 0
    activation_df["is_active"] = (activation_df.ic50 < concentration_upper_bound) & (
        activation_df.ic50 > concentration_lower_bound
    )
    activation_df["activity_final"] = np.where(
        activation_df.operator != "=",
        "inconclusive",
        np.where(
            (activation_df.ic50 >= concentration_upper_bound)
            | (activation_df.ic50 <= concentration_lower_bound)
            | (activation_df.upper_limit <= top_lower_bound),
            "inactive",
            "active",
        ),
    )
    activation_df["is_partially_active"] = (
        (activation_df.upper_limit > top_lower_bound)
        & (activation_df.upper_limit < top_upper_bound)
        & (activation_df.ic50 < concentration_upper_bound)
        & (activation_df.ic50 > concentration_lower_bound)
    )

    cols = activation_df.columns.to_list()
    modulation_concentration = ["modulation_ic50", "concentration_50"]
    pos = cols.index("slope")
    column_order = cols[:pos] + modulation_concentration + cols[pos:]

    activation_df[modulation_concentration] = activation_df.apply(
        lambda row: calculate_modulation_ic50_and_concentration_50(row), axis=1
    )

    return activation_df[column_order]


def perform_hit_determination(
    screen_df: pd.DataFrame,
    concentration_lower_bound: float,
    concentration_upper_bound: float,
    top_lower_bound: float,
    top_upper_bound: float,
) -> pd.DataFrame:
    """
    Performs hit determination on the screening data.

    :param screen_df: screening data
    :param concentration_lower_bound: lower bound for concentration
    :param concentration_upper_bound: upper bound for concentration
    :param top_lower_bound: lower bound for top
    :param top_upper_bound: upper bound for top
    :return: hit determination data
    """
    sorted_df = screen_df.sort_values(by=["EOS", "CONCENTRATION"])
    curve_fit_df = curve_fit_for_activation(screen_df)

    aggregated_df = (
        sorted_df.groupby(["EOS", "CONCENTRATION"])
        .VALUE.mean()
        .reset_index()
        .groupby("EOS")
        .VALUE.aggregate(["max", "min", "mean"])
        .reset_index()
    )

    rename_dict = {"min": "min_value", "max": "max_value", "mean": "mean_value"}
    activation_df = aggregated_df.merge(
        curve_fit_df, how="inner", left_on="EOS", right_on="EOS"
    ).rename(columns=rename_dict)

    activation_df["TOP"] = activation_df["upper_limit"]
    activation_df["BOTTOM"] = activation_df["lower_limit"]

    return process_activation_df(
        activation_df,
        concentration_lower_bound,
        concentration_upper_bound,
        top_lower_bound,
        top_upper_bound,
    )
