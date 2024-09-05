from sqlalchemy import create_engine
from save_portfolio_to_db import Base

db_path = '/tmp/portfolio_data.db'
engine = create_engine(f'sqlite:///{db_path}')

# Drop the existing table (will delete data)
Base.metadata.drop_all(engine)

# Recreate the table with the new schema
Base.metadata.create_all(engine)
