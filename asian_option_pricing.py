import yfinance as yf
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import date, datetime

def main():
    seed = 42

    tk = get_stock_ticker()
    ticker = tk.ticker

    option_type = get_option_type()
    T = get_option_tenor()/12.0
    K = get_option_strike()
    r = get_risk_free_rate()
    q = get_div_yield(tk)

    n = int(input("Input the number of stock price paths simulations as an integer: "))

    S0 = get_stock_price(tk)
    sigma = calculate_vol(tk, T, option_type, S0)

    S_avg = stock_path(S0, sigma, T, n, r, q, seed=seed)
    price, se = price_asian(r, T, option_type, S_avg, K)

    z_95 = 1.959
    ci95 = (price - z_95*se, price + z_95*se)
    ci_low_95, ci_high_95 = ci95

    z_99 = 2.576
    ci99 = (price - z_99*se, price + z_99*se)
    ci_low_99, ci_high_99 = ci99

    print("-"*50)
    print(f"\n Estimated price of Asian option is: {price:.4f}")
    print(f"\n Standard error of the estimatation is {se:.4f}")
    print(f"\n 95% CI for price (MC): [{ci_low_95:.4f}, {ci_high_95:.4f}]")
    print(f"\n 99% CI for price (MC): [{ci_low_99:.4f}, {ci_high_99:.4f}]")
    print("-"*50)


def get_option_type() -> str:
    while True:
        t = input("Choose option's type (call/put): ").strip().lower()
        try:
            if t in ("call", "put"):
                return t
            else:
                raise ValueError
        except ValueError:
            print("Option's type should be either 'call' or 'put'.")


def get_option_tenor() -> int:
    while True:
        s = input("Choose option's time to expiration in months: ").strip()
        if "month" in s:
            s = s.replace("months", "").replace("month", "").strip()
        try:
            return int(s)
        except ValueError:
            print("Tenor should be input as an integer in months, e.g., 1/3/6/12.")


def get_option_strike() -> float:
    while True:
        try:
            return round(float(input("Choose option's strike price: ").strip()), 5)
        except ValueError:
            print("Strike's value should be numeric, e.g., 100 or 150.53.")


def get_risk_free_rate() -> float: 
    while True: 
        s = input("Choose risk-free rate (e.g. 3%): ").strip().replace(" ", "")
        try: 
            if s.endswith("%"): 
                return round(float(s.strip("%")) / 100.0, 5) 
            elif s.lower().endswith("percent"): 
                return round(float(s.replace("percent", "").strip()) / 100.0, 5) 
            x = float(s)
            return x if x <= 1 else x / 100.0
        except ValueError:
            print("Examples: 3%, 3, 0.03, 3 percent")


def get_stock_ticker() -> yf.Ticker:
    ticker = input("Input the stock ticker: ")
    tk = yf.Ticker(ticker)
    hist = tk.history(period="1d")
    if hist.empty:
        raise SystemExit(f"No data found for {ticker}")
    return tk


def get_stock_price(tk: yf.Ticker) -> float:
    latest = tk.history(period="1d")
    return round(float(latest["Close"].iloc[-1]), 5)


def get_div_yield(tk: yf.Ticker) -> float:
    q = getattr(tk, "fast_info", {}).get("dividendYield", None)
    if q is None:
        q = tk.info.get("dividendYield", 0) or 0
    return float(q or 0)/100 


def calculate_vol(tk: yf.Ticker, T, option_type, S0) -> float:
    today = date.today()
    expiries = tk.options
    if not expiries:
        raise SystemExit("Options expiry data not available")

    best_exp = None
    best_diff = float("inf")
    for exp in expiries:
        exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
        days = (exp_date - today).days
        if days <= 0:
            continue
        T_i = days / 365.0
        diff = abs(T - T_i)
        if diff < best_diff:
            best_diff = diff
            best_exp = exp
    
    if best_exp is None:
        raise SystemExit("No future expiry dates found")

    chain = tk.option_chain(best_exp)
    df = chain.calls if option_type == "call" else chain.puts
    if df.empty:
        raise SystemExit("Option chain is empty")
    
    idx = (df["strike"] - S0).abs().argmin()
    iv = float(df.loc[idx, "impliedVolatility"])  
    return iv


def stock_path(S0, sigma, T, n, r, q, seed=None):
    S0, sigma, T, n = S0, sigma, T, n
    N = max(1, int(round(T * 252 * 8)))
    dt = T/N

    rng = np.random.default_rng(seed)
    dW = rng.standard_normal(size=(N, n))

    increments = (r - q - 0.5*sigma**2)*dt + sigma * np.sqrt(dt) * dW
    logS = np.empty((N+1, n))
    logS[0, :] = np.log(S0)
    logS[1:, :] = logS[0, :] + np.cumsum(increments, axis=0)
    S = np.exp(logS)

    S_avg = S[1:, :].mean(axis=0)

    return S_avg


def price_asian(r, T, option_type, S_avg, K) -> float:
    if option_type == "call":
        payoffs = np.maximum(S_avg - K, 0.0)
    elif option_type =="put":
        payoffs = np.maximum(K - S_avg, 0.0)

    disc_payoffs = np.exp(-r * T) * payoffs
    price = disc_payoffs.mean()
    se = disc_payoffs.std(ddof=1) / np.sqrt(n)

    return price, se


if __name__ == "__main__":
    main()