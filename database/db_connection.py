from sqlalchemy import create_engine

DATABASE_URL = "postgresql://nikhilsinghrathaur@localhost/stat_arb"

engine = create_engine(DATABASE_URL)

print("Database connected successfully!")