class IntegratedIRRBBModel:
    def __init__(self):
        self.curves = {}  # Stores multiple curve scenarios
        self.mc_prepay = None
        self.beta_estimates = None
        
    def build_curve_scenarios(self, base_params, shock_scenarios):
        """Generate shocked curves using NSS parameters"""
        for name, shock in shock_scenarios.items():
            shocked_params = base_params.copy()
            shocked_params[:4] += shock  # Apply shock to betas
            self.curves[name] = lambda t: nss_curve(t, *shocked_params)
    
    def monte_carlo_eve(self, n_sims=1000):
        """Run full integrated simulation"""
        # 1. Simulate prepayment paths
        prepay_sims = MonteCarloPrepaymentModel().run_simulation(n_sims)
        
        # 2. Calculate EVE for each path under each curve scenario
        results = []
        for scenario, curve_func in self.curves.items():
            for sim_id in prepay_sims['sim_id'].unique():
                sim_data = prepay_sims[prepay_sims['sim_id'] == sim_id]
                pv_assets = 0
                pv_liabilities = 0
                
                # Asset valuation (mortgages)
                for _, row in sim_data.iterrows():
                    t = row['month'] / 12  # Convert to years
                    rate = curve_func(t)
                    cf = row['prepaid'] if row['month'] > 0 else 0
                    pv_assets += cf / (1 + rate)**t
                
                # Liability valuation (simplified deposits)
                deposit_cf = 3e9 * (0.005 + 0.3*(curve_func(2) - 0.03))  # 2yr maturity
                pv_liabilities = deposit_cf / (1 + curve_func(2))**2
                
                results.append({
                    'scenario': scenario,
                    'sim_id': sim_id,
                    'eve': pv_assets - pv_liabilities
                })
        
        return pd.DataFrame(results)

# Example usage
base_params = calibrate_nss(maturities, observed_rates)
shocks = {
    'baseline': [0, 0, 0, 0],
    'parallel_up': [0.02, 0, 0, 0],
    'parallel_down': [-0.02, 0, 0, 0],
    'steepener': [0, 0.01, -0.005, 0]
}

model = IntegratedIRRBBModel()
model.build_curve_scenarios(base_params, shocks)
eve_sims = model.monte_carlo_eve(n_sims=500)

# Analyze results
risk_metrics = eve_sims.groupby('scenario')['eve'].agg(['mean', 'std', 'min'])
print(risk_metrics)

# Visualize EVE distributions
import seaborn as sns
plt.figure(figsize=(12,6))
sns.boxplot(x='scenario', y='eve', data=eve_sims)
plt.title('EVE Distribution Across Scenarios')
plt.ylabel('Economic Value of Equity ($)')
plt.xlabel('Rate Scenario')
plt.grid()
plt.show()
