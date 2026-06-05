from src.db import PROJECT_ROOT, execute_sql_file


def run_pipeline() -> None:
    execute_sql_file(PROJECT_ROOT / "sql" / "02_mart_schema.sql")
    print("Analytics mart tables rebuilt.")


if __name__ == "__main__":
    run_pipeline()

