# Pricing-Asian-Option  

## Description
This is a Python program that prices an Asian option using Monte Carlo approach. Asian option is a financial derivative instrument whose payoff depends on the average price of the 
underlying instrument over a predetermined period of time. As with the plain vanilla options, Asian options give the holder the right but not the obligation to its owner to exercise it. There are 
several types of Asian options and averaging used for them. In this program, however, the Fixed Strike Asian option with arithmetic averaging is taken into consideration.


## Formulas Used  

### Asian Call Option
$$
C(T) = \max{(A(0,T) - K, 0)}
$$

### Asian Put Option
$$
P(T) = \max{(K - A(0,T), 0)}
$$

where:
- **A(0, T)** is the average price of the underlying instrument over the period from t = 0 to t = T
- **K** is the strike price  

The program relies on Monte Carlo simulations of stock price paths to estimate the average price of the underlying in the predetermined period of time. The price paths are simulated 
based on the **Geometric Brownian Motion (GBM)**. The GBM is a stochastic process which is often applied to stocks' prices. It assumes log-normal distribution of stock returns, 
constant drift ($\mu$), constant volatility ($\sigma$), and a memoryless path, meaning that the future price depends only on the information known now.  

### Risk-Neutral Valuation

Under the risk-neutral measure $\mathbb{Q}$, the underlying price process follows:  

$$
dS_{t} = (r-q)S_{t}dt + \sigma S_{t} dW_{t}
$$

where:
- **r** is the risk-free rate
- **q** is the dividend yield
- **$\sigma$** is annualized volatility of the underlying estimated as the implied volatility of the corresponding ATM plain vanilla option
- **$dW_{t}$** is standard Brownian motion

The discretized analytical solution of this stochastic differential equation used in the program is:  

$$
\log S_{t+\Delta t} = \log S_t + \left(r - q - \tfrac{1}{2}\sigma^2\right)\Delta t + \sigma \sqrt{\Delta t}\ Z
$$

where:
- $\Delta t = \frac{T}{N}$
- $N = \max(1, T*252)$
- $Z \sim \mathcal{N}(0,1)$

The Asin option price is estimated as the discounted expected payoff:  

$$
V_{0} = e^{-rT}\mathbb{E_{Q}}[Payoff]
$$  

## Monte Carlo Simulation

1. Extract the latest underlying price $S_{0}$ and dividend yield q from ```yfinance```
2. Extract **ATM** implied volatility from the option chain (nearest expiry to target T, strike closest to $S_{0}$)
3. Simulate n GBM paths with time step $\Delta t$
4. Compute the arithmetic average A(0, T) for each path
5. Compute payoffs and discount by $e^{-rT}$
6. Estimate the option price as the mean discounted payoff

## Standard Error and Confidence Intervals  

The Monte Carlo estimator is:  

$$
\hat{V}_0 = \frac{1}{n}\sum_{j=1}^{n} e^{-rT}\,\text{Payoff}_j.
$$

The standard error of the Monte Carlo estimator is:  

$$
\text{SE}(\hat{V}_0) = \frac{s}{\sqrt{n}}
$$

where s is the standard deviation of discounted payoffs.

A two-sided confidence interval for the Monte Carlo price estimate is reported as:  

$$
\hat{V}_0 \pm z_{\alpha / 2} SE(\hat{V}_0) , 
$$

with:
- $z_{0.975} \approx 1.96$ for a 95% CI;
- $z_{0.995} \approx 2.576$ for a 99% CI

## Usage Instructions  

1. Install the required packages as per the below:
```bash
pip install yfinance numpy datetime
```
2. Run the program:
```bash
python asian_option_pricing.py
```
3. Once the program is initiated, the user is asked for the following inputs:
- **Input the stock ticker:** any stock ticker supported by ```yfinance``` library
- **Choose option's type (call/put):** call or put
- **Choose option's time to expiration in months:** any reasonable integer
- **Choose option's strike price:** any reasonable float value for a selected stock ticker
- **Choose risk-free rate (e.g. 3%):** any reasonable risk-free rate (e.g., 3-mo SOFR rate, OIS)
- **Input the number of stock price paths simulations as an integer:** any reasonable integer

4. After the inputs are provided, the program will output:
- Estimated price of Asian option
- Standard error of the estimatation
- 95% and 99% CI for price (MC)

## Example Session (as of 01.02.2026)

```text
INPUT:
----------------------------------------------------------------------------------------------
python asian_option_pricing.py
Input the stock ticker: AAPL
Choose option's type (call/put): call
Choose option's time to expiration in months: 6
Choose option's strike price: 270
Choose risk-free rate (e.g. 3%): 3
Input the number of stock price paths simulations as an integer: 10000
OUTPUT:
----------------------------------------------------------------------------------------------
Estimated price of Asian option is: 8.8746

Standard error of the estimatation is 0.1708

95% CI for price (MC): [8.5401, 9.2091]

99% CI for price (MC): [8.4347, 9.3145]
```

## Limitations  

- GBM dynamics (constant $\sigma, \mu$, absence of stochastic volatility)
- Volatility input uses ATM implied volatility, not a full smile/surface

## Possible Extensions
- Variance reduction techniques (antithetic variates, control variates)
- Use of a volatility surface (strike- and maturity-dependent IV)
- Additional averaging conventions (geometric average, discrete fixing schedules)
- Other exotic payoffs (digital, barrier, lookback)








