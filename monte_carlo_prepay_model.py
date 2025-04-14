import numpy as np
import pandas as pd
from scipy.stats import norm, lognorm
from numpy.random import default_rng

class MonteCarloPrepaymentModel:
    def __init__(self, pool_size=5e9, coupon_rate=0.04, vol=0.15, kappa=0.3, theta=0.05):
        self.pool_size = pool_size
        self.coupon_rate = coupon_rate
        self.vol = vol  # Volatility of prepayment speeds
        self.kappa = kappa  # Mean reversion speed
        self.theta = theta  # Long-term mean CPR
        
    def simulate_rates(self, n_sims=1000, periods=120):
        """Simulate future rate paths using Vasicek model"""
        rng = default_rng()
        dt = 1/12
        rates = np.zeros((n_sims, periods))
        rates[:,0] = self.coupon_rate
        
        for t in range(1, periods):
            dw = rng.normal(0, np.sqrt(dt), size=n_sims)
            rates[:,t] = rates[:,t-1] + self.kappa*(self.theta-rates[:,t-1])*dt + self.vol*dw
        
        return rates
    
    def stochastic_prepayment(self, market_rates):
        """Generate prepayment CPR with random component"""
        ri = (self.coupon_rate / market_rates) - 1
        log_cpr = np.log(0.05) + 0.5*ri + self.vol*norm.ppf(np.random.random())
        return np.minimum(np.exp(log_cpr), 0.6)
    
    def run_simulation(self, n_sims=1000):
        rate_paths = self.simulate_rates(n_sims)
        results = []
        
        for path in rate_paths:
            balance = self.pool_size
            monthly_rate = self.coupon_rate / 12
            prepaid_total = 0
            
            for t in range(120):
                if balance <= 0:
                    break
                    
                # Stochastic prepayment
                cpr = self.stochastic_prepayment(path[t])
                smm = 1 - (1 - cpr)**(1/12)
                
                # Cashflow calculations
                payment = balance * monthly_rate / (1 - (1 + monthly_rate)**(-120 + t))
                prepayment = balance * smm
                interest = balance * monthly_rate
                principal = payment - interest + prepayment
                
                balance -= principal
                prepaid_total += prepayment
                
                results.append({
                    'sim_id': len(results)//120,
                    'month': t,
                    'cpr': cpr,
                    'balance': balance,
                    'prepaid': prepaid_total
                })
                
        return pd.DataFrame(results)

# Run simulation
mc_model = MonteCarloPrepaymentModel(vol=0.2)
sim_results = mc_model.run_simulation(n_sims=500)

# Analyze results
prepayment_dist = sim_results.groupby('month')['cpr'].agg(['mean', 'std', lambda x: np.percentile(x, 95)])
plt.figure(figsize=(12,6))
plt.plot(prepayment_dist['mean'], label='Mean CPR')
plt.fill_between(prepayment_dist.index, 
                 prepayment_dist['mean'] - prepayment_dist['std'],
                 prepayment_dist['mean'] + prepayment_dist['std'],
                 alpha=0.2, label='±1σ')
plt.title('Monte Carlo Prepayment Simulation Results')
plt.xlabel('Month')
plt.ylabel('Conditional Prepayment Rate (CPR)')
plt.legend()
plt.grid()
plt.show()
