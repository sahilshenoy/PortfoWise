from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an SQLite database
import os

db_path = '/tmp/portfolio_data.db'
engine = create_engine(f'sqlite:///{db_path}')


# Define the table structure
Base = declarative_base()

class Portfolio(Base):
    __tablename__ = 'portfolio'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)

class HistoricalPrice(Base):
    __tablename__ = 'historical_prices'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    date = Column(String)
    price = Column(Float)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Update save_portfolio_data
def save_portfolio_data(symbol, quantity, average_price):
    portfolio_entry = Portfolio(symbol=symbol, quantity=quantity, average_price=average_price)
    session.add(portfolio_entry)
    session.commit()

def save_historical_data(symbol, hist_data):
    for data in hist_data:
        historical_entry = HistoricalPrice(symbol=symbol, date=data['date'], price=data['price'])
        session.add(historical_entry)
    session.commit()

def save_historical_data(symbol, hist_data):
    for data in hist_data:
        historical_entry = HistoricalPrice(symbol=symbol, date=data['date'], price=data['price'])
        session.add(historical_entry)
    session.commit()
