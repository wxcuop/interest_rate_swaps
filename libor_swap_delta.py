import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import newton

def bootstrap_zero_curve(market_rates, maturities):
    """ Bootstraps a zero curve from market swap rates."""
    zero_rates = []
    for i, rate in enumerate(market_rates):
        if i == 0:
            zero_rates.append(rate)
        else:
            disc_sum = sum(np.exp(-zero_rates[j] * maturities[j]) for j in range(i))
            zero_rate = -np.log((1 - rate * disc_sum) / (1 + rate * maturities[i])) / maturities[i]
            zero_rates.append(zero_rate)
    return interp1d(maturities, zero_rates, kind='linear', fill_value='extrapolate')

def swap_price(fixed_rate, floating_rates, zero_curve, maturities, notional=1e6):
    """ Computes the present value of a fixed-for-floating IRS. """
    fixed_leg = sum(fixed_rate * np.exp(-zero_curve(t) * t) for t in maturities)
    float_leg = sum(r * np.exp(-zero_curve(t) * t) for r, t in zip(floating_rates, maturities))
    return notional * (float_leg - fixed_leg)

def swap_delta(fixed_rate, floating_rates, zero_curve, maturities, bump=0.0001):
    """ Computes delta sensitivities by bumping rates."""
    base_price = swap_price(fixed_rate, floating_rates, zero_curve, maturities)
    deltas = []
    for i in range(len(maturities)):
        bumped_rates = floating_rates.copy()
        bumped_rates[i] += bump
        bumped_price = swap_price(fixed_rate, bumped_rates, zero_curve, maturities)
        deltas.append((bumped_price - base_price) / bump)
    return np.array(deltas)

# Example market data
market_rates = np.array([0.02, 0.025, 0.03, 0.035, 0.04])  # Market swap rates
maturities = np.array([1, 2, 3, 4, 5])  # Swap maturities in years
fixed_rate = 0.03  # Fixed leg rate
floating_rates = np.array([0.021, 0.026, 0.031, 0.036, 0.041])  # Floating rates

# Bootstrap the zero curve
zero_curve = bootstrap_zero_curve(market_rates, maturities)

# Compute swap delta sensitivities
deltas = swap_delta(fixed_rate, floating_rates, zero_curve, maturities)
print("Swap Delta Sensitivities:", deltas)
