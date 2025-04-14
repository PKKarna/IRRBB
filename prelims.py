py as np
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
