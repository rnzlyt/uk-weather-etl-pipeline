import logging
import pandas as pd
from logger import get_logger
from etl.extract import extract_all_cities


logger = get_logger(__name__)


# Rename API field names → friendly column names
COLUMN_RENAME = {
    "time":               "forecast_date",
    "temperature_2m_max": "temp_max_c",
    "temperature_2m_min": "temp_min_c",
    "precipitation_sum":  "precipitation_mm",
    "windspeed_10m_max":  "windspeed_max_kmh",
    "weathercode":        "weather_code",
}


def transform_city(raw):
    """Clean and parse a city's raw API response into a structured pandas DataFrame.

    Converts daily forecast arrays into rows, handles column renaming, casts data 
    types, and drops rows with missing critical values (date and max temperature).

    Args:
        raw (dict): The raw API response dictionary, expected to contain a "daily" 
            key with forecast arrays and an optional "city_name" string.

    Returns:
        pd.DataFrame: A cleaned DataFrame with cast types and renamed columns. 
            Returns an empty DataFrame if no valid rows remain after dropping NaNs.
    """
    city_name = raw.get("city_name", "Unknown")

    # Step 1: Turn the "daily" dict into a DataFrame
    df = pd.DataFrame(raw["daily"])

    # Step 2: Add city name as the first column
    df.insert(0, "city", city_name)

    # Step 3: Rename columns to friendly names
    df = df.rename(columns=COLUMN_RENAME)

    # Step 4: Convert date strings → proper datetime
    df["forecast_date"] = pd.to_datetime(
        df["forecast_date"], errors="coerce"
    )

    # Step 5: Cast temperature and weather columns to numbers
    # errors="coerce" turns any bad value into NaN instead of crashing
    for col in ["temp_max_c", "temp_min_c",
                "precipitation_mm", "windspeed_max_kmh"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Step 6: Drop rows where date or max temp is missing
    df = df.dropna(subset=["forecast_date", "temp_max_c"])

    logger.info("Transformed %d rows for %s.", len(df), city_name)
    return df


def transform_all(raw_data_list):
    """Transform multiple city raw responses and combine them into a single DataFrame.

    Processes each raw dictionary via `transform_city()`, stacks the resulting 
    DataFrames vertically, and appends a UTC ingestion timestamp to the batch.

    Args:
        raw_data_list (list[dict]): A list of raw API response dictionaries 
            to be processed.

    Returns:
        pd.DataFrame: A single, unified DataFrame containing data for all cities, 
            including an 'ingested_at' column.
    """
    city_dfs = [transform_city(raw) for raw in raw_data_list]

    # Stack all city DataFrames vertically into one table
    combined = pd.concat(city_dfs, ignore_index=True)

    # Add a timestamp so we know when this batch was processed
    combined["ingested_at"] = pd.Timestamp.utcnow()

    logger.info("Combined DataFrame: %d rows.", len(combined))
    return combined


if __name__ == "__main__":

    # Step 1: Extract raw data from the API
    raw_data = extract_all_cities()

    # Step 2: Transform the raw data into a clean DataFrame
    df = transform_all(raw_data)

    # Step 3: Print results so you can see what the cleaning did
    if df is not None:
        print("\n── Clean DataFrame ───────────")
        print(df.head().to_string())

        print("\n── Column data types ───────────")
        print(df.dtypes)

        print("\n── Any missing values? ───────────")
        print(df.isnull().sum())

        print("\n── Shape (rows, columns) ───────────")
        print(df.shape)