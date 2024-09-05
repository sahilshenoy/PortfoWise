import numpy as np

# Sharpe Ratio Calculation
def calculate_sharpe_ratio(portfolio_returns, risk_free_rate=0.01):
    excess_returns = portfolio_returns.mean() - risk_free_rate
    portfolio_std = np.std(portfolio_returns)
    return excess_returns / portfolio_std

# Beta Calculation
def calculate_beta(portfolio_returns, market_returns):
    covariance = np.cov(portfolio_returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)
    return covariance / market_variance

# VaR Calculation
def calculate_var(portfolio_returns, confidence_level=0.95):
    sorted_returns = np.sort(portfolio_returns)
    index = int((1 - confidence_level) * len(sorted_returns))
    return sorted_returns[index]
