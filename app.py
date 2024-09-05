from flask import Flask, render_template, send_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from save_portfolio_to_db import Portfolio, HistoricalPrice
from fetch_portfolio import calculate_portfolio_value, calculate_portfolio_performance
from alerts import check_alerts
import io
import base64
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import render_template
from risk_assessments import calculate_sharpe_ratio, calculate_beta, calculate_var
import numpy as np
from portfolio_optimization import optimize_portfolio, portfolio_annualized_performance
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from flask import render_template, request, Flask
import plotly.express as px
from enhanced_insights import fetch_insights




app = Flask(__name__)

# SQLite database
db_path = '/tmp/portfolio_data.db'
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/')
def index():
    portfolio = session.query(Portfolio).all()
    total_value = calculate_portfolio_value()
    performance = calculate_portfolio_performance()
    alerts = check_alerts()
    return render_template('index.html', portfolio=portfolio, total_value=total_value, performance=performance, alerts=alerts)

@app.route('/history/<symbol>')
def history(symbol):
    history = session.query(HistoricalPrice).filter_by(symbol=symbol).all()
    return render_template('history.html', history=history, symbol=symbol)

@app.route('/historical_price/<symbol>')
def historical_price(symbol):
    history = session.query(HistoricalPrice).filter_by(symbol=symbol).all()
    dates = [record.date for record in history]
    prices = [record.price for record in history]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name=symbol))
    fig.update_layout(title=f'Historical Prices for {symbol}', xaxis_title='Date', yaxis_title='Price')

    graph_html = fig.to_html(full_html=False)
    return render_template('historical_price.html', graph_html=graph_html, symbol=symbol)

@app.route('/portfolio_value_over_time')
def portfolio_value_over_time():
    # Fetch all the historical price records
    history = session.query(HistoricalPrice).all()
    dates = sorted(list(set([record.date for record in history])))
    total_values = []

    for date in dates:
        total_value = 0
        # For each date, sum up the value of all stocks in the portfolio
        for record in history:
            if record.date == date:
                # Fetch the quantity from the Portfolio table
                portfolio_entry = session.query(Portfolio).filter_by(symbol=record.symbol).first()
                if portfolio_entry:
                    total_value += record.price * portfolio_entry.quantity  # Calculating total value for that date
        total_values.append(total_value)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=total_values, mode='lines', name='Portfolio Value'))
    fig.update_layout(title='Portfolio Value Over Time', xaxis_title='Date', yaxis_title='Total Value')

    graph_html = fig.to_html(full_html=False)
    return render_template('portfolio_value_over_time.html', graph_html=graph_html)


@app.route('/daily_performance')
def daily_performance():
    history = session.query(HistoricalPrice).all()
    dates = sorted(list(set([record.date for record in history])))
    daily_changes = []

    for i in range(1, len(dates)):
        previous_date = dates[i - 1]
        current_date = dates[i]

        previous_value = sum([
            record.price * session.query(Portfolio).filter_by(symbol=record.symbol).first().quantity 
            for record in history if record.date == previous_date
        ])
        current_value = sum([
            record.price * session.query(Portfolio).filter_by(symbol=record.symbol).first().quantity 
            for record in history if record.date == current_date
        ])

        daily_change = ((current_value - previous_value) / previous_value) * 100
        daily_changes.append(daily_change)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates[1:], y=daily_changes))
    fig.update_layout(title='Daily Portfolio Performance', xaxis_title='Date', yaxis_title='Daily Change (%)')

    graph_html = fig.to_html(full_html=False)
    return render_template('daily_performance.html', graph_html=graph_html)



@app.route('/risk_assessment')
def risk_assessment():
    # Example: Replace with actual portfolio data and market returns
    portfolio_returns = np.random.normal(0.001, 0.02, 1000)  # Simulated portfolio returns
    market_returns = np.random.normal(0.001, 0.02, 1000)  # Simulated market returns
    
    sharpe_ratio = calculate_sharpe_ratio(portfolio_returns)
    beta = calculate_beta(portfolio_returns, market_returns)
    var_95 = calculate_var(portfolio_returns)

    return render_template('risk_assessment.html', sharpe_ratio=sharpe_ratio, beta=beta, var_95=var_95)

from flask import Flask, render_template
from rebalance_portfolio import rebalance_portfolio


@app.route('/rebalance')
def rebalance():    
    suggestions = rebalance_portfolio()
    return render_template('rebalance.html', suggestions=suggestions)


@app.route('/efficient_frontier')
def efficient_frontier():
    mean_returns = np.random.normal(0.001, 0.02, 100)  # Replace with actual stock returns
    cov_matrix = np.random.normal(0.001, 0.02, (100, 100))  # Replace with actual covariance matrix

    optimization_result = optimize_portfolio(mean_returns, cov_matrix)

    # Plot the Efficient Frontier
    results = []
    for _ in range(1000):
        weights = np.random.random(len(mean_returns))
        weights /= np.sum(weights)
        portfolio_std, portfolio_return = portfolio_annualized_performance(weights, mean_returns, cov_matrix)
        results.append([portfolio_std, portfolio_return])

    results = np.array(results)
    plt.scatter(results[:, 0], results[:, 1], c=results[:, 1] / results[:, 0], marker='o')
    plt.title('Efficient Frontier')
    plt.xlabel('Risk (Standard Deviation)')
    plt.ylabel('Return')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

# Flask route to display insights
@app.route('/insights', methods=['POST'])
def insights():
    symbol = request.form['symbol']  # Get the stock symbol from the form input
    insights_data = fetch_insights(symbol)
    return render_template('insights.html', insights=insights_data, symbol=symbol)

@app.route('/allocation_pie_chart')
def allocation_pie_chart():
    portfolio = session.query(Portfolio).all()
    labels = [stock.symbol for stock in portfolio]
    sizes = [stock.quantity * stock.average_price for stock in portfolio]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    
    return send_file(img, mimetype='image/png')

