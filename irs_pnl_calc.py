import numpy as np

def present_value_fixed_leg(notional, fixed_rate, discount_factors, payment_times):
    """Compute the present value of the fixed leg."""
    fixed_cash_flows = fixed_rate * notional
    pv_fixed = np.sum(fixed_cash_flows * discount_factors) + notional * discount_factors[-1]
    return pv_fixed

def present_value_floating_leg(notional, floating_rates, discount_factors, payment_times):
    """Compute the present value of the floating leg."""
    floating_cash_flows = floating_rates * notional
    pv_floating = np.sum(floating_cash_flows * discount_factors) + notional * discount_factors[-1]
    return pv_floating

def calculate_delta(notional, discount_factors, payment_times, is_receiver_fixed):
    """Compute the Delta (PV01) of the IRS. Delta is negative for receiver fixed swaps."""
    delta = -notional * payment_times * discount_factors
    delta_sum = np.sum(delta)
    return delta_sum if is_receiver_fixed else -delta_sum

def calculate_pnl(notional, fixed_rate, floating_rates, discount_factors, payment_times, previous_mtm, fwd_mark_today, fwd_mark_yesterday, is_receiver_fixed):
    """Calculate IRS PnL based on changes in MtM values, accrued interest, and Delta."""
    pv_fixed = present_value_fixed_leg(notional, fixed_rate, discount_factors, payment_times)
    pv_floating = present_value_floating_leg(notional, floating_rates, discount_factors, payment_times)
    
    mtm_today = pv_fixed - pv_floating
    mtm_change = mtm_today - previous_mtm
    
    accrued_interest = fixed_rate * notional * (payment_times[0] / 360)  # Assuming ACT/360
    
    delta = calculate_delta(notional, discount_factors, payment_times, is_receiver_fixed)
    delta_pnl = delta * (fwd_mark_today - fwd_mark_yesterday)
    
    total_pnl = mtm_change + accrued_interest + delta_pnl
    
    return {
        "PV Fixed Leg": pv_fixed,
        "PV Floating Leg": pv_floating,
        "MtM Today": mtm_today,
        "MtM Change": mtm_change,
        "Accrued Interest": accrued_interest,
        "Delta": delta,
        "Delta PnL": delta_pnl,
        "Total PnL": total_pnl
    }

# Example Usage
notional = 100_000_000  # $100M
fixed_rate = 0.03  # 3%
floating_rates = np.array([0.025, 0.026, 0.027])  # SOFR forward rates
payment_times = np.array([90, 180, 270]) / 360  # Quarterly payments

discount_factors = np.array([0.98, 0.96, 0.94])  # Discount factors from yield curve
previous_mtm = -200_000  # Yesterday's MtM value
fwd_mark_today = 0.0265  # Today's forward mark
fwd_mark_yesterday = 0.026  # Yesterday's forward mark
is_receiver_fixed = True  # True for Rec Fixed, False for Pay Fixed

pnl_result = calculate_pnl(notional, fixed_rate, floating_rates, discount_factors, payment_times, previous_mtm, fwd_mark_today, fwd_mark_yesterday, is_receiver_fixed)

for key, value in pnl_result.items():
    print(f"{key}: {value:,.2f}")
