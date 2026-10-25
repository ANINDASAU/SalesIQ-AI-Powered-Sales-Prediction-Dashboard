import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

load_dotenv()

url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "sales_dashboard"),
    query={"connect_timeout": "5"},
)

engine = create_engine(
    url,
    pool_pre_ping=True,
)


def test_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DATABASE()")
        )
        print("Connected to database:", result.scalar())


if __name__ == "__main__":
    test_connection()