import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DB_CONFIG, DB_TABLE_NAME
from etl.extract import extract_all_cities
from etl.transform import transform_all
from logger import get_logger


logger = get_logger(__name__)


def get_engine():
    """Build a SQLAlchemy connection to PostgreSQL."""
    url = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )
    return create_engine(url)


def create_table_if_not_exists(engine):
    """Ensure the target database table exists with the correct schema.

    Executes a 'CREATE TABLE IF NOT EXISTS' statement to define the weather 
    schema, including constraints and a composite primary key. This is 
    idempotent and safe to run on every execution.

    Args:
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine used to 
            connect to the database.

    Notes:
        - Uses the table name defined in `DB_TABLE_NAME`.
        - Sets a composite Primary Key on `(city, forecast_date)` to prevent 
          duplicate daily entries per city.
    """

    sql = text(f"""
        CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
            city              VARCHAR(100)  NOT NULL,
            forecast_date     DATE          NOT NULL,
            temp_max_c        NUMERIC(5,2),
            temp_min_c        NUMERIC(5,2),
            precipitation_mm  NUMERIC(7,2),
            windspeed_max_kmh NUMERIC(6,2),
            weather_code      SMALLINT,
            ingested_at       TIMESTAMPTZ,
            PRIMARY KEY (city, forecast_date)
        );
    """)
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()
    logger.info("Table '%s' is ready.", DB_TABLE_NAME)


def load_to_postgres(df):
    """Write the clean DataFrame into PostgreSQL using an upsert pattern.

    Creates the target table if missing, uploads the data to a temporary staging 
    table, and merges it into the main table. Rows with conflicting primary keys 
    (city, forecast_date) are silently ignored to prevent duplicate entries.

    Args:
        df (pd.DataFrame): The cleaned weather DataFrame to load.

    Notes:
        - Uses a `ON CONFLICT (city, forecast_date) DO NOTHING` strategy.
        - Automatically creates and drops a suffix-based staging table 
          (e.g., `{DB_TABLE_NAME}_staging`) during the process.
    """

    engine = get_engine()
    create_table_if_not_exists(engine)

    staging = DB_TABLE_NAME + "_staging"

    with engine.connect() as conn:
        # Step 1: Write to a temporary staging table
        df.to_sql(staging, conn, if_exists="replace", index=False)
        logger.info("Wrote %d rows to staging.", len(df))

        # Step 2: Copy from staging → main table, skip duplicates
        upsert = text(f"""
            INSERT INTO {DB_TABLE_NAME}
                (city, forecast_date, temp_max_c, temp_min_c,
                 precipitation_mm, windspeed_max_kmh,
                 weather_code, ingested_at)
            SELECT city, forecast_date, temp_max_c, temp_min_c,
                   precipitation_mm, windspeed_max_kmh,
                   weather_code, ingested_at::TIMESTAMPTZ
            FROM   {staging}
            ON CONFLICT (city, forecast_date) DO NOTHING;
        """)
        result = conn.execute(upsert)
        conn.commit()
        logger.info("%d new rows inserted.", result.rowcount)

        # Step 3: Drop the staging table — we don't need it anymore
        conn.execute(text(f"DROP TABLE IF EXISTS {staging};"))
        conn.commit()


if __name__ == "__main__":

    # Step 1: Extract raw data from the API
    raw_data = extract_all_cities()

    # Step 2: Transform into a clean DataFrame
    clean_df = transform_all(raw_data)

    # Step 3: Load into PostgreSQL
    if clean_df is not None:
        load_to_postgres(clean_df)
        print("\n── Load complete! ──────────")
        print(f"Rows loaded: {len(clean_df)}")
        print("Check your PostgreSQL database to verify.")       