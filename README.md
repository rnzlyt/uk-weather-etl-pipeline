# UK Weather ETL Pipeline

A production-style data engineering portfolio project that extracts daily
weather forecasts for five UK cities from the Open-Meteo API, cleans and
transforms the data using pandas, loads it into PostgreSQL, and orchestrates
the full workflow with Apache Airflow — running automatically every day.

---

## Pipeline Architecture

Open-Meteo API
│
▼
etl/extract.py       ← Fetch raw JSON for 5 UK cities
│
▼
etl/transform.py     ← Clean and reshape with pandas
│
▼
etl/load.py          ← Upsert into PostgreSQL
│
▼
PostgreSQL: uk_weather_daily
│
▼
reports/generate_report.py  ← Charts saved as PNG
│
Orchestrated by:
dags/weather_dag.py         ← Airflow DAG, runs daily at 07:00

---

## Cities Covered

| City       | Country          |
|------------|------------------|
| London     | England          |
| Manchester | England          |
| Edinburgh  | Scotland         |
| Cardiff    | Wales            |
| Belfast    | Northern Ireland |

---

## Technologies Used

| Tool / Library   | Purpose                                    |
|------------------|--------------------------------------------|
| Python 3.11+     | Core language                              |
| requests         | HTTP calls to Open-Meteo API               |
| pandas           | Data cleaning and transformation           |
| psycopg2         | PostgreSQL adapter                         |
| SQLAlchemy       | Engine for pandas .to_sql()                |
| python-dotenv    | Load credentials from .env                 |
| Apache Airflow   | Pipeline orchestration and scheduling      |
| matplotlib       | Chart generation for reports               |

---

## Project Structure

weather_etl_pipeline/
├── config/
│   ├── init.py
│   └── settings.py          ← All configuration in one place
├── dags/
│   └── weather_dag.py       ← Airflow DAG
├── etl/
│   ├── init.py
│   ├── extract.py           ← API calls
│   ├── transform.py         ← Data cleaning
│   └── load.py              ← Write to PostgreSQL
├── reports/
│   ├── init.py
│   └── generate_report.py   ← Summary charts
├── logs/                    ← Pipeline logs (auto-created)
├── logger.py                ← Central logging configuration
├── main.py                  ← Manual pipeline runner
├── .env                     ← Credentials (not on GitHub)
├── .gitignore
├── requirements.txt
└── README.md

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/uk-weather-etl-pipeline.git
cd uk-weather-etl-pipeline
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create the PostgreSQL database

```sql
CREATE DATABASE weather_db;
```

### 4. Configure credentials

Create a `.env` file in the project root:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather_db
DB_USER=your_username
DB_PASSWORD=your_password

### 5. Run the pipeline manually

```bash
python -m main
```

### 6. Generate reports

```bash
python -m reports.generate_report
```

Charts are saved to `reports/output/`.

---

## Data Model

Table: `uk_weather_daily`

| Column             | Type                     | Description                          |
|--------------------|--------------------------|--------------------------------------|
| city               | VARCHAR(100)             | City name (primary key component)    |
| forecast_date      | DATE                     | Forecast date (primary key component)|
| temp_max_c         | NUMERIC(5,2)             | Max temperature in °C                |
| temp_min_c         | NUMERIC(5,2)             | Min temperature in °C                |
| precipitation_mm   | NUMERIC(7,2)             | Total rainfall in mm                 |
| windspeed_max_kmh  | NUMERIC(6,2)             | Max wind speed in km/h               |
| weather_code       | SMALLINT                 | WMO weather interpretation code      |
| ingested_at        | TIMESTAMP WITH TIME ZONE | When this row was inserted           |

---

## Sample SQL Queries

```sql
-- Which city had the highest max temperature?
SELECT city, MAX(temp_max_c) AS hottest_day
FROM uk_weather_daily
GROUP BY city
ORDER BY hottest_day DESC;

-- Which cities had rain forecast?
SELECT DISTINCT city
FROM uk_weather_daily
WHERE precipitation_mm > 0;

-- Full forecast for Edinburgh
SELECT forecast_date, temp_max_c, temp_min_c, precipitation_mm
FROM uk_weather_daily
WHERE city = 'Edinburgh'
ORDER BY forecast_date;
```

---

## Key Data Engineering Concepts Demonstrated

- **ETL separation of concerns** — extract, transform, load in isolated modules
- **Upsert pattern** — daily runs never create duplicate rows
- **Environment variables** — credentials never hardcoded in source code
- **Centralised logging** — structured log output saved to daily log files
- **Docstrings and type hints** — every function fully documented
- **Apache Airflow DAG** — tasks orchestrated with XCom for inter-task communication
- **Efficient pandas** — vectorised operations throughout

---

## What I Learned

This project was built while completing the Data Engineering in Python
track on DataCamp, covering:

- Introduction to APIs in Python
- Cleaning Data in Python
- Streamlined Data Integration with pandas
- ETL and ELT in Python
- Introduction to Apache Airflow in Python
- Writing Efficient Python Code

