import os, logging
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text
from config.settings import DB_TABLE_NAME, REPORTS_OUTPUT_DIR
from etl.load import get_engine


logger = logging.getLogger(__name__)

def fetch_report_data():
    """Query all historical weather data from PostgreSQL into a DataFrame.

    Retrieves core weather metrics ordered sequentially by city and date. 
    Automatically parses the date column into pandas datetime objects.

    Returns:
        pd.DataFrame: A DataFrame containing the queried columns: 
            'city', 'forecast_date', 'temp_max_c', 'precipitation_mm', 
            and 'windspeed_max_kmh'.
    """

    engine = get_engine()
    query = text(f"""
        SELECT city, forecast_date, temp_max_c,
               precipitation_mm, windspeed_max_kmh
        FROM   {DB_TABLE_NAME}
        ORDER BY city, forecast_date;
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, parse_dates=["forecast_date"])
    

def plot_avg_temperature(df):
    """Bar chart: average max temperature per city."""
    avg = (df.groupby("city")["temp_max_c"]
             .mean()
             .sort_values(ascending=False))

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(avg.index, avg.values, color="#378ADD")
    ax.bar_label(bars, fmt="%.1f°C", padding=4)
    ax.set_title("Average max temperature by city")
    ax.set_ylabel("°C")
    plt.tight_layout()

    path = os.path.join(REPORTS_OUTPUT_DIR, "temperature.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("Saved temperature chart to %s", path)


def plot_total_precipitation(df):
    """Horizontal bar chart: total rainfall per city."""
    total = (df.groupby("city")["precipitation_mm"]
               .sum()
               .sort_values(ascending=True))

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(total.index, total.values, color="#1D9E75")
    ax.bar_label(bars, fmt="%.1f mm", padding=4)
    ax.set_title("Total precipitation by city")
    ax.set_xlabel("mm")
    plt.tight_layout()

    path = os.path.join(REPORTS_OUTPUT_DIR, "precipitation.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info("Saved precipitation chart to %s", path)


def generate_all_reports():
    """Main entry point to generate and save all analytical weather reports.

    Ensures the output directory exists, pulls the latest data via 
    `fetch_report_data()`, and generates the temperature and precipitation 
    visualizations. Aborts gracefully with a warning if no data is available.

    Notes:
        - Creates the directory specified by `REPORTS_OUTPUT_DIR` if it doesn't exist.
        - Triggers both `plot_avg_temperature()` and `plot_total_precipitation()`.
    """

    os.makedirs(REPORTS_OUTPUT_DIR, exist_ok=True)

    df = fetch_report_data()

    if df.empty:
        logger.warning("No data found — run the ETL pipeline first.")
        return
    
    plot_avg_temperature(df)
    plot_total_precipitation(df)
    
    logger.info("Reports saved to %s", REPORTS_OUTPUT_DIR)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_all_reports()
