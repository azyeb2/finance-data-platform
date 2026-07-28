from src.etl_service.pipeline import run_etl_pipeline


def main():

    print("Finance Data Platform başlıyor...")

    run_etl_pipeline()

    print("Finance Data Platform tamamlandı.")


if __name__ == "__main__":
    main()