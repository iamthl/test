import logging
import os

from sqlalchemy import create_engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

# Database URL for the transaction service
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5436/transaction_db")
engine = create_engine(DATABASE_URL)

@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_db() -> None:
    try:
        logger.info("Attempting to connect to database...")
        with Session(engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
        logger.info("Database connection successful!")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise e

def main() -> None:
    logger.info("Initializing Transaction Service...")
    init_db()
    logger.info("Transaction Service database initialized.")


if __name__ == "__main__":
    main() 