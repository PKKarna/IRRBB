from scipy.optimize import curve_fit

def nss_curve(t, beta0, beta1, beta2, beta3, tau1, tau2):
    """Nelson-Siegel-Svensson model"""
    term1 = beta0
    term2 = beta1 * ((1 - np.exp(-t/tau1)) / (t/tau1)
    term3 = beta2 * (((1 - np.exp(-t/tau1)) / (t/tau1) - np.exp(-t/tau1))
    term4 = beta3 * (((1 - np.exp(-t/tau2)) / (t/tau2) - np.exp(-t/tau2))
    return term1 + term2 + term3 + term4

def calibrate_nss(maturities, observed_rates):
    """Calibrate NSS parameters to market data"""
    p0 = [0.05, -0.01, 0.01, 0.01, 1.0, 1.0]  # Initial guesses
    bounds = (
        [0, -1, -1, -1, 0.1, 0.1],
        [0.2, 1, 1, 1, 10, 10]
    )
    params, _ = curve_fit(nss_curve, maturities, observed_rates, p0=p0, bounds=bounds)
    return params

# Example market data (US Treasury yields)
maturities = np.array([1, 2, 3, 5, 7, 10, 20, 30])  # in years
observed_rates = np.array([0.05, 0.055, 0.057, 0.06, 0.062, 0.063, 0.065, 0.066])

# Calibrate and plot
params = calibrate_nss(maturities, observed_rates)
t_grid = np.linspace(0.1, 30, 100)
fitted_curve = nss_curve(t_grid, *params)

plt.figure(figsize=(10,6))
plt.plot(maturities, observed_rates*100, 'o', label='Market Yields')
plt.plot(t_grid, fitted_curve*100, label='NSS Fit')
plt.title('Nelson-Siegel-Svensson Yield Curve Fitting')
plt.xlabel('Maturity (Years)')
plt.ylabel('Yield (%)')
plt.legend()
plt.grid()
plt.show()

print(f"Calibrated Parameters:\nBeta0={params[0]:.4f}\nBeta1={params[1]:.4f}\nBeta2={params[2]:.4f}\nBeta3={params[3]:.4f}\nTau1={params[4]:.2f}\nTau2={params[5]:.2f}")
