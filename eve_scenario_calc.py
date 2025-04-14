def calculate_eve(cashflows, discount_curve, asset_type='loan'):
    """Calculate Economic Value of Equity for a cashflow stream"""
    pv = 0
    for _, row in cashflows.iterrows():
        period = row['period']
        if asset_type == 'loan':
            cf = row['interest'] + row['scheduled_principal'] + row['prepayment']
        else:  # liability (deposit)
            cf = -row['interest']  # Negative for liabilities
        
        # Use appropriate discount rate from curve
        discount_rate = discount_curve.get(period, discount_curve[max(k for k in discount_curve.keys() if k <= period)])
        pv += cf / ((1 + discount_rate/12) ** period)
    return pv

# Define baseline and shocked discount curves
def create_curve(base_rate, shock_scenario):
    """Create yield curve under different shock scenarios"""
    tenors = [1, 12, 24, 60, 120]  # 1mo to 10y
    if shock_scenario == "parallel_up":
        return {t: base_rate + 0.02 for t in tenors}  # +200bps
    elif shock_scenario == "parallel_down":
        return {t: max(base_rate - 0.02, 0) for t in tenors}  # -200bps (floor at 0%)
    elif shock_scenario == "steepener":
        return {1: base_rate + 0.03, 12: base_rate + 0.02, 120: base_rate + 0.01}
    else:  # baseline
        return {t: base_rate for t in tenors}

# Calculate EVE under different scenarios
scenarios = ['baseline', 'parallel_up', 'parallel_down', 'steepener']
results = []

for scenario in scenarios:
    curve = create_curve(0.03, scenario)  # 3% baseline rate
    
    # Calculate asset PV (mortgages)
    asset_pv = calculate_eve(cashflows, curve, 'loan')
    
    # Simulate liability cashflows (deposits)
    # Simplified: Assume deposits have 2yr avg life with beta-adjusted rates
    deposit_cf = pd.DataFrame({
        'period': [1, 12, 24],
        'interest': [300e6 * (0.005 + beta_results['beta'].mean() * (curve[1]-0.03)) / 12,
                     300e6 * (0.005 + beta_results['beta'].mean() * (curve[12]-0.03)) / 12,
                     300e6 * (0.005 + beta_results['beta'].mean() * (curve[24]-0.03)) / 12],
        'scheduled_principal': [0, 0, 300e6],
        'prepayment': [0, 0, 0]
    })
    
    liability_pv = calculate_eve(deposit_cf, curve, 'deposit')
    
    results.append({
        'scenario': scenario,
        'eve': asset_pv + liability_pv,
        'eve_change_pct': (asset_pv + liability_pv - calculate_eve(cashflows, create_curve(0.03, 'baseline'), 'loan') - 
                          calculate_eve(deposit_cf, create_curve(0.03, 'baseline'), 'deposit')) / 5e9 * 100
    })

# Display results
eve_results = pd.DataFrame(results)
print(eve_results)

# Check capital requirements
baseline_eve = eve_results[eve_results['scenario'] == 'baseline']['eve'].values[0]
max_eve_shock = min(eve_results[eve_results['scenario'] != 'baseline']['eve'])
capital_charge = max(baseline_eve - max_eve_shock, 0) * 0.08  # 8% supervisory factor

print(f"\nBasel III Capital Charge: ${capital_charge/1e6:.2f}M")
