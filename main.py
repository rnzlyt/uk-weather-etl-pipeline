from etl.extract import extract_all_cities
from etl.transform import transform_all
from etl.load import load_to_postgres
from reports.generate_report import generate_all_reports
from logger import get_logger


logger = get_logger(__name__)


if __name__ == "__main__":
    print("\n── Step 1: Extract ───")
    raw = extract_all_cities()

    print("\n── Step 2: Transform ───")
    clean = transform_all(raw)

    print("\n── Step 3: Load ───")
    load_to_postgres(clean)

    print("\n── Step 4: Report ───")
    generate_all_reports()

    print("\n✓ Pipeline complete!")