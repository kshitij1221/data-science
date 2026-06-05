from src.run_pipeline import run_pipeline
from src.seed_data import seed
from src.show_kpis import show_kpis
from src.validate import run_validations


def main() -> None:
    seed()
    run_pipeline()
    run_validations()
    show_kpis()


if __name__ == "__main__":
    main()

