
# IRRBB Modeling – Financial & Mathematical Prerequisites (Python Script)

# Time Value of Money (TVM)
def present_value(fv, r, n):
    return fv / (1 + r) ** n

print("PV Example:", present_value(1000, 0.05, 3))  # Output: ~863.84

# Bootstrapping Example
from scipy.optimize import fsolve

def bootstrap_2y(r2):
    return 5 / (1 + 0.02) + 105 / ((1 + r2) ** 2) - 102

r2 = fsolve(bootstrap_2y, 0.03)[0]
print("Bootstrapped 2Y Rate (%):", round(r2 * 100, 2))  # ~2.96%

# Forward Rate Calculation
r1 = 0.02
r2 = 0.0296
fwd = (1 + r2)**2 / (1 + r1) - 1
print("1Y Forward Rate starting in 1Y:", round(fwd, 4))  # ~0.039

# Macaulay Duration
def macaulay_duration(coupon, face, rate, years):
    cf = [coupon] * (years - 1) + [coupon + face]
    df = [(c / (1 + rate) ** t) for t, c in enumerate(cf, start=1)]
    weighted = [t * (c / (1 + rate) ** t) for t, c in enumerate(cf, start=1)]
    return sum(weighted) / sum(df)

print("Macaulay Duration:", macaulay_duration(5, 100, 0.05, 5))  # ~4.55

# Convexity
def bond_convexity(coupon, face, rate, years):
    cf = [coupon] * (years - 1) + [coupon + face]
    convexity = sum(c * t * (t + 1) / (1 + rate) ** (t + 2)
                    for t, c in enumerate(cf, start=1))
    price = sum(c / (1 + rate) ** t for t, c in enumerate(cf, start=1))
    return convexity / price

print("Bond Convexity:", bond_convexity(5, 100, 0.05, 5))  # ~21.5

# Monte Carlo Simulation – Interest Rate Paths
import numpy as np
import matplotlib.pyplot as plt

def simulate_rates(r0, mu, sigma, T, steps, n_sim):
    dt = T / steps
    rates = np.zeros((steps + 1, n_sim))
    rates[0] = r0
    for t in range(1, steps + 1):
        z = np.random.standard_normal(n_sim)
        rates[t] = rates[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)
    return rates

sim_rates = simulate_rates(0.02, 0.001, 0.01, 1, 252, 10)
plt.plot(sim_rates)
plt.title("Simulated Rate Paths")
plt.show()

# Regression for Behavioral Modeling (NMDs)
import statsmodels.api as sm

deposits = np.array([100, 102, 105, 107, 110])
rates = np.array([1.0, 1.2, 1.5, 1.7, 2.0])
X = sm.add_constant(rates)
model = sm.OLS(deposits, X).fit()
print(model.summary())
